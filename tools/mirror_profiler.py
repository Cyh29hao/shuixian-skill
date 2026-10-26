#!/usr/bin/env python3
"""
Turn normalized transcripts into a compact relationship and value profile report.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Iterable


MESSAGE_PATTERN = re.compile(r"^\[(?P<timestamp>[^\]]+)\]\s+(?P<sender>[^:]+):\s+(?P<content>.+)$")
TIME_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M")

DEFAULT_SELF_ALIASES = {"我", "me", "self", "myself", "user"}

KINSHIP_HINTS = (
    "妈妈",
    "母亲",
    "爸爸",
    "父亲",
    "爷爷",
    "奶奶",
    "外公",
    "外婆",
    "哥哥",
    "姐姐",
    "弟弟",
    "妹妹",
    "舅",
    "姨",
    "叔",
    "姑",
    "伯",
    "mom",
    "dad",
    "mother",
    "father",
    "brother",
    "sister",
)

RELATION_KEYWORDS: dict[str, tuple[str, ...]] = {
    "family-like": KINSHIP_HINTS + ("家人", "parents"),
    "coworker": (
        "同事",
        "老板",
        "项目",
        "需求",
        "汇报",
        "开会",
        "上班",
        "下班",
        "会议",
        "客户",
        "okr",
        "deadline",
        "meeting",
        "manager",
        "coworker",
        "office",
        "slack",
    ),
    "mentor": ("老师", "导师", "学长", "学姐", "前辈", "mentor", "professor", "coach"),
    "ex": (
        "前任",
        "前男友",
        "前女友",
        "分手",
        "复合",
        "挽回",
        "回头",
        "放不下",
        "前夫",
        "前妻",
        "ex",
        "breakup",
        "got back",
    ),
    "crush": (
        "喜欢你",
        "心动",
        "想你",
        "约会",
        "见你",
        "好想见",
        "好帅",
        "好漂亮",
        "crush",
        "date",
        "miss you",
    ),
    "situationship": (
        "暧昧",
        "说不清",
        "算什么",
        "别认真",
        "复杂",
        "冷处理",
        "断联",
        "朋友以上",
        "不确定",
        "situationship",
        "undefined",
        "mixed signals",
    ),
}

AFFECTION_WORDS = (
    "宝贝",
    "宝宝",
    "亲爱的",
    "抱抱",
    "晚安",
    "早安",
    "爱你",
    "想你",
    "陪你",
    "乖",
    "hug",
    "kiss",
    "love you",
    "miss you",
    "baby",
    "darling",
)
SUPPORT_WORDS = (
    "没事",
    "别急",
    "先别",
    "我在",
    "陪你",
    "辛苦了",
    "抱抱",
    "慢慢来",
    "你可以",
    "不用怕",
    "it's okay",
    "i'm here",
    "take your time",
)
CONFLICT_WORDS = (
    "生气",
    "烦",
    "吵",
    "吵架",
    "不想理",
    "别说了",
    "踩雷",
    "受不了",
    "hurt",
    "angry",
    "upset",
    "fight",
)
REPAIR_WORDS = (
    "对不起",
    "抱歉",
    "是我不对",
    "我收回",
    "我们慢慢说",
    "重新来",
    "my bad",
    "sorry",
    "let's reset",
)
SELF_DISCLOSURE_WORDS = (
    "我觉得",
    "我有点",
    "我害怕",
    "我不想",
    "我其实",
    "我可能",
    "我最近",
    "我今天",
    "我焦虑",
    "我难受",
    "我累",
    "i feel",
    "i'm scared",
    "i'm tired",
    "i don't want",
    "lately i",
)
FLIRT_WORDS = (
    "心动",
    "想亲",
    "好帅",
    "好漂亮",
    "脸红",
    "想见你",
    "想抱你",
    "撩",
    "暧昧",
    "hot",
    "cute",
    "pretty",
    "handsome",
    "date you",
)
LOGISTICS_WORDS = (
    "几点",
    "在哪",
    "到了",
    "走吧",
    "发我",
    "定位",
    "地址",
    "快递",
    "meeting",
    "schedule",
    "arrive",
    "where are you",
    "send me",
)
TOPIC_KEYWORDS: dict[str, tuple[str, ...]] = {
    # Ordinary preferences (喜欢短句、爱喝茶) do not establish a romantic topic.
    "love-and-relationship": ("恋爱", "恋人", "伴侣", "男友", "女友", "表白", "约会", "分手", "暧昧", "婚姻", "结婚", "爱你", "crush", "date", "relationship", "breakup"),
    "family-and-home": ("家里", "家人", "妈妈", "爸爸", "回家", "family", "mom", "dad", "home"),
    "work-and-study": ("工作", "上班", "同事", "开会", "老板", "学校", "导师", "作业", "study", "work", "meeting"),
    "gender-and-identity": ("女权", "男权", "lgbt", "同性恋", "跨性别", "gender", "feminism", "queer", "lesbian", "gay"),
    "money-and-future": ("钱", "工资", "存款", "房子", "买房", "未来", "career", "salary", "rent", "future"),
    "body-and-mental-state": ("累", "焦虑", "难受", "失眠", "崩溃", "抑郁", "tired", "anxious", "burnout", "panic"),
}


@dataclass
class Message:
    timestamp: datetime | None
    sender: str
    content: str


@dataclass
class TranscriptBundle:
    source_path: Path
    label: str
    source_hint: str
    messages: list[Message]


def normalize_text(value: str) -> str:
    return value.replace("\x00", " ").strip()


def lower_text(value: str) -> str:
    return normalize_text(value).lower()


def parse_timestamp(value: str) -> datetime | None:
    cleaned = normalize_text(value)
    if cleaned == "unknown-time":
        return None
    for fmt in TIME_FORMATS:
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def parse_messages(text: str) -> list[Message]:
    messages: list[Message] = []
    for line in text.splitlines():
        if messages and line.startswith("    "):
            messages[-1].content += "\n" + line[4:]
            continue
        match = MESSAGE_PATTERN.match(line.strip())
        if not match:
            continue
        messages.append(
            Message(
                timestamp=parse_timestamp(match.group("timestamp")),
                sender=normalize_text(match.group("sender")),
                content=normalize_text(match.group("content")),
            )
        )
    return messages


def transcript_label(text: str, fallback: str) -> tuple[str, str]:
    label = fallback
    source_hint = fallback
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- Contact:"):
            label = normalize_text(stripped.split(":", 1)[1]) or fallback
        elif stripped.startswith("- Target:"):
            label = normalize_text(stripped.split(":", 1)[1]) or label
        elif stripped.startswith("- Source:"):
            source_hint = normalize_text(stripped.split(":", 1)[1]) or source_hint
    return label, source_hint


def parse_archive_bundles(path: Path, text: str) -> list[TranscriptBundle]:
    bundles: list[TranscriptBundle] = []
    blocks = re.finditer(
        r"^## File:[^\S\n]+([^\n]+)\n\n(`{3,})text[^\S\n]*\n(.*?)^\2[^\S\n]*$",
        text, flags=re.DOTALL | re.MULTILINE,
    )
    for block in blocks:
        filename = normalize_text(block.group(1))
        transcript_text = block.group(3).strip()
        messages = parse_messages(transcript_text)
        if not messages:
            continue
        label, source_hint = transcript_label(transcript_text, filename)
        bundles.append(TranscriptBundle(source_path=path, label=label, source_hint=source_hint, messages=messages))
    return bundles


def parse_input_file(path: Path) -> list[TranscriptBundle]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        raise ValueError(
            f"Input is not valid UTF-8: {path}. Keep the original, save a UTF-8 copy, and retry."
        ) from error
    archive_bundles = parse_archive_bundles(path, text)
    if archive_bundles:
        return archive_bundles

    messages = parse_messages(text)
    if not messages:
        return []
    label, source_hint = transcript_label(text, path.stem)
    return [TranscriptBundle(source_path=path, label=label, source_hint=source_hint, messages=messages)]


def keyword_hits(text: str, keywords: Iterable[str]) -> int:
    lowered = lower_text(text)
    return sum(1 for keyword in keywords if (
        bool(re.search(r"(?<![a-z0-9_])" + re.escape(keyword) + r"(?![a-z0-9_])", lowered))
        if keyword.isascii() else keyword in lowered
    ))


def excerpt(text: str, limit: int = 60) -> str:
    cleaned = " ".join(text.split())
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1] + "…"


def confidence_label(score: int, gap: int) -> str:
    if score >= 10 and gap >= 4:
        return "high-confidence"
    if score >= 5 and gap >= 2:
        return "medium-confidence"
    return "soft-guess"


def choose_relation(messages: list[Message], label: str) -> tuple[str, str, list[str], Counter[str]]:
    scores: Counter[str] = Counter()
    reasons: list[str] = []
    joined_text = "\n".join(message.content for message in messages)
    lowered_label = lower_text(label)

    for category, keywords in RELATION_KEYWORDS.items():
        scores[category] += keyword_hits(joined_text, keywords)
        if keyword_hits(lowered_label, keywords):
            scores[category] += 8

    affection = keyword_hits(joined_text, AFFECTION_WORDS)
    flirt = keyword_hits(joined_text, FLIRT_WORDS)
    support = keyword_hits(joined_text, SUPPORT_WORDS)
    conflict = keyword_hits(joined_text, CONFLICT_WORDS)
    repair = keyword_hits(joined_text, REPAIR_WORDS)
    logistics = keyword_hits(joined_text, LOGISTICS_WORDS)
    disclosure = keyword_hits(joined_text, SELF_DISCLOSURE_WORDS)

    if affection + flirt >= 5:
        scores["crush"] += 3
    if affection + flirt >= 7:
        scores["situationship"] += 2
    if support >= 5:
        scores["close-friend"] += 3
    if support >= 2 and disclosure >= 2:
        scores["close-friend"] += 4
    if support >= 8 and affection <= 2:
        scores["close-friend"] += 2
    if logistics >= 5 and support <= 2:
        scores["coworker"] += 2
    if conflict >= 3 and repair >= 2:
        scores["situationship"] += 1
        scores["ex"] += 1

    if not scores:
        scores["friend"] = 1

    if scores["family-like"] == 0 and support >= 6 and any(hint in lowered_label for hint in ("姐", "哥", "姨", "叔")):
        scores["family-like"] += 6

    if scores["close-friend"] == 0 and support >= 4 and logistics <= 2:
        scores["close-friend"] += 2

    if all(value == 0 for value in scores.values()):
        scores["friend"] = 1

    top = scores.most_common(2)
    winner, score = top[0]
    second_score = top[1][1] if len(top) > 1 else 0

    if winner == "crush" and scores["situationship"] >= score - 1:
        winner = "crush / situationship"
    elif winner == "close-friend" and affection + flirt >= 3:
        winner = "close-friend with romantic residue"
    elif winner == "friend" and support >= 4:
        winner = "close-friend"

    if affection + flirt:
        reasons.append("出现亲密或调情用语；需要结合语境确认其含义")
    if support:
        reasons.append("对话出现安抚或支持用语；不据此断言双方互相支持")
    if conflict and repair:
        reasons.append("出现过摩擦，同时也有修复动作")
    if logistics >= 5:
        reasons.append("事务或日程型沟通占比不低")
    if keyword_hits(lowered_label, KINSHIP_HINTS):
        reasons.append("联系人名称本身带亲属提示")

    if not reasons:
        reasons.append("从现有记录看，更像稳定但信息量有限的普通关系")

    return winner, confidence_label(score, score - second_score), reasons[:3], scores


def recommend_role(relation_guess: str) -> str:
    if relation_guess.startswith("family-like"):
        return "family-like"
    if relation_guess.startswith("close-friend"):
        return "close-friend"
    if relation_guess.startswith("coworker") or relation_guess.startswith("mentor"):
        return "co-thinker"
    if "crush" in relation_guess or "situationship" in relation_guess or relation_guess == "ex":
        return "romantic"
    return "confidant"


def density_label(self_messages: list[Message]) -> str:
    if not self_messages:
        return "measured"
    avg_len = mean(len(message.content) for message in self_messages)
    if avg_len < 10:
        return "sparse"
    if avg_len < 26:
        return "measured"
    if avg_len < 60:
        return "lively"
    return "long-message"


def progression_label(affection_hits: int, total_messages: int) -> str:
    if affection_hits >= 8 and total_messages >= 40:
        return "soft-but-forward"
    return "gradual"


def conflict_label(conflict_hits: int, repair_hits: int) -> str:
    if conflict_hits >= 3 and repair_hits >= 1:
        return "allow-disagreement-but-repair"
    if conflict_hits >= 3 and repair_hits == 0:
        return "avoid-needless-escalation"
    return "avoid-unnecessary-conflict"


def topic_clues(messages: list[Message]) -> dict[str, list[str]]:
    clues: dict[str, list[str]] = {}
    for topic, keywords in TOPIC_KEYWORDS.items():
        hits: list[str] = []
        for message in messages:
            if keyword_hits(message.content, keywords):
                hits.append(excerpt(message.content))
            if len(hits) >= 2:
                break
        if hits:
            clues[topic] = hits
    return clues


def pattern_bullets(
    *,
    self_messages: list[Message],
    other_messages: list[Message],
    support_hits: int,
    disclosure_hits: int,
    conflict_hits: int,
    repair_hits: int,
    logistics_hits: int,
) -> list[str]:
    bullets: list[str] = []
    if disclosure_hits >= 3:
        bullets.append("已识别用户发言中出现情绪或状态自述；这只描述当前样本。")
    if support_hits >= 3:
        bullets.append("对话中出现安抚或照顾用语，仍需区分是谁在支持谁。")
    if logistics_hits >= 4 and support_hits <= 2:
        bullets.append("沟通更偏事务 / 日程协调，不完全像高亲密关系。")
    if conflict_hits >= 2 and repair_hits >= 1:
        bullets.append("关系里允许摩擦，但修复动作也比较重要。")
    if len(self_messages) >= 3 and len(other_messages) >= 3:
        self_avg = mean(len(message.content) for message in self_messages)
        other_avg = mean(len(message.content) for message in other_messages)
        if self_avg < other_avg * 0.75:
            bullets.append("当前样本中，已识别用户发言平均较短；不能据此判断是否喜欢追问。")
        elif self_avg > other_avg * 1.25:
            bullets.append("当前样本中，已识别用户发言平均较长；先阅读原文再决定镜像回复长度。")
    if not bullets:
        bullets.append("这段记录目前更适合作为风格补样，而不是单独决定镜像设定。")
    return bullets[:4]


def render_report(
    bundles: list[TranscriptBundle],
    self_aliases: set[str],
    generated_at: str,
) -> str:
    lines = [
        "# Mirror Profile Report",
        "",
        f"- Generated At: {generated_at}",
        f"- Transcript Count: {len(bundles)}",
        "- Positioning: heuristic report for faster mirror building, not ground truth",
        "",
        "Use this report as a middle layer between raw transcripts and final mirror writing.",
        "",
    ]

    for index, bundle in enumerate(bundles, start=1):
        self_messages = [message for message in bundle.messages if lower_text(message.sender) in self_aliases]
        other_messages = [message for message in bundle.messages if lower_text(message.sender) not in self_aliases]
        observed_messages = self_messages

        relation_guess, relation_confidence, relation_reasons, _ = choose_relation(bundle.messages, bundle.label)
        support_hits = sum(keyword_hits(message.content, SUPPORT_WORDS) for message in bundle.messages)
        disclosure_hits = sum(keyword_hits(message.content, SELF_DISCLOSURE_WORDS) for message in observed_messages)
        conflict_hits = sum(keyword_hits(message.content, CONFLICT_WORDS) for message in bundle.messages)
        repair_hits = sum(keyword_hits(message.content, REPAIR_WORDS) for message in bundle.messages)
        affection_hits = sum(keyword_hits(message.content, AFFECTION_WORDS + FLIRT_WORDS) for message in bundle.messages)
        logistics_hits = sum(keyword_hits(message.content, LOGISTICS_WORDS) for message in bundle.messages)
        clues = topic_clues(observed_messages)
        first_ts = min((message.timestamp for message in bundle.messages if message.timestamp), default=None)
        last_ts = max((message.timestamp for message in bundle.messages if message.timestamp), default=None)

        lines.extend(
            [
                f"## Profile {index}: {bundle.label}",
                "",
                f"- Source: {bundle.source_hint}",
                f"- File: {bundle.source_path.name}",
                f"- Message Count: {len(bundle.messages)}",
                f"- Identified User Messages: {len(self_messages)}",
                "- Attribution: only identified user messages support user-pattern and topic clues; relationship clues describe the conversation, not verified identity or preferences",
                f"- Time Span: {(first_ts.strftime('%Y-%m-%d') if first_ts else 'unknown')} -> {(last_ts.strftime('%Y-%m-%d') if last_ts else 'unknown')}",
                f"- Relation Guess: {relation_guess} ({relation_confidence})",
                "",
                "### Why This Guess",
                "",
            ]
        )
        for reason in relation_reasons:
            lines.append(f"- {reason}")
        lines.extend(["", "### User Pattern Clues", ""])
        if not self_messages:
            lines.append("- 未识别到用户发言；请用 --self-name 指定导出中的用户名称。不会把其他人的话当作用户特征。")
        for bullet in pattern_bullets(
            self_messages=self_messages,
            other_messages=other_messages,
            support_hits=support_hits,
            disclosure_hits=disclosure_hits,
            conflict_hits=conflict_hits,
            repair_hits=repair_hits,
            logistics_hits=logistics_hits,
        ) if self_messages else []:
            lines.append(f"- {bullet}")

        lines.extend(["", "### Suggested Mirror Settings", ""])
        lines.append(f"- companion_role: {recommend_role(relation_guess) if self_messages else 'unconfirmed'} (candidate only; confirm with user)")
        lines.append("- core_alignment: unconfirmed; transcripts do not establish consent or core values")
        lines.append(f"- reply_density: {density_label(self_messages) if self_messages else 'unconfirmed'}")
        lines.append("- progression_style: gradual; intimacy requires explicit user preference")
        lines.append(f"- conflict_style: {conflict_label(conflict_hits, repair_hits) if self_messages else 'unconfirmed'}")
        lines.append("- note: 核心价值观和雷区以用户明确提供的设定为准，不从话题词或他人发言代填。")

        if clues:
            lines.extend(["", "### Topic Clues To Read Carefully", ""])
            for topic, snippets in clues.items():
                lines.append(f"- {topic}:")
                for snippet in snippets:
                    lines.append(f"  - {snippet}")
        else:
            lines.extend(["", "### Topic Clues To Read Carefully", "", "- 当前样本里的明确议题还不够多，暂时不要过度判断价值观。"])

        lines.extend(["", "### Carryover Guidance", ""])
        if disclosure_hits >= 3:
            lines.append("- 这类关系适合“先识别情绪，再追问一小步”，不要一上来给宏大结论。")
        if self_messages and density_label(self_messages) in {"sparse", "measured"}:
            lines.append("- 回复量保持克制，不要每轮都说太密。")
        if affection_hits >= 4:
            lines.append("- 对话含亲密词，不代表用户希望镜像采用浪漫关系；先确认偏好。")
        if conflict_hits >= 2:
            lines.append("- 如果发生分歧，优先修顺序：先理解，再表达不同。")
        if relation_guess.startswith("coworker"):
            lines.append("- 不要误把高频事务往来写成恋爱感。")
        if relation_guess.startswith("family-like"):
            lines.append("- 这是明显的非浪漫关系线索，生成镜像时不要带恋爱残影。")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def discover_inputs(input_values: list[str], skill_dir: Path | None) -> list[Path]:
    paths = [Path(value).expanduser().resolve() for value in input_values]
    if skill_dir:
        imports_dir = skill_dir / "knowledge" / "imports"
        if imports_dir.exists():
            paths.extend(sorted(imports_dir.glob("*.md")))
    seen: set[Path] = set()
    unique_paths: list[Path] = []
    for path in paths:
        if path not in seen and path.exists():
            seen.add(path)
            unique_paths.append(path)
    return unique_paths


def archive_report(skill_dir: Path, report_text: str) -> Path:
    analysis_dir = skill_dir / "knowledge" / "analysis"
    analysis_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
    target = analysis_dir / f"{stamp}-mirror-profile.md"
    target.write_text(report_text, encoding="utf-8")
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Profile normalized transcripts for create-shuixian.")
    parser.add_argument("--input", action="append", default=[], help="Transcript or archived import file path. Repeat for multiple files.")
    parser.add_argument("--skill-dir", help="Generated shuixian skill directory. Profiles every file under knowledge/imports.")
    parser.add_argument("--output", default="./mirror-profile.md", help="Where to write the combined profile report.")
    parser.add_argument("--self-name", action="append", default=[], help="Additional sender labels that should be treated as the user.")
    parser.add_argument("--archive-to", help="Skill directory where the report should also be copied into knowledge/analysis.")
    args = parser.parse_args()

    for value in args.input:
        if not Path(value).expanduser().is_file():
            parser.error(f"Input must be an existing file: {value}")

    skill_dir = Path(args.skill_dir).expanduser().resolve() if args.skill_dir else None
    archive_to = Path(args.archive_to).expanduser().resolve() if args.archive_to else skill_dir
    input_paths = discover_inputs(args.input, skill_dir)
    if not input_paths:
        raise SystemExit("No valid transcript inputs found. Use --input or --skill-dir.")
    output_path = Path(args.output).expanduser().resolve()
    try:
        aliases_input = output_path in input_paths or (
            output_path.exists() and any(output_path.samefile(path) for path in input_paths)
        )
    except OSError as error:
        parser.error(f"Cannot verify output preserves original inputs: {error}")
    if aliases_input:
        parser.error("Output must differ from every input file; originals are preserved.")

    if archive_to:
        analysis_dir = archive_to / "knowledge" / "analysis"
        try:
            for directory in (analysis_dir, *analysis_dir.parents):
                if directory.exists() and not directory.is_dir():
                    parser.error(
                        f"Archive destination is blocked by a file: {directory}. "
                        "Choose a directory with --archive-to and retry; no files were written."
                    )
        except OSError as error:
            parser.error(f"Cannot check archive destination {archive_to}: {error}")

    bundles: list[TranscriptBundle] = []
    try:
        for path in input_paths:
            bundles.extend(parse_input_file(path))
    except (OSError, ValueError) as error:
        parser.error(str(error))

    if not bundles:
        raise SystemExit("No transcript-like messages found in the supplied files.")

    self_aliases = {lower_text(alias) for alias in DEFAULT_SELF_ALIASES}
    self_aliases.update(lower_text(alias) for alias in args.self_name if normalize_text(alias))

    generated_at = datetime.now(timezone.utc).isoformat()
    report_text = render_report(bundles, self_aliases, generated_at)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_text, encoding="utf-8")

    print(f"Profiled {len(bundles)} transcript bundle(s).")
    identified_count = sum(
        lower_text(message.sender) in self_aliases
        for bundle in bundles for message in bundle.messages
    )
    message_count = sum(len(bundle.messages) for bundle in bundles)
    print(f"Identified user messages: {identified_count}/{message_count}")
    if not identified_count:
        print(
            "Warning: No user sender labels matched. User settings remain unconfirmed. "
            "Check sender labels in the transcript and retry with --self-name YOUR_SENDER_LABEL "
            "(repeat for multiple names).",
            file=sys.stderr,
        )
    print(f"Wrote mirror profile report to {output_path}")

    if archive_to:
        archived_path = archive_report(archive_to, report_text)
        print(f"Archived mirror profile report to {archived_path}")


if __name__ == "__main__":
    for cli_stream in (sys.stdout, sys.stderr):
        if hasattr(cli_stream, "reconfigure"):
            cli_stream.reconfigure(encoding="utf-8")
    main()
