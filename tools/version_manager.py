#!/usr/bin/env python3
"""
Version management for generated shuixian mirror skills.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from skill_writer import (
    REQUIRED_FILES,
    TRACKED_FILES,
    archive_current_version,
    archive_name,
    is_linked_path,
    mirror_skill_name,
    parse_meta_json,
    read_text_file,
    render_skill_markdown,
    write_skill_files,
)


DEFAULT_BASE_DIR = "./.agents/skills"
MAX_VERSIONS = 10


def archived_at(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def load_section(path: Path) -> str:
    if not path.exists():
        return ""
    return read_text_file(path)


def list_versions(skill_dir: Path) -> list[dict[str, str]]:
    versions_dir = skill_dir / "versions"
    if not versions_dir.exists():
        return []

    results: list[dict[str, str]] = []
    for entry in sorted(versions_dir.iterdir(), key=lambda item: item.stat().st_mtime):
        if not entry.is_dir():
            continue
        results.append(
            {
                "version": entry.name,
                "archived_at": archived_at(entry),
                "files": ", ".join(sorted(file.name for file in entry.iterdir() if file.is_file())),
            }
        )
    return results


def rewrite_skill(skill_dir: Path, slug: str, meta: dict) -> None:
    skill_dir.joinpath("SKILL.md").write_text(
        render_skill_markdown(
            slug=slug,
            meta=meta,
            style_content=load_section(skill_dir / "style.md"),
            mind_content=load_section(skill_dir / "mind.md"),
            relationship_content=load_section(skill_dir / "relationship.md"),
            appearance_content=load_section(skill_dir / "appearance.md"),
        ),
        encoding="utf-8",
    )


def backup_current_state(skill_dir: Path, backup_name: str) -> Path:
    return archive_current_version(skill_dir, backup_name)


def rollback(skill_dir: Path, slug: str, target_version: str) -> bool:
    mirror_skill_name(slug)
    archive_name(target_version)
    version_dir = skill_dir / "versions" / target_version
    if is_linked_path(skill_dir) or is_linked_path(skill_dir / "versions") or is_linked_path(version_dir):
        raise ValueError("Refusing rollback through a linked directory.")
    if not version_dir.is_dir():
        print(f"Version does not exist: {target_version}", file=sys.stderr)
        return False

    meta_path = skill_dir / "meta.json"
    if not meta_path.exists():
        print(f"Missing meta.json in {skill_dir}", file=sys.stderr)
        return False

    meta = parse_meta_json(str(meta_path))
    missing = [filename for filename in REQUIRED_FILES if not (version_dir / filename).is_file()]
    if missing:
        raise ValueError(f"Archive is incomplete; live files were not changed. Missing: {', '.join(missing)}")
    if any(is_linked_path(version_dir / filename) for filename in TRACKED_FILES):
        raise ValueError("Refusing to restore linked archive files.")
    # Read and validate the whole target before touching any current files.
    sections = {filename: load_section(version_dir / filename)
                for filename in TRACKED_FILES if filename != "meta.json"}
    reloaded_meta = parse_meta_json(str(version_dir / "meta.json"))
    current_version = str(meta.get("version", "unknown"))
    backup_current_state(skill_dir, f"{current_version}-before-rollback")

    reloaded_meta["slug"] = slug
    reloaded_meta["skill_name"] = mirror_skill_name(slug)
    reloaded_meta["version"] = f"{target_version}-restored"
    reloaded_meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    reloaded_meta["rollback_from"] = current_version
    write_skill_files(
        skill_dir=skill_dir,
        slug=slug,
        meta=reloaded_meta,
        style_content=sections["style.md"],
        mind_content=sections["mind.md"],
        relationship_content=sections["relationship.md"],
        appearance_content=sections["appearance.md"],
    )

    print(f"Rolled back {mirror_skill_name(slug)} to {target_version}")
    print(f"Restored files: {', '.join(name for name in TRACKED_FILES if (version_dir / name).exists())}")
    return True


def cleanup_old_versions(skill_dir: Path, max_versions: int = MAX_VERSIONS) -> None:
    if max_versions < 1:
        raise ValueError("Keep at least one archived version.")
    versions_dir = skill_dir / "versions"
    if is_linked_path(skill_dir) or is_linked_path(versions_dir):
        raise ValueError("Refusing cleanup through a linked directory.")
    if not versions_dir.exists():
        return

    version_dirs = sorted(
        [entry for entry in versions_dir.iterdir() if entry.is_dir() and not is_linked_path(entry)],
        key=lambda entry: entry.stat().st_mtime,
    )
    stale_dirs = version_dirs[:-max_versions] if len(version_dirs) > max_versions else []
    for stale_dir in stale_dirs:
        if not stale_dir.resolve().is_relative_to(skill_dir.resolve()):
            raise ValueError(f"Archive escapes the skill directory: {stale_dir}")
        shutil.rmtree(stale_dir)
        print(f"Removed old version archive: {stale_dir.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage versions for generated shuixian mirror skills.")
    parser.add_argument("--action", required=True, choices=["list", "rollback", "cleanup"])
    parser.add_argument("--slug", required=True, help="Mirror slug.")
    parser.add_argument("--version", help="Target version for rollback.")
    parser.add_argument("--base-dir", default=DEFAULT_BASE_DIR, help="Directory where generated skills are stored.")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).expanduser().resolve()
    skill_dir = base_dir / mirror_skill_name(args.slug)
    if not skill_dir.exists():
        print(f"Skill directory does not exist: {skill_dir}", file=sys.stderr)
        sys.exit(1)

    if args.action == "list":
        versions = list_versions(skill_dir)
        if not versions:
            print(f"No archived versions for {mirror_skill_name(args.slug)}")
            return
        print(f"Archived versions for {mirror_skill_name(args.slug)}:\n")
        for version in versions:
            print(f"{version['version']}  Archived: {version['archived_at']}  Files: {version['files']}")
        return

    if args.action == "rollback":
        if not args.version:
            print("rollback requires --version", file=sys.stderr)
            sys.exit(1)
        if not rollback(skill_dir, args.slug, args.version):
            sys.exit(1)
        return

    cleanup_old_versions(skill_dir)
    print("Cleanup complete")


if __name__ == "__main__":
    for cli_stream in (sys.stdout, sys.stderr):
        if hasattr(cli_stream, "reconfigure"):
            cli_stream.reconfigure(encoding="utf-8")
    try:
        main()
    except (OSError, ValueError) as exc:
        raise SystemExit(f"Error: {exc}") from None
