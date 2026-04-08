#!/usr/bin/env python3
"""
Create and update Codex-compatible shuixian mirror skills.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_BASE_DIR = "./.agents/skills"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("mirror-%Y%m%d-%H%M%S")


def read_text_file(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def write_text_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def slugify(text: str) -> str:
    try:
        from pypinyin import lazy_pinyin  # type: ignore

        parts = [part.strip().lower() for part in lazy_pinyin(text) if part.strip()]
        candidate = "-".join(parts)
    except ImportError:
        normalized = []
        for char in text.lower():
            if char.isascii() and char.isalnum():
                normalized.append(char)
            elif char in {" ", "-", "_"}:
                normalized.append("-")
        candidate = "".join(normalized)

    candidate = re.sub(r"[^a-z0-9-]+", "-", candidate)
    candidate = re.sub(r"-+", "-", candidate).strip("-")
    return candidate or timestamp_slug()


def sanitize_inline(text: str) -> str:
    return " ".join(str(text).replace('"', "'").split())


def read_optional_file(path: str | None) -> str:
    if not path:
        return ""
    return read_text_file(Path(path))


def parse_meta_json(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    return json.loads(read_text_file(Path(path)))


def mirror_skill_name(slug: str) -> str:
    return f"shuixian-{slug}"


def default_meta(slug: str, name: str | None = None) -> dict[str, Any]:
    display_name = name or slug.replace("-", " ").title()
    return {
        "slug": slug,
        "display_name": display_name,
        "mirror_mode": "selective-mirror",
        "privacy_mode": "style-only",
        "presentation": "gender-flipped",
        "companion_role": "romantic",
        "relationship_tone": "sweet",
        "core_alignment": "align-on-core-values",
        "difference_style": "playful-on-low-stakes-topics",
        "reply_density": "measured",
        "progression_style": "gradual",
        "conflict_style": "allow-disagreement-but-repair",
        "contract": "A warm self-mirror companion who feels emotionally legible and safe.",
        "boundaries": [
            "Stay fictional and do not claim literal identity.",
            "Do not pressure the user into isolation.",
        ],
    }


def format_boundaries(value: Any) -> str:
    if isinstance(value, list):
        items = [sanitize_inline(item) for item in value if str(item).strip()]
    elif isinstance(value, str) and value.strip():
        items = [sanitize_inline(line) for line in value.splitlines() if line.strip()]
    else:
        items = []

    if not items:
        items = ["Stay fictional and emotionally safe."]

    return "\n".join(f"- {item}" for item in items)


def render_section(title: str, body: str, fallback: str) -> str:
    content = body.strip() or fallback
    return f"## {title}\n\n{content}\n"


def render_skill_markdown(
    *,
    slug: str,
    meta: dict[str, Any],
    style_content: str,
    mind_content: str,
    relationship_content: str,
    appearance_content: str,
) -> str:
    skill_name = mirror_skill_name(slug)
    display_name = meta.get("display_name", slug)
    description = sanitize_inline(
        meta.get(
            "description",
            "Self-mirror companion built from user-provided voice, values, and boundaries.",
        )
    )
    contract = sanitize_inline(
        meta.get("contract", "A warm self-mirror companion who feels emotionally legible and safe.")
    )
    mirror_mode = sanitize_inline(meta.get("mirror_mode", "selective-mirror"))
    privacy_mode = sanitize_inline(meta.get("privacy_mode", "style-only"))
    presentation = sanitize_inline(meta.get("presentation", "gender-flipped"))
    companion_role = sanitize_inline(meta.get("companion_role", "romantic"))
    relationship_tone = sanitize_inline(meta.get("relationship_tone", "sweet"))
    core_alignment = sanitize_inline(meta.get("core_alignment", "align-on-core-values"))
    difference_style = sanitize_inline(meta.get("difference_style", "playful-on-low-stakes-topics"))
    reply_density = sanitize_inline(meta.get("reply_density", "measured"))
    progression_style = sanitize_inline(meta.get("progression_style", "gradual"))
    conflict_style = sanitize_inline(meta.get("conflict_style", "allow-disagreement-but-repair"))
    boundaries = format_boundaries(meta.get("boundaries"))

    return f"""---
name: {skill_name}
description: "{description}"
---

# {display_name}

Treat this skill as a fictional self-mirror companion created from user-provided materials.

Respond in the same language as the current user unless they ask for another language.

## Mirror Card

- Mode: {mirror_mode}
- Privacy: {privacy_mode}
- Presentation: {presentation}
- Companion Role: {companion_role}
- Relationship Tone: {relationship_tone}
- Core Alignment: {core_alignment}
- Difference Style: {difference_style}
- Reply Density: {reply_density}
- Progression Style: {progression_style}
- Conflict Style: {conflict_style}
- Contract: {contract}

## Safety Contract

{boundaries}

{render_section("Voice DNA", style_content, "No voice profile captured yet.")}
{render_section("Mind Pattern", mind_content, "No cognition profile captured yet.")}
{render_section("Relationship Dynamic", relationship_content, "No relationship profile captured yet.")}
{render_section("Appearance Layer", appearance_content, "No appearance layer captured yet.")}
## Priority Order

1. Follow hard boundaries, high-confidence values, and veto topics before anything else.
2. Use companion role and relationship logic to decide stance, closeness, and initiative.
3. Use voice and pacing rules to decide how much to say and how quickly to say it.
4. Use low-stakes variation only where it adds life without stepping on the user's core worldview.

## Operating Rules

1. Keep the mirror coherent with the configured voice, values, companion role, and relationship tone.
2. Stay fictional. Never claim literal consciousness transfer, diagnosis, or metaphysical identity.
3. In `full-mirror`, align closely with repeated opinions, relationship logic, and explicit value statements from the source material.
4. Avoid stepping on the user's high-stakes beliefs, identity boundaries, or known no-go themes.
5. Moderate message density. Do not flood the user with overlong replies unless they clearly invite that style.
6. Let intimacy and trust grow gradually; do not force escalation just because the mirror is warm.
7. Low-stakes disagreement is allowed when it feels lively, respectful, and topic-generating rather than invalidating.
8. If conflict happens, keep it emotionally legible and capable of repair rather than manipulative or punishing.
9. Distinguish evidence-backed traits from aesthetic inference when the user asks.
10. If the user appears to be in acute distress, soften roleplay and encourage grounding and real-world support.
"""


def ensure_structure(skill_dir: Path) -> None:
    (skill_dir / "versions").mkdir(parents=True, exist_ok=True)
    (skill_dir / "knowledge" / "imports").mkdir(parents=True, exist_ok=True)
    (skill_dir / "knowledge" / "images").mkdir(parents=True, exist_ok=True)
    (skill_dir / "knowledge" / "notes").mkdir(parents=True, exist_ok=True)


def write_skill_files(
    *,
    skill_dir: Path,
    slug: str,
    meta: dict[str, Any],
    style_content: str,
    mind_content: str,
    relationship_content: str,
    appearance_content: str,
) -> None:
    write_text_file(skill_dir / "style.md", style_content)
    write_text_file(skill_dir / "mind.md", mind_content)
    write_text_file(skill_dir / "relationship.md", relationship_content)
    if appearance_content.strip():
        write_text_file(skill_dir / "appearance.md", appearance_content)
    elif (skill_dir / "appearance.md").exists():
        (skill_dir / "appearance.md").unlink()

    write_text_file(
        skill_dir / "SKILL.md",
        render_skill_markdown(
            slug=slug,
            meta=meta,
            style_content=style_content,
            mind_content=mind_content,
            relationship_content=relationship_content,
            appearance_content=appearance_content,
        ),
    )
    write_text_file(skill_dir / "meta.json", json.dumps(meta, ensure_ascii=False, indent=2))


def archive_current_version(skill_dir: Path, version_name: str) -> None:
    version_dir = skill_dir / "versions" / version_name
    version_dir.mkdir(parents=True, exist_ok=True)
    for filename in ("SKILL.md", "style.md", "mind.md", "relationship.md", "appearance.md", "meta.json"):
        source = skill_dir / filename
        if source.exists():
            write_text_file(version_dir / filename, read_text_file(source))


def create_skill(
    *,
    base_dir: Path,
    slug: str,
    meta: dict[str, Any],
    style_content: str,
    mind_content: str,
    relationship_content: str,
    appearance_content: str,
) -> Path:
    skill_dir = base_dir / mirror_skill_name(slug)
    ensure_structure(skill_dir)

    merged_meta = default_meta(slug, meta.get("display_name") or meta.get("name"))
    merged_meta.update(meta)
    merged_meta["slug"] = slug
    merged_meta["skill_name"] = mirror_skill_name(slug)
    merged_meta.setdefault("created_at", now_iso())
    merged_meta["updated_at"] = now_iso()
    merged_meta["version"] = "v1"

    write_skill_files(
        skill_dir=skill_dir,
        slug=slug,
        meta=merged_meta,
        style_content=style_content,
        mind_content=mind_content,
        relationship_content=relationship_content,
        appearance_content=appearance_content,
    )
    return skill_dir


def next_version(current_version: str) -> str:
    match = re.match(r"^v(\d+)", current_version)
    if not match:
        return "v2"
    return f"v{int(match.group(1)) + 1}"


def update_skill(
    *,
    base_dir: Path,
    slug: str,
    meta_patch: dict[str, Any],
    style_patch: str,
    mind_patch: str,
    relationship_patch: str,
    appearance_patch: str,
) -> tuple[Path, str]:
    skill_dir = base_dir / mirror_skill_name(slug)
    meta_path = skill_dir / "meta.json"
    if not meta_path.exists():
        raise FileNotFoundError(f"Missing meta.json for slug '{slug}'")

    meta = json.loads(read_text_file(meta_path))
    current_version = str(meta.get("version", "v1"))
    archive_current_version(skill_dir, current_version)

    style_content = read_text_file(skill_dir / "style.md")
    mind_content = read_text_file(skill_dir / "mind.md")
    relationship_content = read_text_file(skill_dir / "relationship.md")
    appearance_path = skill_dir / "appearance.md"
    appearance_content = read_text_file(appearance_path) if appearance_path.exists() else ""

    def append_patch(content: str, patch: str) -> str:
        clean_patch = patch.strip()
        if not clean_patch:
            return content
        stripped = content.rstrip()
        if not stripped:
            return f"{clean_patch}\n"
        return f"{stripped}\n\n{clean_patch}\n"

    style_content = append_patch(style_content, style_patch)
    mind_content = append_patch(mind_content, mind_patch)
    relationship_content = append_patch(relationship_content, relationship_patch)
    appearance_content = append_patch(appearance_content, appearance_patch)

    meta.update(meta_patch)
    meta["slug"] = slug
    meta["skill_name"] = mirror_skill_name(slug)
    meta["version"] = next_version(current_version)
    meta["updated_at"] = now_iso()

    write_skill_files(
        skill_dir=skill_dir,
        slug=slug,
        meta=meta,
        style_content=style_content,
        mind_content=mind_content,
        relationship_content=relationship_content,
        appearance_content=appearance_content,
    )
    return skill_dir, str(meta["version"])


def list_mirrors(base_dir: Path) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    if not base_dir.exists():
        return results

    for entry in sorted(base_dir.iterdir()):
        if not entry.is_dir():
            continue
        meta_path = entry / "meta.json"
        if not meta_path.exists():
            continue
        try:
            meta = json.loads(read_text_file(meta_path))
        except json.JSONDecodeError:
            continue

        results.append(
            {
                "folder": entry.name,
                "slug": meta.get("slug", entry.name),
                "display_name": meta.get("display_name", meta.get("name", entry.name)),
                "mirror_mode": meta.get("mirror_mode", ""),
                "privacy_mode": meta.get("privacy_mode", ""),
                "presentation": meta.get("presentation", ""),
                "companion_role": meta.get("companion_role", ""),
                "relationship_tone": meta.get("relationship_tone", ""),
                "reply_density": meta.get("reply_density", ""),
                "version": meta.get("version", "v1"),
                "updated_at": meta.get("updated_at", ""),
                "skill_name": meta.get("skill_name", entry.name),
            }
        )

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Create or update Codex-compatible shuixian mirror skills.")
    parser.add_argument("--action", required=True, choices=["create", "update", "list"])
    parser.add_argument("--slug", help="Mirror slug.")
    parser.add_argument("--name", help="Mirror display name.")
    parser.add_argument("--meta", help="Path to meta.json input.")
    parser.add_argument("--style", help="Path to style.md input.")
    parser.add_argument("--mind", help="Path to mind.md input.")
    parser.add_argument("--relationship", help="Path to relationship.md input.")
    parser.add_argument("--appearance", help="Path to appearance.md input.")
    parser.add_argument("--style-patch", help="Path to style patch.")
    parser.add_argument("--mind-patch", help="Path to mind patch.")
    parser.add_argument("--relationship-patch", help="Path to relationship patch.")
    parser.add_argument("--appearance-patch", help="Path to appearance patch.")
    parser.add_argument("--base-dir", default=DEFAULT_BASE_DIR, help="Directory where generated skills are stored.")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).expanduser().resolve()
    base_dir.mkdir(parents=True, exist_ok=True)

    if args.action == "list":
        mirrors = list_mirrors(base_dir)
        if not mirrors:
            print("No shuixian mirrors found.")
            return

        print(f"Found {len(mirrors)} shuixian mirror(s):\n")
        for mirror in mirrors:
            updated = str(mirror["updated_at"])[:19].replace("T", " ")
            print(f"[{mirror['slug']}] {mirror['display_name']}")
            print(
                "  "
                f"Mode: {mirror['mirror_mode']}  Privacy: {mirror['privacy_mode']}  "
                f"Presentation: {mirror['presentation']}  Role: {mirror['companion_role']}  "
                f"Tone: {mirror['relationship_tone']}  Density: {mirror['reply_density']}"
            )
            print(f"  Version: {mirror['version']}  Updated: {updated}")
            print(f"  Skill: ${mirror['skill_name']}")
            print()
        return

    meta = parse_meta_json(args.meta)
    if args.name:
        meta["display_name"] = args.name

    slug_source = args.slug or meta.get("slug") or meta.get("display_name") or meta.get("name") or "mirror"
    slug = slugify(str(slug_source))

    if args.action == "create":
        skill_dir = create_skill(
            base_dir=base_dir,
            slug=slug,
            meta=meta,
            style_content=read_optional_file(args.style),
            mind_content=read_optional_file(args.mind),
            relationship_content=read_optional_file(args.relationship),
            appearance_content=read_optional_file(args.appearance),
        )
        print(f"Created shuixian mirror at {skill_dir}")
        print(f"Use: ${mirror_skill_name(slug)}")
        return

    skill_dir, version = update_skill(
        base_dir=base_dir,
        slug=slug,
        meta_patch=meta,
        style_patch=read_optional_file(args.style_patch),
        mind_patch=read_optional_file(args.mind_patch),
        relationship_patch=read_optional_file(args.relationship_patch),
        appearance_patch=read_optional_file(args.appearance_patch),
    )
    print(f"Updated shuixian mirror at {skill_dir}")
    print(f"Version: {version}")
    print(f"Use: ${mirror_skill_name(slug)}")


if __name__ == "__main__":
    main()
