#!/usr/bin/env python3
"""
Archive source material for a generated shuixian mirror skill.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


TEXT_SUFFIXES = {".txt", ".md", ".json", ".jsonl", ".csv", ".log"}
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")


def safe_source_slug(source: str) -> str:
    """Use source labels as metadata, never as user-controlled path segments."""
    return re.sub(r"[^\w.-]+", "-", source, flags=re.UNICODE).strip(".-")[:80] or "manual-import"


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError(
            f"Input is not valid UTF-8: {path}. Keep the original, save a UTF-8 copy, and retry."
        ) from error


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
        text = read_file(file_path).rstrip()
        longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
        fence = "`" * max(3, longest + 1)
        lines.append(f"{fence}text")
        lines.append(text)
        lines.append(fence)
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

    source_paths = [Path(value).expanduser().resolve() for value in args.input]
    for source_path in source_paths:
        if not source_path.is_file():
            parser.error(f"Input must be an existing file: {source_path}")

    skill_dir = Path(args.skill_dir).expanduser().resolve()
    imports_dir = skill_dir / "knowledge" / "imports"
    images_dir = skill_dir / "knowledge" / "images"
    try:
        for destination in (imports_dir, images_dir):
            for directory in (destination, *destination.parents):
                if directory.exists() and not directory.is_dir():
                    parser.error(
                        f"Archive destination is blocked by a file: {directory}. "
                        "Choose a directory with --skill-dir and retry; no files were written."
                    )
    except OSError as error:
        parser.error(f"Cannot check archive destination {skill_dir}: {error}")
    text_files: list[Path] = []
    image_copies: list[tuple[Path, Path]] = []

    for source_path in source_paths:
        suffix = source_path.suffix.lower()
        if suffix in IMAGE_SUFFIXES:
            target_path = images_dir / f"{now_stamp()}-{source_path.name}"
            image_copies.append((source_path, target_path))
            continue

        if suffix in TEXT_SUFFIXES or source_path.is_file():
            text_files.append(source_path)

    copied_images = [target for _, target in image_copies]
    # Decode the entire batch before creating directories or copying screenshots.
    try:
        archive = render_archive(
            source=args.source,
            self_name=args.self_name,
            mirror_name=args.mirror_name,
            note=args.note,
            text_files=text_files,
            copied_images=copied_images,
        )
    except (ValueError, OSError) as error:
        parser.error(str(error))

    imports_dir.mkdir(parents=True, exist_ok=True)
    images_dir.mkdir(parents=True, exist_ok=True)
    for source_path, target_path in image_copies:
        shutil.copy2(source_path, target_path)
    archive_path = imports_dir / f"{now_stamp()}-{safe_source_slug(args.source)}.md"
    archive_path.write_text(archive, encoding="utf-8")

    print(f"Archived materials to {archive_path}")
    if copied_images:
        print(f"Copied {len(copied_images)} image file(s) to {images_dir}")


if __name__ == "__main__":
    for cli_stream in (sys.stdout, sys.stderr):
        if hasattr(cli_stream, "reconfigure"):
            cli_stream.reconfigure(encoding="utf-8")
    main()
