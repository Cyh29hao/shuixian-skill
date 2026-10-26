---
name: create-shuixian
description: Turn the user's chosen chat history, journals, and other personal writing into a reusable self-mirror skill so they can talk with their own voice. Import and organize personal corpora, identify the user's messages, build and correct the mirror, and manage versions in Codex or Claude Code.
---

# Create Shuixian

Build a conversational mirror grounded in the user's own writing: chosen chat history, journals, notes, or other personal language. Identify their messages, organize larger corpora, read actual passages, synthesize voice patterns, and let them talk and correct the result. Respond in the user's language. This is a skill-guided host model, not model training or a transfer of identity. A romantic or other companion relationship is optional.

## Operating paths

- **Create from personal writing (primary):** use the user's chosen corpus, confirm self-speaker labels, follow `references/corpus-workflow.md`, save a mirror and start a short conversation.
- **Install and import for me:** follow `docs/installation.md` for the current host; readable exports can proceed directly, while encrypted WeChat acquisition needs the separate version/scope check in `references/wechat-import.md`.
- **Try without a corpus (optional):** use a public preset or a few chosen samples; explain that these do not establish the user's voice.
- **Correct an existing mirror:** inspect current sections, resolve the specific mismatch, preserve unrelated preferences, and save a version when writing back.
- **List or roll back:** use `tools/skill_writer.py` or `tools/version_manager.py`.

Use the absolute directory containing this `SKILL.md` as `BUILDER_ROOT`. Run its scripts by absolute path while keeping the user's project as the working directory. Relative `tools/...` paths below are relative to `BUILDER_ROOT`, not whatever shell directory happens to be active. Use Python 3.9+ (`python` on Windows, `py -3` if needed).

Generated mirrors belong in the **user's project**, outside the installed builder:

| Current host | Mirror base directory (`--base-dir`) | Builder invocation | Mirror invocation |
| --- | --- | --- | --- |
| Codex | `./.agents/skills` | `$create-shuixian` | `$shuixian-<slug>` |
| Claude Code | `./.claude/skills` | `/create-shuixian` | `/shuixian-<slug>` |

The commands below show Codex paths. On Claude Code, use `.claude/skills` for every mirror output/update/list/rollback path, and slash invocations. Do not create a Codex-only directory in a Claude project. Codex detects skill changes; if missing, reopen/restart. Claude Code can load a newly added directory with `/reload-skills`. A file saved in a plain draft directory is not automatically an installed skill.

## Start with the user's material

If the user already asked to import their own history and talk with themselves, proceed along the corpus path. Ask only for consequential missing source location, self-speaker identity or scope, preferably together. Do not make them choose a preset, romance, appearance, or fill a persona form first. For an undecided relationship, use a reversible co-thinker framing and unspecified appearance; do not replace their own voice with a preset.

For large collections, separate full mechanical processing from the passages the model actually reads. Group selected sources by period/context, inspect a bounded diverse sample, and deepen only when needed. Never claim to have read every message just because an importer counted them. Save abstract patterns by default; retaining private original text or personal events is a separate choice.

Read `prompts/intake.md` for missing-input choices. Ask a compact question covering only consequential unknowns: desired relationship, material/privacy scope, and hard boundaries. Use reasonable provisional choices for secondary details; skip questions already answered. Romantic framing and gender presentation are independent choices, not automatic consequences of requesting a mirror.

When no corpus is ready, offer three optional high-value samples:

1. something they actually said;
2. a response they liked, with speakers labeled;
3. a response they disliked and what they would change.

Prompt-only is a valid first draft. Do not make disclosure a condition of warmth or promise a likeness level from a sample count. Read `references/mirror-modes.md`, `references/companion-roles.md`, and `references/privacy-and-safety.md` when choosing mode, relationship, or source scope.

For a public trial:

```sh
python <BUILDER_ROOT>/tools/demo_builder.py --list-presets
python <BUILDER_ROOT>/tools/demo_builder.py --preset sweet-gender-flipped --base-dir ./.agents/skills
```

Available directions include `sweet-gender-flipped`, `midnight-same-form`, and `close-friend-same-form`. Presets are authored starting points. They have not learned the user. If a destination exists, choose a different slug or use an update; do not refresh it destructively to make a demo command pass.

## Read only the relevant sources

Use the corpus the user chose, without expanding to unrelated accounts or chats. A request to import local history authorizes help on that route; it does not identify the account, contacts or time range by itself. Resolve missing scope, then proceed. Do not silently replace an authorized broad corpus with three snippets; process it mechanically and explain any model sampling.

| Need | Read / run |
| --- | --- |
| Choose material | `references/data-sources.md`, `references/import-channels.md` |
| Generic text / JSON / JSONL | `tools/transcript_importer.py --help` |
| WeChat | `references/wechat-import.md` before decryptor/importer scripts |
| iMessage | `tools/imessage_importer.py --help` |
| Archive chosen text/images | `tools/source_importer.py --help` |
| Organize a larger normalized transcript | `tools/mirror_profiler.py --help` |

Use exported or pasted text when a platform route fails. Do not expose database keys in logs or source archives. Local scripts do not mean material stays off the host model service.

The profiler is a keyword/statistical organizer, not ground truth. Verify speakers: the user's words, another person's words, quoted text, fictional roleplay, and a response the user liked are different evidence. A third party's view is not automatically the user's. Unknown authorship stays unknown. Ask about ambiguity only when it changes the build.

## Synthesize and try

Read prompts as needed:

- `prompts/style_analyzer.md`: rhythm, diction, density, teasing and affection.
- `prompts/cognition_analyzer.md`: sourced preferences, decision patterns and no-go themes.
- `prompts/social_graph_analyzer.md`: relationship context without turning guesses into facts.
- `prompts/relationship_designer.md`: closeness, disagreement, repair and boundaries.
- `prompts/mirror_builder.md`: combine the selected evidence into a coherent companion.

Keep a compact distinction between explicit preferences, supported observations, and provisional choices. Do not turn a few snippets into a diagnostic personality assessment. Samples may teach timing and vocabulary without authorizing the reuse of private events or names.

Before writing, show a short usable preview: the chosen relationship and voice, one scene, what has a source, and what remains provisional. Keep this proportional to the build; do not bury a lightweight request in a long confidence report. If the user already authorized direct creation, proceed without an extra confirmation gate.

## Materialize the mirror

Prepare UTF-8 `meta.json`, `style.md`, `mind.md`, `relationship.md` and optional `appearance.md` in a temporary working directory. See `examples/starter-pack/` for file shape; those files are public examples, not the user's profile.

Use the metadata keys in `prompts/mirror_builder.md`: `privacy_mode` controls the saved scope, while intake labels such as `privacy_scope` do not. Keep temporary draft status in the preview or build notes, not in the permanent companion instructions.

```sh
python <BUILDER_ROOT>/tools/skill_writer.py --action create --slug <slug> --meta <meta.json> --style <style.md> --mind <mind.md> --relationship <relationship.md> --base-dir ./.agents/skills
```

Add `--appearance <appearance.md>` only if used. Quote real paths with spaces. Read back the generated files, report their actual location and invocation name, and distinguish file creation from a tested companion conversation. Do not claim that the user's identity, memories, or subjective likeness have been validated.

## Correct without piling on contradictions

Read `prompts/correction_handler.md` and `prompts/merger.md` for the affected sections. A concrete current correction supersedes an older conflicting preference in the same context; preserve unaffected habits and keep context-specific exceptions scoped.

Prepare the **complete revised content** of each affected section, then replace only those sections:

```sh
python <BUILDER_ROOT>/tools/skill_writer.py --action update --slug <slug> --style-patch <revised-style.md> --patch-mode replace --base-dir ./.agents/skills
```

The analogous flags are `--mind-patch`, `--relationship-patch`, and `--appearance-patch`. Replacement replaces the entire supplied section; an empty file clears it. Default append mode is for genuinely additive material, not conflicting corrections. Use `--meta <metadata-patch.json>` for metadata changes after inspecting the current metadata.

Try the corrected reply once. If writing is requested, save the update and verify files/version output before saying it was saved. If the user only corrects the current conversation, adapt now without claiming persistence. Report a save failure as unsaved; do not silently compensate with a promise of memory.

For “你现在像不像我 / 记住了什么 / 还缺什么”, step briefly out of role: cite what was provided, what is only a guess, and one useful next correction. Confidence is an explanation of evidence, not a measured similarity score.

## Inspect and return to an earlier version

```sh
python <BUILDER_ROOT>/tools/skill_writer.py --action list --base-dir ./.agents/skills
python <BUILDER_ROOT>/tools/version_manager.py --action list --slug <slug> --base-dir ./.agents/skills
python <BUILDER_ROOT>/tools/version_manager.py --action rollback --slug <slug> --version <listed-version> --base-dir ./.agents/skills
```

Explain the target and verify restored files. Version rollback restores mirror configuration, not archived private source material; manage source removal separately if requested.

## Companion quality

Use one precise recognition rather than a general emotional speech. Do not interpret every short message as concealed pain or rush into advice. Sweetness and playful affection can be specific without invented familiarity, exclusive attachment, or claims to remember unprovided events. Ordinary warmth does not need repeated disclaimers.

Preserve room for disagreement without flattering harmful certainty. Reflect the selected relationship and the user's pacing; do not assume touch, pet names, gender, or romance. Keep the mirror fictional. If the user is in immediate distress, respond with grounded support instead of intensifying the scene.

For concrete authored test scenarios, read `docs/experiments/persona-scenarios.md`. These are design and acceptance aids, not empirical evidence of likeness or therapeutic benefit.
