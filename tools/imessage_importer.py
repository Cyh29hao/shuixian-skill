#!/usr/bin/env python3
"""
Import iMessage chat history into a normalized transcript for create-shuixian.
"""

from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from source_importer import render_archive


APPLE_EPOCH_OFFSET = 978307200


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\x00", " ").strip()


def connect(db_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(str(db_path))


def match_handles(conn: sqlite3.Connection, target: str) -> list[tuple[int, str]]:
    cursor = conn.execute(
        """
        SELECT ROWID, id
        FROM handle
        WHERE id LIKE ?
        ORDER BY ROWID ASC
        """,
        (f"%{target}%",),
    )
    return [(int(row[0]), normalize_text(row[1])) for row in cursor.fetchall()]


def ns_to_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    try:
        raw = int(value)
    except (TypeError, ValueError):
        return None

    try:
        return datetime.fromtimestamp(raw / 1_000_000_000 + APPLE_EPOCH_OFFSET)
    except (OSError, OverflowError, ValueError):
        return None


def extract_messages(db_path: Path, target: str) -> tuple[str, list[dict[str, Any]]]:
    messages: list[dict[str, Any]] = []
    with connect(db_path) as conn:
        handles = match_handles(conn, target)
        if not handles:
            raise LookupError(f"Could not find iMessage handle matching `{target}`.")

        handle_ids = [row[0] for row in handles]
        handle_display = handles[0][1]
        placeholders = ", ".join("?" for _ in handle_ids)

        cursor = conn.execute(
            f"""
            SELECT m.date, m.text, m.is_from_me, m.cache_has_attachments
            FROM message m
            WHERE m.handle_id IN ({placeholders})
            ORDER BY m.date ASC
            """,
            handle_ids,
        )

        for date_raw, text, is_from_me, has_attachments in cursor.fetchall():
            content = normalize_text(text)
            if not content and has_attachments:
                content = "[attachment]"
            if not content:
                continue

            messages.append(
                {
                    "timestamp": ns_to_datetime(date_raw),
                    "sender": "我" if is_from_me else handle_display,
                    "content": content,
                }
            )

    return handle_display, messages


def render_transcript(handle_display: str, target: str, messages: list[dict[str, Any]]) -> str:
    lines = [
        "# iMessage Transcript",
        "",
        f"- Target: {handle_display}",
        f"- Query: {target}",
        f"- Message Count: {len(messages)}",
        "",
        "## Conversation",
        "",
    ]

    for message in messages:
        timestamp = message["timestamp"].strftime("%Y-%m-%d %H:%M") if message["timestamp"] else "unknown-time"
        lines.append(f"[{timestamp}] {message['sender']}: {message['content']}")

    return "\n".join(lines).rstrip() + "\n"


def archive_transcript(skill_dir: Path, output_path: Path, target: str, self_name: str, mirror_name: str) -> Path:
    imports_dir = skill_dir / "knowledge" / "imports"
    imports_dir.mkdir(parents=True, exist_ok=True)
    archive_path = imports_dir / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-imessage.md"
    archive_path.write_text(
        render_archive(
            source=f"imessage:{target}",
            self_name=self_name,
            mirror_name=mirror_name,
            note=f"Imported from iMessage chat.db for target {target}.",
            text_files=[output_path],
            copied_images=[],
        ),
        encoding="utf-8",
    )
    return archive_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract iMessage transcript files for create-shuixian.")
    parser.add_argument("--db", required=True, help="Path to ~/Library/Messages/chat.db")
    parser.add_argument("--target", required=True, help="Phone number, email, or Apple ID substring")
    parser.add_argument("--output", default="./imessage-messages.txt", help="Transcript output path")
    parser.add_argument("--archive-to", help="Generated shuixian skill directory to archive into")
    parser.add_argument("--self-name", default="", help="Optional user display name for archive metadata")
    parser.add_argument("--mirror-name", default="", help="Optional mirror display name for archive metadata")
    args = parser.parse_args()

    db_path = Path(args.db).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    handle_display, messages = extract_messages(db_path, args.target)
    output_path.write_text(render_transcript(handle_display, args.target, messages), encoding="utf-8")

    print(f"Matched iMessage target: {handle_display}")
    print(f"Extracted {len(messages)} messages.")
    print(f"Wrote normalized transcript to {output_path}")

    if args.archive_to:
        archive_path = archive_transcript(
            Path(args.archive_to).expanduser().resolve(),
            output_path,
            args.target,
            args.self_name,
            args.mirror_name,
        )
        print(f"Archived transcript to {archive_path}")


if __name__ == "__main__":
    main()
