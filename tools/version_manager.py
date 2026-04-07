#!/usr/bin/env python3
"""
Version management for generated shuixian mirror skills.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

from skill_writer import mirror_skill_name, read_text_file, render_skill_markdown


DEFAULT_BASE_DIR = "./.agents/skills"
TRACKED_FILES = ("SKILL.md", "style.md", "mind.md", "relationship.md", "appearance.md", "meta.json")
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


def backup_current_state(skill_dir: Path, backup_name: str) -> None:
    backup_dir = skill_dir / "versions" / backup_name
    backup_dir.mkdir(parents=True, exist_ok=True)
    for filename in TRACKED_FILES:
        source = skill_dir / filename
        if source.exists():
            shutil.copy2(source, backup_dir / filename)


def rollback(skill_dir: Path, slug: str, target_version: str) -> bool:
    version_dir = skill_dir / "versions" / target_version
    if not version_dir.exists():
        print(f"Version does not exist: {target_version}", file=sys.stderr)
        return False

    meta_path = skill_dir / "meta.json"
    if not meta_path.exists():
        print(f"Missing meta.json in {skill_dir}", file=sys.stderr)
        return False

    meta = json.loads(read_text_file(meta_path))
    current_version = str(meta.get("version", "unknown"))
    backup_current_state(skill_dir, f"{current_version}-before-rollback")

    restored_files: list[str] = []
    for filename in TRACKED_FILES:
        source = version_dir / filename
        target = skill_dir / filename
        if source.exists():
            shutil.copy2(source, target)
            restored_files.append(filename)
        elif filename != "appearance.md" and target.exists():
            target.unlink()

    reloaded_meta = json.loads(read_text_file(meta_path))
    reloaded_meta["slug"] = slug
    reloaded_meta["skill_name"] = mirror_skill_name(slug)
    reloaded_meta["version"] = f"{target_version}-restored"
    reloaded_meta["updated_at"] = datetime.now(timezone.utc).isoformat()
    reloaded_meta["rollback_from"] = current_version
    meta_path.write_text(json.dumps(reloaded_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    rewrite_skill(skill_dir, slug, reloaded_meta)

    print(f"Rolled back {mirror_skill_name(slug)} to {target_version}")
    print(f"Restored files: {', '.join(restored_files)}")
    return True


def cleanup_old_versions(skill_dir: Path, max_versions: int = MAX_VERSIONS) -> None:
    versions_dir = skill_dir / "versions"
    if not versions_dir.exists():
        return

    version_dirs = sorted(
        [entry for entry in versions_dir.iterdir() if entry.is_dir()],
        key=lambda entry: entry.stat().st_mtime,
    )
    stale_dirs = version_dirs[:-max_versions] if len(version_dirs) > max_versions else []
    for stale_dir in stale_dirs:
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
    main()
