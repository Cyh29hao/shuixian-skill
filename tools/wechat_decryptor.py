#!/usr/bin/env python3
"""
Best-effort WeChat desktop database decryptor for create-shuixian.

This tool is adapted from common SQLCipher-based WeChat export workflows,
including ideas from the MIT-licensed `npy-skill` reference repository.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


IS_WINDOWS = sys.platform == "win32"
IS_MACOS = sys.platform == "darwin"
SQLITE_HEADER = b"SQLite format 3\x00"
PAGE_SIZE = 4096


def eprint(message: str) -> None:
    print(message, file=sys.stderr)


def require_dependency(name: str, pip_name: str | None = None) -> object:
    try:
        return __import__(name)
    except ImportError as exc:
        package = pip_name or name
        raise SystemExit(f"Missing dependency: {package}. Install it with `pip install {package}`.") from exc


def find_wechat_pid() -> int | None:
    psutil = require_dependency("psutil")
    target_names = {"wechat.exe", "wechatapp.exe"} if IS_WINDOWS else {"wechat", "微信"}

    for proc in psutil.process_iter(["pid", "name"]):
        name = (proc.info["name"] or "").lower()
        if name in target_names:
            return int(proc.info["pid"])
    return None


def default_wechat_data_dir() -> Path | None:
    candidates: list[Path]
    if IS_WINDOWS:
        candidates = [
            Path.home() / "Documents" / "WeChat Files",
            Path.home() / "AppData" / "Roaming" / "Tencent" / "WeChat",
        ]
    elif IS_MACOS:
        candidates = [
            Path.home() / "Library" / "Containers" / "com.tencent.xinWeChat" / "Data",
            Path.home() / "Library" / "Application Support" / "com.tencent.xinWeChat",
        ]
    else:
        candidates = []

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def find_account_dirs(root: Path) -> list[Path]:
    account_dirs: list[Path] = []
    if not root.exists():
        return account_dirs

    if IS_WINDOWS:
        for child in root.iterdir():
            if child.is_dir() and (child / "Msg").exists():
                account_dirs.append(child)
            elif child.is_dir() and child.name.startswith("wxid_"):
                account_dirs.append(child)
    elif IS_MACOS:
        for version_dir in root.iterdir():
            if not version_dir.is_dir():
                continue
            for account_dir in version_dir.iterdir():
                if not account_dir.is_dir():
                    continue
                if (account_dir / "Message").exists() or (account_dir / "Msg").exists():
                    account_dirs.append(account_dir)

    return account_dirs


def find_message_root(account_dir: Path) -> Path:
    for name in ("Message", "Msg", "msg"):
        candidate = account_dir / name
        if candidate.exists():
            return candidate
    return account_dir


def find_db_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    direct_names = [root / "MicroMsg.db"] + [root / f"MSG{i}.db" for i in range(20)]

    for path in direct_names:
        if path.exists():
            candidates.append(path)

    for pattern in ("**/MicroMsg.db", "**/MSG*.db", "**/msg_*.db"):
        for path in sorted(root.glob(pattern)):
            if path not in candidates:
                candidates.append(path)

    return candidates


def extract_key_windows(pid: int) -> str | None:
    require_dependency("psutil")
    pymem = require_dependency("pymem")
    require_dependency("pymem.process")

    pm = pymem.Pymem(pid)
    key_candidates: list[bytes] = []

    try:
        module = pymem.process.module_from_name(pm.process_handle, "WeChatWin.dll")
        if not module:
            eprint("Could not find WeChatWin.dll in the running process.")
            return None

        base = module.lpBaseOfDll
        size = module.SizeOfImage
        chunk_size = 0x100000
        pattern = b"iphone\x00"
        offset = 0

        while offset < size:
            to_read = min(chunk_size, size - offset)
            try:
                chunk = pm.read_bytes(base + offset, to_read)
            except Exception:
                offset += chunk_size
                continue

            search_pos = 0
            while True:
                found = chunk.find(pattern, search_pos)
                if found == -1:
                    break
                key_offset = found - 0x70
                if key_offset >= 0:
                    key_candidate = chunk[key_offset : key_offset + 32]
                    if len(key_candidate) == 32 and key_candidate != b"\x00" * 32:
                        key_candidates.append(key_candidate)
                search_pos = found + 1

            offset += chunk_size
    except Exception as exc:
        eprint(f"Memory scan failed: {exc}")

    if key_candidates:
        return key_candidates[0].hex()

    return fallback_key_windows(pm)


def fallback_key_windows(pm: object) -> str | None:
    prefixes = [bytes.fromhex("0400000020000000"), bytes.fromhex("0100000020000000")]

    try:
        import pymem.process  # type: ignore

        for module in pm.list_modules():
            if b"WeChatWin" not in module.szModule:
                continue

            base = module.lpBaseOfDll
            size = module.SizeOfImage
            chunk_size = 0x200000
            offset = 0

            while offset < size:
                to_read = min(chunk_size, size - offset)
                try:
                    chunk = pm.read_bytes(base + offset, to_read)
                except Exception:
                    offset += chunk_size
                    continue

                for prefix in prefixes:
                    search_pos = 0
                    while True:
                        found = chunk.find(prefix, search_pos)
                        if found == -1:
                            break
                        key_start = found + len(prefix)
                        key_candidate = chunk[key_start : key_start + 32]
                        if len(key_candidate) == 32 and key_candidate != b"\x00" * 32:
                            return key_candidate.hex()
                        search_pos = found + 1
                offset += chunk_size
    except Exception:
        return None

    return None


def extract_key_macos(pid: int) -> str | None:
    key = extract_key_macos_keychain()
    if key:
        return key
    return extract_key_macos_lldb(pid)


def extract_key_macos_keychain() -> str | None:
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "com.tencent.xinWeChat", "-w"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:
        return None

    key = result.stdout.strip()
    return key or None


def extract_key_macos_lldb(pid: int) -> str | None:
    try:
        result = subprocess.run(
            ["lldb", "-p", str(pid), "-o", "process interrupt", "-o", "quit"],
            capture_output=True,
            text=True,
            timeout=20,
            check=False,
        )
    except Exception:
        return None

    if result.returncode == 0:
        eprint("Automatic macOS key extraction is not fully implemented. Use `--key` if available.")
    return None


def extract_key_from_memory(pid: int) -> str | None:
    if IS_WINDOWS:
        return extract_key_windows(pid)
    if IS_MACOS:
        return extract_key_macos(pid)
    eprint("Only Windows and macOS are supported for automatic key lookup.")
    return None


def test_key(db_path: Path, key_hex: str) -> bool:
    try:
        from Crypto.Cipher import AES
        from Crypto.Hash import HMAC, SHA1
        from Crypto.Protocol.KDF import PBKDF2
    except ImportError as exc:
        raise SystemExit("Missing dependency: pycryptodome. Install it with `pip install pycryptodome`.") from exc

    key_bytes = bytes.fromhex(key_hex)
    header = db_path.read_bytes()[:PAGE_SIZE]
    if len(header) < PAGE_SIZE:
        return False

    salt = header[:16]
    key = PBKDF2(key_bytes, salt, dkLen=32, count=4000, prf=lambda p, s: HMAC.new(p, s, SHA1).digest())
    iv = header[16:32]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(header[32:48])
    return decrypted != b"\x00" * 16


def decrypt_db(db_path: Path, key_hex: str, output_path: Path) -> bool:
    try:
        from Crypto.Cipher import AES
        from Crypto.Hash import HMAC, SHA1
        from Crypto.Protocol.KDF import PBKDF2
    except ImportError as exc:
        raise SystemExit("Missing dependency: pycryptodome. Install it with `pip install pycryptodome`.") from exc

    raw = db_path.read_bytes()
    if len(raw) < PAGE_SIZE:
        eprint(f"Skipping invalid database (too small): {db_path}")
        return False

    key_bytes = bytes.fromhex(key_hex)
    salt = raw[:16]
    key = PBKDF2(key_bytes, salt, dkLen=32, count=4000, prf=lambda p, s: HMAC.new(p, s, SHA1).digest())
    output = bytearray()

    for page_num in range(len(raw) // PAGE_SIZE):
        page = raw[page_num * PAGE_SIZE : (page_num + 1) * PAGE_SIZE]
        if page_num == 0:
            iv = page[16:32]
            cipher = AES.new(key, AES.MODE_CBC, iv)
            decrypted_content = cipher.decrypt(page[32 : PAGE_SIZE - 32])
            decrypted_page = SQLITE_HEADER + decrypted_content[len(SQLITE_HEADER) :]
            output.extend(decrypted_page)
            output.extend(b"\x00" * 32)
            continue

        iv = page[-48:-32]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_content = cipher.decrypt(page[: PAGE_SIZE - 48])
        output.extend(decrypted_content)
        output.extend(b"\x00" * 48)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(output)

    import sqlite3

    try:
        conn = sqlite3.connect(str(output_path))
        conn.execute("SELECT name FROM sqlite_master LIMIT 1")
        conn.close()
        return True
    except sqlite3.DatabaseError:
        output_path.unlink(missing_ok=True)
        return False


def choose_root_from_args(db_dir_arg: str | None) -> Path:
    if db_dir_arg:
        return Path(db_dir_arg).expanduser().resolve()

    root = default_wechat_data_dir()
    if not root:
        raise SystemExit("Could not auto-detect the WeChat data directory. Pass `--db-dir` explicitly.")
    return root


def resolve_databases(root: Path) -> list[Path]:
    if root.is_file():
        return [root]

    account_dirs = find_account_dirs(root)
    if account_dirs:
        if len(account_dirs) == 1:
            root = find_message_root(account_dirs[0])
        else:
            print("Found multiple WeChat accounts:")
            for index, account_dir in enumerate(account_dirs):
                print(f"  [{index}] {account_dir.name}")
            selected = input("Choose an account index: ").strip() or "0"
            root = find_message_root(account_dirs[int(selected)])

    db_files = find_db_files(root)
    if not db_files:
        raise SystemExit(f"No WeChat database files found under: {root}")
    return db_files


def main() -> None:
    if not IS_WINDOWS and not IS_MACOS:
        raise SystemExit("This tool currently supports only Windows and macOS.")

    parser = argparse.ArgumentParser(description="Decrypt WeChat desktop databases for create-shuixian.")
    parser.add_argument("--db-dir", help="WeChat data directory, account directory, or message-db directory.")
    parser.add_argument("--db", help="Single database file to decrypt.")
    parser.add_argument("--output", default="./decrypted", help="Directory where decrypted SQLite files are written.")
    parser.add_argument("--key", help="SQLCipher key in hex. Skips automatic memory lookup.")
    parser.add_argument("--find-key-only", action="store_true", help="Print the discovered key and stop.")
    parser.add_argument("--test-db", help="Test whether a key can decrypt one database file.")
    args = parser.parse_args()

    key_hex = args.key
    if not key_hex:
        pid = find_wechat_pid()
        if not pid:
            raise SystemExit("Could not find a logged-in WeChat process. Open WeChat first or pass `--key`.")
        print(f"Found WeChat process: PID {pid}")
        key_hex = extract_key_from_memory(pid)
        if not key_hex:
            raise SystemExit(
                "Could not extract the key automatically. "
                "Try admin privileges, or use a key from PyWxDump / WeChatMsg via `--key`."
            )

    if args.find_key_only:
        print(key_hex)
        return

    if args.test_db:
        ok = test_key(Path(args.test_db).expanduser().resolve(), key_hex)
        print("Key looks valid." if ok else "Key test failed.")
        return

    if args.db:
        db_files = [Path(args.db).expanduser().resolve()]
    else:
        db_files = resolve_databases(choose_root_from_args(args.db_dir))

    output_dir = Path(args.output).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    success_count = 0
    for db_path in db_files:
        output_path = output_dir / db_path.name
        print(f"Decrypting {db_path.name} ...", end=" ", flush=True)
        if decrypt_db(db_path, key_hex, output_path):
            print("ok")
            success_count += 1
        else:
            print("failed")

    print(f"Finished: {success_count}/{len(db_files)} database files decrypted.")
    print(f"Output directory: {output_dir}")
    print("Next step:")
    print(f"  python tools/wechat_importer.py --list-contacts --db-dir \"{output_dir}\"")


if __name__ == "__main__":
    main()
