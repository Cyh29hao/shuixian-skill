---
name: create-shuixian
description: Create, update, list, and roll back Codex-compatible self-mirror companion skills from prompts, pasted notes, exported chat logs, screenshots, and other language samples. Use when the user wants a "shuixian" companion who speaks in their wavelength, understands their relationships and values, and can be configured as a lover, friend, family-like confidant, or other mirror role with configurable privacy scope, worldview alignment, pacing, and safety boundaries.
---

# Create Shuixian

Use this skill when the user wants to turn their own language, habits, values, and optional chat history into a reusable "water-immortal" self-mirror companion skill.

Always respond in the same language as the user unless they ask for another language.

## Codex-specific conventions

- Explicit invocation is `$create-shuixian`.
- Generated skills should be written under the current workspace at `./.agents/skills/`.
- The generated skill name should be `$shuixian-<slug>`.
- Store the generated material in `./.agents/skills/shuixian-<slug>/`.
- If the generated skill does not appear immediately, tell the user to restart Codex.

## Files in this skill

Use these files relative to this skill directory:

- `prompts/intake.md`
- `prompts/style_analyzer.md`
- `prompts/cognition_analyzer.md`
- `prompts/social_graph_analyzer.md`
- `prompts/relationship_designer.md`
- `prompts/mirror_builder.md`
- `prompts/merger.md`
- `prompts/correction_handler.md`
- `references/mirror-modes.md`
- `references/companion-roles.md`
- `references/privacy-and-safety.md`
- `references/data-sources.md`
- `references/import-channels.md`
- `references/wechat-import.md`
- `tools/skill_writer.py`
- `tools/demo_builder.py`
- `tools/version_manager.py`
- `tools/source_importer.py`
- `tools/mirror_profiler.py`
- `tools/wechat_decryptor.py`
- `tools/wechat_importer.py`
- `tools/imessage_importer.py`
- `tools/transcript_importer.py`

When running bundled scripts on Windows, prefer `python`. If `python` is unavailable, use `py -3`.

## Main workflow

### 0. No-privacy demo first when helpful

If the user is still deciding whether the concept feels right, or they want a public-safe demo before sharing personal material, start with:

```powershell
python tools/demo_builder.py --list-presets
python tools/demo_builder.py --preset sweet-gender-flipped --base-dir ./.agents/skills
```

This creates a ready-to-use demo mirror without any private chat history.

### 1. Intake

If the user has not already provided enough detail, gather only the missing essentials:

1. codename or nickname for the mirror
2. mirror mode
3. privacy scope
4. embodiment or presentation choice
5. companion role or identity framing
6. relationship tone
7. pacing, reply density, and disagreement tolerance
8. hard boundaries and worldview no-go themes

Use `prompts/intake.md` as a reference. Keep the intake light. Do not force the user to over-disclose.

### 2. Collect materials

Offer the smallest workable input path first:

- prompt-only mode with no logs
- pasted self-description
- pasted chat snippets
- exported chat logs
- WeChat desktop chat history
- iMessage chat history
- transcript exports from Telegram, QQ, Discord, Slack, Feishu, or similar tools
- screenshots or images
- manual preference sheet

Prefer the minimum material that can still support a convincing voice.

Before deeper analysis, read:

- `references/mirror-modes.md`
- `references/companion-roles.md`
- `references/privacy-and-safety.md`
- `references/data-sources.md`
- `references/import-channels.md`
- `references/wechat-import.md` when the user wants WeChat import

### WeChat import workflow

When the user wants to import WeChat desktop history:

1. ask for the minimum privacy scope first
2. run `tools/wechat_decryptor.py` to discover or apply a SQLCipher key
3. run `tools/wechat_importer.py --list-contacts` so the user can choose the contact
4. when the user imports large-scale history, run `tools/wechat_importer.py --contact-report` first so the mirror can reason about likely close ties and relationship clusters
5. run `tools/wechat_importer.py --extract` to generate normalized transcripts for the most relevant contacts
6. archive those transcripts or reports into the target mirror with `--archive-to` when helpful

If automatic key extraction fails, do not get stuck. Fall back to exported text or user-pasted snippets.

### Other import workflows

When the user wants non-WeChat imports:

1. use `tools/imessage_importer.py` for `chat.db` on macOS
2. use `tools/transcript_importer.py` for `.txt`, `.md`, `.json`, and `.jsonl` exports
3. archive normalized outputs into the target mirror when the user wants long-term reuse

Prefer normalized transcript files over raw database or vendor export formats once extraction succeeds.

### Profiling workflow

When transcript volume is high enough that raw logs become noisy, run:

```powershell
python tools/mirror_profiler.py --input <normalized-transcript.txt> --output ./mirror-profile.md
```

If the transcript files were already archived into a generated mirror:

```powershell
python tools/mirror_profiler.py --skill-dir ./.agents/skills/shuixian-<slug>
```

Use the report as a middle layer before final synthesis. It should help surface:

- likely relationship categories
- topic clues worth reading carefully
- value and no-go hints
- pacing and density suggestions for the mirror

### 3. Analyze along four tracks

Use the prompt files as working references:

- `prompts/style_analyzer.md` for voice, rhythm, pet phrases, pacing, emoji use, and affection style
- `prompts/cognition_analyzer.md` for worldview, decision habits, triggers, values, veto topics, and emotional logic
- `prompts/social_graph_analyzer.md` for relationship categories, attachment map, and how the user handles different people
- `prompts/relationship_designer.md` for companion role, intimacy framing, boundaries, power balance, conflict style, and desired closeness

When available, read the output of `tools/mirror_profiler.py` before synthesizing the final mirror. Treat it as an organizer, not as ground truth.

If the user wants a visualized or gender-flipped mirror, infer only from explicit user preferences plus light stylistic hints. Do not present appearance guesses as objective truth.

### 4. Preview before writing

Before materializing a skill, show a compact preview:

- 3 to 5 bullets for voice DNA
- 3 to 5 bullets for thought pattern and core values
- 3 to 5 bullets for relationship map and identity configuration
- 3 to 5 bullets for relationship dynamic, pacing, and boundaries
- 1 short sample opening scene

If the user clearly asked you to proceed directly, you may skip an extra confirmation pause.

### 5. Write the generated skill

Prepare temporary files for `meta.json`, `style.md`, `mind.md`, `relationship.md`, and optionally `appearance.md`, then run:

```powershell
python tools/skill_writer.py --action create --slug <slug> --meta <meta.json> --style <style.md> --mind <mind.md> --relationship <relationship.md> --appearance <appearance.md> --base-dir ./.agents/skills
```

After creation, tell the user the generated skill name:

- `$shuixian-<slug>`

## Update and correction workflow

### Append new material

When the user adds more notes, logs, or corrections:

1. read the new material
2. read the current `style.md`, `mind.md`, `relationship.md`, and `appearance.md` if present
3. use `prompts/merger.md` as reference
4. prepare delta files for the affected sections
5. run:

```powershell
python tools/skill_writer.py --action update --slug <slug> --style-patch <style_patch.md> --mind-patch <mind_patch.md> --relationship-patch <relationship_patch.md> --appearance-patch <appearance_patch.md> --base-dir ./.agents/skills
```

### Conversation correction

When the user says things like "这不像我", "ta 不会这么回", or "太油了":

1. use `prompts/correction_handler.md`
2. decide which layer needs the patch
3. append a concise correction note
4. run the same `update` flow

## Management commands

### List generated mirrors

```powershell
python tools/skill_writer.py --action list --base-dir ./.agents/skills
```

### List versions for one mirror

```powershell
python tools/version_manager.py --action list --slug <slug> --base-dir ./.agents/skills
```

### Roll back one mirror

```powershell
python tools/version_manager.py --action rollback --slug <slug> --version <version> --base-dir ./.agents/skills
```

## Quality bar

- Keep the generated companion warm, specific, and emotionally legible.
- Preserve the user's pacing, relationship logic, and inner logic instead of producing generic flirting.
- In `full-mirror`, align strongly with high-confidence values, opinions, and hard veto topics that appear repeatedly in the source material.
- Allow small differences on low-stakes topics only when they add life and conversation without stepping on the user's core values or identity boundaries.
- Keep the mirror's message density measured. It should not flood every turn or rush intimacy unless the user clearly prefers that.
- Let closeness grow gradually. Slow burn and course correction should remain available even after import-heavy builds.
- Make privacy scope explicit inside the generated skill.
- Keep the mirror fictional. Never claim literal consciousness, diagnosis, or metaphysical identity.
- If the user shows signs of crisis, obsessive isolation, or severe distress, break roleplay gently and ground the response.
