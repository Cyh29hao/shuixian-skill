#!/usr/bin/env python3
"""
Import generic transcript exports into normalized text for create-shuixian.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from source_importer import render_archive


TEXT_PATTERNS = [
    re.compile(r"\[((?:\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?::\d{2})?|unknown-time))\]\s+([^:]+):\s+(.+)"),
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

    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        try:
            raw = float(value)
            if abs(raw) >= 10**11:
                raw = raw / 1000
            return datetime.fromtimestamp(raw, timezone.utc).replace(tzinfo=None)
        except (OSError, OverflowError, ValueError):
            return None

    text = normalize_text(value)
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc).replace(tzinfo=None) if parsed.tzinfo else parsed
    except ValueError:
        pass
    for time_format in TIME_FORMATS:
        try:
            return datetime.strptime(text, time_format)
        except ValueError:
            continue
    return None


def parse_text_lines(content: str) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    lines = content.splitlines()
    normalized = bool(lines and lines[0] == "# Imported Transcript" and "## Conversation" in lines)
    if normalized:
        lines = lines[lines.index("## Conversation") + 1:]

    for raw_line in lines:
        if normalized and messages and raw_line.startswith("    "):
            messages[-1]["content"] += "\n" + raw_line[4:]
            continue
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
        if key in payload and payload[key] not in (None, ""):
            return payload[key]
    return None


def message_text(value: Any) -> str:
    """Extract text blocks without turning attachments or metadata into prose."""
    if isinstance(value, str):
        # Segment-edge whitespace can separate inline words; trim only after
        # the complete message has been assembled.
        return value.replace("\x00", " ")
    if isinstance(value, list):
        # Typed model content blocks are separate paragraphs. Telegram rich-text
        # arrays mix strings and entities and must retain inline concatenation.
        separate_blocks = bool(value) and all(
            isinstance(part, dict) and part.get("type") in {"text", "input_text", "output_text"}
            for part in value
        )
        separator = "\n" if separate_blocks else ""
        return separator.join(message_text(part) for part in value)
    if isinstance(value, dict):
        for key in ("parts", "text", "content"):
            if key in value:
                return message_text(value[key])
    return ""


def sender_text(value: Any) -> str:
    if isinstance(value, dict):
        value = first_value(value, ("name", "display_name", "role", "id"))
    return " ".join(normalize_text(value).split()) if isinstance(value, (str, int)) else "unknown"


def parse_json_records(payload: Any) -> list[dict[str, Any]]:
    """Handle plain records and common export containers, preserving speakers."""
    if isinstance(payload, list):
        return [message for item in payload for message in parse_json_records(item)]
    if not isinstance(payload, dict):
        return []

    # A message may carry auxiliary `data`/`payload` metadata. Read the actual
    # record before treating those keys as conversation containers.
    if isinstance(payload.get("message"), dict) and not any(key in payload for key in SENDER_KEYS):
        return parse_json_records(payload["message"])
    content = normalize_text(message_text(first_value(payload, CONTENT_KEYS)))
    if content:
        return [{
            "timestamp": parse_datetime(first_value(payload, TIME_KEYS + ("create_time",))),
            "sender": sender_text(first_value(payload, SENDER_KEYS)) or "unknown",
            "content": content,
        }]

    # OpenAI exports contain branches; walk only the selected conversation path.
    mapping = payload.get("mapping")
    if isinstance(mapping, dict):
        current = payload.get("current_node")
        if isinstance(current, str) and current in mapping:
            nodes, seen = [], set()
            while isinstance(current, str) and current in mapping and current not in seen:
                seen.add(current)
                node = mapping[current]
                if not isinstance(node, dict):
                    break
                nodes.append(node.get("message"))
                current = node.get("parent")
            return parse_json_records(list(reversed(nodes)))
        return parse_json_records([node.get("message") for node in mapping.values() if isinstance(node, dict)])

    for key in ("messages", "conversations", "chats", "list", "data", "payload"):
        container = payload.get(key)
        if isinstance(container, (dict, list)):
            return parse_json_records(container)
    return []


def parse_file(path: Path, forced_format: str) -> list[dict[str, Any]]:
    try:
        content = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError(
            f"{path}: input is not valid UTF-8. Preserve the original, save a copy "
            "as UTF-8 (with or without BOM), and retry with that copy."
        ) from None

    if forced_format == "text":
        return parse_text_lines(content)

    if forced_format == "jsonl":
        records = []
        for line_number, line in enumerate(content.splitlines(), 1):
            if not line.strip():
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as error:
                raise ValueError(
                    f"{path}: line {line_number}, column {error.colno}: invalid JSON ({error.msg}). "
                    "Fix this input file and retry."
                ) from error
        return parse_json_records(records)

    if forced_format == "json":
        try:
            payload = json.loads(content)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"{path}: line {error.lineno}, column {error.colno}: invalid JSON ({error.msg}). "
                "Fix this input file and retry."
            ) from error
        return parse_json_records(payload)

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
        # Without timestamps, identical utterances can be separate real turns.
        if message["timestamp"] is not None and key in seen:
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
        "- Timestamp Note: epoch and offset-aware timestamps are normalized to UTC; naive timestamps retain their original wall time",
        "",
        "## Conversation",
        "",
    ]

    for message in messages:
        timestamp = message["timestamp"].strftime("%Y-%m-%d %H:%M:%S") if message["timestamp"] else "unknown-time"
        content_lines = message["content"].splitlines()
        lines.append(f"[{timestamp}] {message['sender']}: {content_lines[0]}")
        lines.extend(f"    {line}" for line in content_lines[1:])

    return "\n".join(lines).rstrip() + "\n"


def archive_transcript(skill_dir: Path, output_path: Path, source_label: str, self_name: str, mirror_name: str) -> Path:
    imports_dir = skill_dir / "knowledge" / "imports"
    imports_dir.mkdir(parents=True, exist_ok=True)
    archive_path = imports_dir / f"{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}-transcript.md"
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
    input_paths = [Path(value).expanduser().resolve() for value in args.input]
    output_path = Path(args.output).expanduser().resolve()
    try:
        aliases_input = output_path in input_paths or (
            output_path.exists() and any(path.exists() and output_path.samefile(path) for path in input_paths)
        )
    except OSError as error:
        parser.error(f"Cannot verify output preserves original inputs: {error}")
    if aliases_input:
        parser.error("Output must differ from every input file; originals are preserved.")
    try:
        for path in input_paths:
            all_messages.extend(parse_file(path, args.format))
    except (OSError, ValueError) as error:
        parser.error(str(error))

    messages = dedupe_messages(all_messages)
    if not messages:
        parser.error("No text messages found; check the input format or export structure.")
    archive_dir = Path(args.archive_to).expanduser().resolve() if args.archive_to else None
    if archive_dir:
        imports_dir = archive_dir / "knowledge" / "imports"
        try:
            for directory in (imports_dir, *imports_dir.parents):
                if directory.exists() and not directory.is_dir():
                    parser.error(
                        f"Archive destination is blocked by a file: {directory}. "
                        "Choose a directory with --archive-to and retry; no files were written."
                    )
        except OSError as error:
            parser.error(f"Cannot check archive destination {imports_dir}: {error}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_transcript(args.source_label, messages), encoding="utf-8")

    print(f"Parsed {len(messages)} messages.")
    print(f"Wrote normalized transcript to {output_path}")

    if archive_dir:
        archive_path = archive_transcript(
            archive_dir,
            output_path,
            args.source_label,
            args.self_name,
            args.mirror_name,
        )
        print(f"Archived transcript to {archive_path}")


if __name__ == "__main__":
    for cli_stream in (sys.stdout, sys.stderr):
        if hasattr(cli_stream, "reconfigure"):
            cli_stream.reconfigure(encoding="utf-8")
    main()
