#!/usr/bin/env python3
"""
Normalize WeChat chat history for create-shuixian.
"""

from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from source_importer import render_archive


CONTACT_TABLE_CANDIDATES = ("Contact", "rcontact")
MESSAGE_TABLE_CANDIDATES = ("MSG", "Message", "msg")
CONTACT_ID_COLUMNS = ("UsrName", "UserName", "username")
CONTACT_NICK_COLUMNS = ("NickName", "Nickname", "nick_name")
CONTACT_REMARK_COLUMNS = ("Remark", "RemarkName", "ConRemark", "remark")
CONTACT_ALIAS_COLUMNS = ("Alias", "alias")
MESSAGE_TIME_COLUMNS = ("CreateTime", "CreateTimeMs", "MsgTime", "time", "Timestamp")
MESSAGE_CONTENT_COLUMNS = ("StrContent", "Content", "DisplayContent", "Message")
MESSAGE_TALKER_COLUMNS = ("StrTalker", "Talker", "TalkerId", "Partner", "UserName")
MESSAGE_IS_SENDER_COLUMNS = ("IsSender", "isSend", "IsFromMe", "Des")
MESSAGE_TYPE_COLUMNS = ("Type", "MsgType", "type")
MESSAGE_SUBTYPE_COLUMNS = ("SubType", "Subtype", "sub_type")


@dataclass
class Contact:
    rowid: int | None
    wxid: str
    nickname: str
    remark: str
    alias: str
    display_name: str


@dataclass
class ContactReportEntry:
    contact: Contact
    total_messages: int = 0
    sent_by_me: int = 0
    sent_by_them: int = 0
    first_timestamp: datetime | None = None
    last_timestamp: datetime | None = None


def sqlite_connect(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(str(path))


def quote_ident(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def sqlite_tables(conn: sqlite3.Connection) -> list[str]:
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return [str(row[0]) for row in cursor.fetchall()]


def table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    cursor = conn.execute(f"PRAGMA table_info({quote_ident(table_name)})")
    return {str(row[1]) for row in cursor.fetchall()}


def pick_column(columns: Iterable[str], candidates: tuple[str, ...]) -> str | None:
    column_set = set(columns)
    for candidate in candidates:
        if candidate in column_set:
            return candidate
    return None


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\x00", " ").strip()


def normalize_lookup_key(value: Any) -> str:
    return normalize_text(value).lower()


def find_micro_msg_db(root: Path) -> Path:
    direct = root / "MicroMsg.db"
    if direct.exists():
        return direct
    matches = list(root.glob("**/MicroMsg.db"))
    if not matches:
        raise FileNotFoundError(f"Could not find MicroMsg.db under {root}")
    return matches[0]


def find_message_dbs(root: Path) -> list[Path]:
    matches = sorted(path for path in root.glob("**/MSG*.db") if path.name != "MicroMsg.db")
    if matches:
        return matches
    return sorted(root.glob("**/msg_*.db"))


def load_contacts(micro_msg_db: Path) -> list[Contact]:
    contacts: list[Contact] = []
    with sqlite_connect(micro_msg_db) as conn:
        tables = sqlite_tables(conn)
        for table_name in CONTACT_TABLE_CANDIDATES:
            if table_name not in tables:
                continue

            columns = table_columns(conn, table_name)
            wxid_col = pick_column(columns, CONTACT_ID_COLUMNS)
            if not wxid_col:
                continue

            nickname_col = pick_column(columns, CONTACT_NICK_COLUMNS)
            remark_col = pick_column(columns, CONTACT_REMARK_COLUMNS)
            alias_col = pick_column(columns, CONTACT_ALIAS_COLUMNS)

            aliases = [("__rowid__", "rowid"), ("wxid", wxid_col)]
            if nickname_col:
                aliases.append(("nickname", nickname_col))
            if remark_col:
                aliases.append(("remark", remark_col))
            if alias_col:
                aliases.append(("alias", alias_col))

            selected = [f"rowid AS {quote_ident('__rowid__')}"]
            for alias, column_name in aliases[1:]:
                selected.append(f"{quote_ident(column_name)} AS {quote_ident(alias)}")

            query = f"SELECT {', '.join(selected)} FROM {quote_ident(table_name)}"
            for row in conn.execute(query):
                labels = [item[0] for item in aliases]
                payload = dict(zip(labels, row))
                wxid = normalize_text(payload.get("wxid"))
                if not wxid or wxid.endswith("@chatroom") or wxid == "filehelper":
                    continue

                nickname = normalize_text(payload.get("nickname"))
                remark = normalize_text(payload.get("remark"))
                alias = normalize_text(payload.get("alias"))
                display_name = remark or nickname or alias or wxid

                contacts.append(
                    Contact(
                        rowid=int(payload.get("__rowid__")) if payload.get("__rowid__") is not None else None,
                        wxid=wxid,
                        nickname=nickname,
                        remark=remark,
                        alias=alias,
                        display_name=display_name,
                    )
                )
            break

    unique_contacts: dict[tuple[str, str], Contact] = {}
    for contact in contacts:
        unique_contacts[(contact.wxid, contact.display_name)] = contact
    return sorted(unique_contacts.values(), key=lambda item: item.display_name.lower())


def match_contact(contacts: list[Contact], target: str) -> Contact:
    needle = target.strip().lower()
    exact_matches: list[Contact] = []
    fuzzy_matches: list[Contact] = []

    for contact in contacts:
        haystacks = {
            contact.display_name.lower(),
            contact.nickname.lower(),
            contact.remark.lower(),
            contact.alias.lower(),
            contact.wxid.lower(),
        }
        if needle in haystacks:
            exact_matches.append(contact)
            continue
        if any(needle and needle in haystack for haystack in haystacks):
            fuzzy_matches.append(contact)

    if exact_matches:
        return exact_matches[0]
    if fuzzy_matches:
        return fuzzy_matches[0]

    sample = ", ".join(contact.display_name for contact in contacts[:10])
    raise LookupError(f"Could not find contact `{target}`. Sample contacts: {sample}")


def possible_contact_keys(contact: Contact) -> list[Any]:
    keys: list[Any] = []
    if contact.rowid is not None:
        keys.extend([contact.rowid, str(contact.rowid)])
    for value in (contact.wxid, contact.nickname, contact.remark, contact.alias, contact.display_name):
        if value and value not in keys:
            keys.append(value)
    return keys


def build_contact_lookup(contacts: list[Contact]) -> dict[str, Contact]:
    lookup: dict[str, Contact] = {}
    for contact in contacts:
        for key in possible_contact_keys(contact):
            normalized = normalize_lookup_key(key)
            if normalized and normalized not in lookup:
                lookup[normalized] = contact
    return lookup


def coerce_timestamp(raw_value: Any) -> datetime | None:
    if raw_value in (None, ""):
        return None
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return None

    if value > 10**15:
        value = value / 1_000_000_000
    elif value > 10**12:
        value = value / 1000

    try:
        return datetime.fromtimestamp(value)
    except (OverflowError, OSError, ValueError):
        return None


def type_name(raw_type: Any, raw_subtype: Any) -> str:
    try:
        type_code = int(raw_type)
    except (TypeError, ValueError):
        return "unknown"

    mapping = {
        1: "text",
        3: "image",
        34: "voice",
        43: "video",
        47: "sticker",
        48: "location",
        49: "file-or-link",
        50: "call",
        10000: "system",
    }
    label = mapping.get(type_code, f"type-{type_code}")
    if raw_subtype not in (None, ""):
        return f"{label}/{raw_subtype}"
    return label


def message_tables(conn: sqlite3.Connection) -> list[tuple[str, set[str]]]:
    discovered: list[tuple[str, set[str]]] = []
    for table_name in sqlite_tables(conn):
        columns = table_columns(conn, table_name)
        if table_name not in MESSAGE_TABLE_CANDIDATES:
            if not pick_column(columns, MESSAGE_CONTENT_COLUMNS) or not pick_column(columns, MESSAGE_TIME_COLUMNS):
                continue
        discovered.append((table_name, columns))
    return discovered


def extract_messages_from_one_db(msg_db: Path, contact: Contact) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    with sqlite_connect(msg_db) as conn:
        for table_name, columns in message_tables(conn):
            time_col = pick_column(columns, MESSAGE_TIME_COLUMNS)
            content_col = pick_column(columns, MESSAGE_CONTENT_COLUMNS)
            talker_col = pick_column(columns, MESSAGE_TALKER_COLUMNS)
            sender_col = pick_column(columns, MESSAGE_IS_SENDER_COLUMNS)
            type_col = pick_column(columns, MESSAGE_TYPE_COLUMNS)
            subtype_col = pick_column(columns, MESSAGE_SUBTYPE_COLUMNS)

            if not time_col or not content_col:
                continue

            select_specs = [("ts", time_col), ("content", content_col)]
            if talker_col:
                select_specs.append(("talker", talker_col))
            if sender_col:
                select_specs.append(("is_sender", sender_col))
            if type_col:
                select_specs.append(("raw_type", type_col))
            if subtype_col:
                select_specs.append(("raw_subtype", subtype_col))

            selected = [f"{quote_ident(column_name)} AS {quote_ident(alias)}" for alias, column_name in select_specs]
            query = f"SELECT {', '.join(selected)} FROM {quote_ident(table_name)}"
            params: list[Any] = []
            if talker_col:
                keys = possible_contact_keys(contact)
                placeholders = ", ".join("?" for _ in keys)
                query += f" WHERE {quote_ident(talker_col)} IN ({placeholders})"
                params.extend(keys)
            query += f" ORDER BY {quote_ident(time_col)} ASC"

            try:
                cursor = conn.execute(query, params)
            except sqlite3.Error:
                continue

            aliases = [alias for alias, _ in select_specs]
            for row in cursor.fetchall():
                payload = dict(zip(aliases, row))
                content = normalize_text(payload.get("content"))
                raw_type = payload.get("raw_type")
                if not content and raw_type in (1, None):
                    continue

                timestamp = coerce_timestamp(payload.get("ts"))
                is_sender = payload.get("is_sender")
                sender = "我" if is_sender in (1, "1", True) else contact.display_name

                messages.append(
                    {
                        "timestamp": timestamp,
                        "sender": sender,
                        "content": content or f"[{type_name(raw_type, payload.get('raw_subtype'))}]",
                        "message_type": type_name(raw_type, payload.get("raw_subtype")),
                        "source_db": msg_db.name,
                    }
                )

    return messages


def dedupe_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[Any, ...]] = set()
    ordered: list[dict[str, Any]] = []
    for message in messages:
        key = (
            message["timestamp"].isoformat() if message["timestamp"] else None,
            message["sender"],
            message["content"],
            message["message_type"],
        )
        if key in seen:
            continue
        seen.add(key)
        ordered.append(message)
    ordered.sort(key=lambda item: item["timestamp"] or datetime.min)
    return ordered


def collect_contact_report(root: Path) -> list[ContactReportEntry]:
    contacts = load_contacts(find_micro_msg_db(root))
    contact_lookup = build_contact_lookup(contacts)
    stats: dict[str, ContactReportEntry] = {
        contact.wxid: ContactReportEntry(contact=contact) for contact in contacts
    }

    db_files = find_message_dbs(root)
    if not db_files:
        raise FileNotFoundError(f"Could not find MSG*.db under {root}")

    for msg_db in db_files:
        with sqlite_connect(msg_db) as conn:
            for table_name, columns in message_tables(conn):
                talker_col = pick_column(columns, MESSAGE_TALKER_COLUMNS)
                time_col = pick_column(columns, MESSAGE_TIME_COLUMNS)
                sender_col = pick_column(columns, MESSAGE_IS_SENDER_COLUMNS)
                if not talker_col or not time_col:
                    continue

                selected = [
                    f"{quote_ident(talker_col)} AS {quote_ident('talker')}",
                    f"{quote_ident(time_col)} AS {quote_ident('ts')}",
                ]
                if sender_col:
                    selected.append(f"{quote_ident(sender_col)} AS {quote_ident('is_sender')}")

                query = f"SELECT {', '.join(selected)} FROM {quote_ident(table_name)}"
                try:
                    cursor = conn.execute(query)
                except sqlite3.Error:
                    continue

                aliases = ["talker", "ts"]
                if sender_col:
                    aliases.append("is_sender")

                for row in cursor.fetchall():
                    payload = dict(zip(aliases, row))
                    contact = contact_lookup.get(normalize_lookup_key(payload.get("talker")))
                    if not contact:
                        continue

                    entry = stats[contact.wxid]
                    entry.total_messages += 1

                    is_sender = payload.get("is_sender")
                    if is_sender in (1, "1", True):
                        entry.sent_by_me += 1
                    else:
                        entry.sent_by_them += 1

                    timestamp = coerce_timestamp(payload.get("ts"))
                    if timestamp:
                        if entry.first_timestamp is None or timestamp < entry.first_timestamp:
                            entry.first_timestamp = timestamp
                        if entry.last_timestamp is None or timestamp > entry.last_timestamp:
                            entry.last_timestamp = timestamp

    report = [entry for entry in stats.values() if entry.total_messages > 0]
    report.sort(
        key=lambda item: (
            item.total_messages,
            item.last_timestamp or datetime.min,
            item.contact.display_name.lower(),
        ),
        reverse=True,
    )
    return report


def render_contact_report(entries: list[ContactReportEntry], top: int) -> str:
    visible = entries[:top]
    lines = [
        "# WeChat Contact Report",
        "",
        f"- Contact Count With Messages: {len(entries)}",
        f"- Showing Top: {min(len(visible), top)}",
        "- Sort: message count first, then recency",
        "",
        "Use this report to decide which transcripts to extract for relationship or worldview analysis.",
        "",
        "## Ranked Contacts",
        "",
    ]

    for index, entry in enumerate(visible, start=1):
        first_seen = entry.first_timestamp.strftime("%Y-%m-%d") if entry.first_timestamp else "unknown"
        last_seen = entry.last_timestamp.strftime("%Y-%m-%d") if entry.last_timestamp else "unknown"
        lines.extend(
            [
                f"### {index}. {entry.contact.display_name}",
                "",
                f"- wxid: {entry.contact.wxid}",
                f"- messages: {entry.total_messages}",
                f"- 我发出: {entry.sent_by_me}",
                f"- 对方发出: {entry.sent_by_them}",
                f"- first_seen: {first_seen}",
                f"- last_seen: {last_seen}",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def render_transcript(contact: Contact, messages: list[dict[str, Any]]) -> str:
    lines = [
        "# WeChat Transcript",
        "",
        f"- Contact: {contact.display_name}",
        f"- wxid: {contact.wxid}",
        f"- Message Count: {len(messages)}",
        "",
        "## Conversation",
        "",
    ]

    for message in messages:
        timestamp = message["timestamp"].strftime("%Y-%m-%d %H:%M") if message["timestamp"] else "unknown-time"
        lines.append(f"[{timestamp}] {message['sender']}: {message['content']}")

    return "\n".join(lines).rstrip() + "\n"


def archive_transcript(skill_dir: Path, output_path: Path, contact: Contact, self_name: str, mirror_name: str) -> Path:
    imports_dir = skill_dir / "knowledge" / "imports"
    imports_dir.mkdir(parents=True, exist_ok=True)
    archive_path = imports_dir / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}-wechat-{contact.wxid}.md"
    archive_path.write_text(
        render_archive(
            source=f"wechat:{contact.display_name}",
            self_name=self_name,
            mirror_name=mirror_name,
            note=f"Imported from decrypted WeChat databases for {contact.display_name}.",
            text_files=[output_path],
            copied_images=[],
        ),
        encoding="utf-8",
    )
    return archive_path


def command_list_contacts(root: Path) -> None:
    contacts = load_contacts(find_micro_msg_db(root))
    print(f"Found {len(contacts)} contacts:\n")
    for contact in contacts:
        alias_note = f"  alias={contact.alias}" if contact.alias else ""
        remark_note = f"  remark={contact.remark}" if contact.remark else ""
        print(f"- {contact.display_name} [{contact.wxid}]{remark_note}{alias_note}")


def command_contact_report(
    root: Path,
    output_path: Path,
    top: int,
    archive_to: Path | None,
    self_name: str,
    mirror_name: str,
) -> None:
    report = collect_contact_report(root)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_contact_report(report, top), encoding="utf-8")

    print(f"Profiled {len(report)} contacts with message history.")
    print(f"Wrote contact report to {output_path}")

    if archive_to:
        archive_path = archive_transcript(
            archive_to,
            output_path,
            Contact(
                rowid=None,
                wxid="contact-report",
                nickname="WeChat Contact Report",
                remark="",
                alias="",
                display_name="WeChat Contact Report",
            ),
            self_name,
            mirror_name,
        )
        print(f"Archived contact report to {archive_path}")


def command_extract(root: Path, target: str, output_path: Path, archive_to: Path | None, self_name: str, mirror_name: str) -> None:
    contacts = load_contacts(find_micro_msg_db(root))
    contact = match_contact(contacts, target)
    db_files = find_message_dbs(root)
    if not db_files:
        raise FileNotFoundError(f"Could not find MSG*.db under {root}")

    all_messages: list[dict[str, Any]] = []
    for msg_db in db_files:
        all_messages.extend(extract_messages_from_one_db(msg_db, contact))

    messages = dedupe_messages(all_messages)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_transcript(contact, messages), encoding="utf-8")

    print(f"Matched contact: {contact.display_name} [{contact.wxid}]")
    print(f"Extracted {len(messages)} messages.")
    print(f"Wrote normalized transcript to {output_path}")

    if archive_to:
        archive_path = archive_transcript(archive_to, output_path, contact, self_name, mirror_name)
        print(f"Archived transcript to {archive_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="List and extract WeChat chats for create-shuixian.")
    parser.add_argument("--db-dir", required=True, help="Directory that contains decrypted MicroMsg.db and MSG*.db files.")
    parser.add_argument("--list-contacts", action="store_true", help="List contacts from MicroMsg.db.")
    parser.add_argument("--contact-report", action="store_true", help="Summarize the busiest and most recent contacts.")
    parser.add_argument("--extract", action="store_true", help="Extract one contact's transcript from MSG*.db files.")
    parser.add_argument("--target", help="Contact display name, remark, alias, or wxid to match.")
    parser.add_argument("--output", default="./wechat-messages.txt", help="Transcript output path.")
    parser.add_argument("--top", type=int, default=30, help="Maximum contacts to include in a contact report.")
    parser.add_argument("--archive-to", help="Generated shuixian skill directory to archive into.")
    parser.add_argument("--self-name", default="", help="Optional user display name for archive metadata.")
    parser.add_argument("--mirror-name", default="", help="Optional mirror display name for archive metadata.")
    args = parser.parse_args()

    root = Path(args.db_dir).expanduser().resolve()
    default_output = "./wechat-messages.txt"
    output_value = args.output
    if args.contact_report and output_value == default_output:
        output_value = "./wechat-contact-report.md"

    if args.list_contacts:
        command_list_contacts(root)
        return

    if args.contact_report:
        command_contact_report(
            root=root,
            output_path=Path(output_value).expanduser().resolve(),
            top=max(args.top, 1),
            archive_to=Path(args.archive_to).expanduser().resolve() if args.archive_to else None,
            self_name=args.self_name,
            mirror_name=args.mirror_name,
        )
        return

    if args.extract:
        if not args.target:
            raise SystemExit("`--extract` requires `--target`.")
        command_extract(
            root=root,
            target=args.target,
            output_path=Path(output_value).expanduser().resolve(),
            archive_to=Path(args.archive_to).expanduser().resolve() if args.archive_to else None,
            self_name=args.self_name,
            mirror_name=args.mirror_name,
        )
        return

    parser.print_help()


if __name__ == "__main__":
    main()
