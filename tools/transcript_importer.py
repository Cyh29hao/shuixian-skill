#!/usr/bin/env python3
"""
Import generic transcript exports into normalized text for create-shuixian.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from source_importer import render_archive


TEXT_PATTERNS = [
    re.compile(r"\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?::\d{2})?)\]\s+([^:]+):\s+(.+)"),
    re.compile(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?::\d{2})?)\s+([^:]+):\s+(.+)"),
    re.compile(r"([^:]+)\s+\((\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?::\d{2})?)\):\s+(.+)"),
]
TIME_FORMATS = ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S")
SENDER_KEYS = ("sender", "from", "author", "name", "role", "speaker")
CONTENT_KEYS = ("content", "text", "message", "body")
TIME_KEYS = ("timestamp", "time", "date", "created_at", "datetime")


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\x00", " ").strip()


def parse_datetime(value: Any) -> datetime | None:
    if value in (None, ""):
        return None

    if isinstance(value, (int, float)):
        try:
            raw = float(value)
            if raw > 10**12:
                raw = raw / 1000
            return datetime.fromtimestamp(raw)
        except (OSError, OverflowError, ValueError):
            return None

    text = normalize_text(value)
    for time_format in TIME_FORMATS:
        try:
            return datetime.strptime(text, time_format)
        except ValueError:
            continue
    return None


def parse_text_lines(content: str) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        matched = False
        for pattern in TEXT_PATTERNS:
            match = pattern.match(line)
            if not match:
                continue

            first, second, message_text = match.groups()
            if pattern is TEXT_PATTERNS[2]:
                sender, timestamp = first, second
            else:
                timestamp, sender = first, second

            messages.append(
                {
                    "timestamp": parse_datetime(timestamp),
                    "sender": normalize_text(sender),
                    "content": normalize_text(message_text),
                }
            )
            matched = True
            break

        if not matched:
            messages.append({"timestamp": None, "sender": "unknown", "content": line})

    return messages


def first_value(payload: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in payload:
            return payload[key]
    return None


def parse_json_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        if "messages" in payload and isinstance(payload["messages"], list):
            payload = payload["messages"]
        else:
            payload = [payload]

    if not isinstance(payload, list):
        return []

    messages: list[dict[str, Any]] = []
    for item in payload:
        if not isinstance(item, dict):
            continue

        sender = normalize_text(first_value(item, SENDER_KEYS)) or "unknown"
        content = normalize_text(first_value(item, CONTENT_KEYS))
        if not content:
            continue

        messages.append(
            {
                "timestamp": parse_datetime(first_value(item, TIME_KEYS)),
                "sender": sender,
                "content": content,
            }
        )

    return messages


def parse_file(path: Path, forced_format: str) -> list[dict[str, Any]]:
    content = path.read_text(encoding="utf-8-sig", errors="replace")

    if forced_format == "text":
        return parse_text_lines(content)

    if forced_format == "jsonl":
        records = [json.loads(line) for line in content.splitlines() if line.strip()]
        return parse_json_records(records)

    if forced_format == "json":
        return parse_json_records(json.loads(content))

    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        return parse_file(path, "jsonl")
    if suffix == ".json":
        return parse_file(path, "json")
    return parse_text_lines(content)


def dedupe_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    ordered: list[dict[str, Any]] = []
    for message in messages:
        key = (
            message["timestamp"].isoformat() if message["timestamp"] else None,
            message["sender"],
            message["content"],
        )
        if key in seen:
            continue
        seen.add(key)
        ordered.append(message)

    ordered.sort(key=lambda item: item["timestamp"] or datetime.min)
    return ordered


def render_transcript(source_label: str, messages: list[dict[str, Any]]) -> str:
    lines = [
        "# Imported Transcript",
        "",
        f"- Source: {source_label}",
        f"- Message Count: {len(messages)}",
        "",
        "## Conversation",
        "",
    ]

    for message in messages:
        timestamp = message["timestamp"].strftime("%Y-%m-%d %H:%M") if message["timestamp"] else "unknown-time"
        lines.append(f"[{timestamp}] {message['sender']}: {message['content']}")

    return "\n".join(lines).rstrip() + "\n"


def archive_transcript(skill_dir: Path, output_path: Path, source_label: str, self_name: str, mirror_name: str) -> Path:
    imports_dir = skill_dir / "knowledge" / "imports"
    imports_dir.mkdir(parents=True, exist_ok=True)
    archive_path = imports_dir / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-transcript.md"
    archive_path.write_text(
        render_archive(
            source=source_label,
            self_name=self_name,
            mirror_name=mirror_name,
            note=f"Imported generic transcript from {source_label}.",
            text_files=[output_path],
            copied_images=[],
        ),
        encoding="utf-8",
    )
    return archive_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Import generic transcript exports for create-shuixian.")
    parser.add_argument("--input", action="append", required=True, help="Transcript file path. Repeat for multiple files.")
    parser.add_argument("--format", choices=("auto", "text", "json", "jsonl"), default="auto", help="Force one parser")
    parser.add_argument("--source-label", default="generic-transcript", help="Source label written into the normalized transcript")
    parser.add_argument("--output", default="./transcript.txt", help="Normalized transcript output path")
    parser.add_argument("--archive-to", help="Generated shuixian skill directory to archive into")
    parser.add_argument("--self-name", default="", help="Optional user display name for archive metadata")
    parser.add_argument("--mirror-name", default="", help="Optional mirror display name for archive metadata")
    args = parser.parse_args()

    all_messages: list[dict[str, Any]] = []
    for input_value in args.input:
        path = Path(input_value).expanduser().resolve()
        all_messages.extend(parse_file(path, args.format))

    messages = dedupe_messages(all_messages)
    output_path = Path(args.output).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_transcript(args.source_label, messages), encoding="utf-8")

    print(f"Parsed {len(messages)} messages.")
    print(f"Wrote normalized transcript to {output_path}")

    if args.archive_to:
        archive_path = archive_transcript(
            Path(args.archive_to).expanduser().resolve(),
            output_path,
            args.source_label,
            args.self_name,
            args.mirror_name,
        )
        print(f"Archived transcript to {archive_path}")


if __name__ == "__main__":
    main()
