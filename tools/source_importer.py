#!/usr/bin/env python3
"""
Archive source material for a generated shuixian mirror skill.
"""

from __future__ import annotations

import argparse
import shutil
from datetime import datetime, timezone
from pathlib import Path


TEXT_SUFFIXES = {".txt", ".md", ".json", ".jsonl", ".csv", ".log"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig", errors="replace")


def render_archive(
    *,
    source: str,
    self_name: str,
    mirror_name: str,
    note: str,
    text_files: list[Path],
    copied_images: list[Path],
) -> str:
    lines = [
        "# Imported Source Material",
        "",
        f"- Source: {source}",
        f"- Self Name: {self_name or 'unspecified'}",
        f"- Mirror Name: {mirror_name or 'unspecified'}",
        f"- Note: {note or 'none'}",
        "",
    ]

    if copied_images:
        lines.append("## Copied Images")
        lines.append("")
        for image in copied_images:
            lines.append(f"- {image.as_posix()}")
        lines.append("")

    for file_path in text_files:
        lines.append(f"## File: {file_path.name}")
        lines.append("")
        lines.append("```text")
        lines.append(read_file(file_path).rstrip())
        lines.append("```")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Archive text files and screenshots for a shuixian mirror skill.")
    parser.add_argument("--input", action="append", required=True, help="Input file path. Repeat for multiple files.")
    parser.add_argument("--skill-dir", required=True, help="Generated mirror skill directory.")
    parser.add_argument("--source", default="manual-import", help="Source label for these materials.")
    parser.add_argument("--self-name", default="", help="User display name.")
    parser.add_argument("--mirror-name", default="", help="Mirror display name.")
    parser.add_argument("--note", default="", help="Optional note about this batch.")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).expanduser().resolve()
    imports_dir = skill_dir / "knowledge" / "imports"
    images_dir = skill_dir / "knowledge" / "images"
    imports_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)

    text_files: list[Path] = []
    copied_images: list[Path] = []

    for input_value in args.input:
        source_path = Path(input_value).expanduser().resolve()
        if not source_path.exists():
            raise FileNotFoundError(f"Input file does not exist: {source_path}")

        suffix = source_path.suffix.lower()
        if suffix in IMAGE_SUFFIXES:
            target_path = images_dir / f"{now_stamp()}-{source_path.name}"
            shutil.copy2(source_path, target_path)
            copied_images.append(target_path)
            continue

        if suffix in TEXT_SUFFIXES or source_path.is_file():
            text_files.append(source_path)

    archive_path = imports_dir / f"{now_stamp()}-{args.source}.md"
    archive_path.write_text(
        render_archive(
            source=args.source,
            self_name=args.self_name,
            mirror_name=args.mirror_name,
            note=args.note,
            text_files=text_files,
            copied_images=copied_images,
        ),
        encoding="utf-8",
    )

    print(f"Archived materials to {archive_path}")
    if copied_images:
        print(f"Copied {len(copied_images)} image file(s) to {images_dir}")


if __name__ == "__main__":
    main()
