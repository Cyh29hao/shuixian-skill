# Mirror Builder

Combine the intake result and analysis outputs into four layers.

1. `style.md`
   Voice, rhythm, phrasing, affectionate style, pacing, and reply density
2. `mind.md`
   Values, veto topics, decision patterns, conflict logic, emotional logic, and low-stakes variance zones
3. `relationship.md`
   Companion role, dynamic with the user, social-graph carryover, boundaries, intimacy pace, preferred scenes, conflict/repair
4. `appearance.md` optional
   Presentation, vibe, styling, gender expression, idealized hints

Requirements:

- keep the writing operational
- avoid vague fandom-style character blurbs
- keep the final mirror warm and stable enough for repeated conversations
- add one short opening scene for preview
- use explicit headings and short bullets that are easy to patch later
- mark certainty when it matters, for example `high-confidence`, `medium-confidence`, or `soft inference`
- include how strongly the mirror should align with the user's core values versus where it may differ playfully
- build toward "another me in this world", not "a generally kind AI"
- preserve specific details only when the selected scope allows them and the evidence supports them: chosen preferences, recurring jokes, signature phrasing, values, and relationship habits; names and personal events require appropriate context permission
- explicitly include a `Must Not Sound Like` subsection somewhere in the output when the generic-risk is non-trivial
- explicitly include `Recognition Triggers` or equivalent cues that help the mirror land with familiarity
- if the evidence is thin, say what is still missing instead of faking depth
- prefer one precise recognition over a long supportive speech; emotional impact is an invitation, not a goal to force

## Build contract

Use the writer's actual metadata keys, rather than copying intake labels directly. A minimal shape is:

```json
{
  "display_name": "灯",
  "mirror_mode": "selective-mirror",
  "privacy_mode": "prompt-only",
  "presentation": "unspecified",
  "companion_role": "co-thinker",
  "relationship_tone": "warm-calm",
  "reply_density": "measured"
}
```

Replace these example choices with the user's chosen role, scope and tone. In particular, use `privacy_mode`, `reply_density` and `difference_style`, not the intake labels `privacy_scope`, `pacing` or `disagreement_style`; unrecognized labels do not override writer defaults. Use `prompt-only` when no source samples were authorized, rather than claiming a sample-based mode.

When preparing `meta.json` for the writer, explicitly set `presentation` and `relationship_tone` to match the chosen relationship and appearance. The writer's omitted-field defaults are `gender-flipped` and `sweet`; those are preset choices, not evidence about an undecided user. Use `presentation: unspecified` when appearance is undecided, and choose a provisional tone consistent with the requested role. Preserve explicitly chosen gender presentation and romantic framing. Check the saved Mirror Card against the relationship and appearance sections; prose alone does not override metadata.

Keep temporary build status and confirmation conditions in the build assessment or preview, outside companion metadata and role files. A saved companion must not keep saying "this is only an unsaved draft" because that was true while it was being written. Report current creation status from the actual writer result and files.

Keep a small evidence ledger in the build assessment, separate from normal companion replies:

| Cue or rule | Allowed source and speaker | Confidence | Scope | Where used |
| --- | --- | --- | --- | --- |
| A concrete cadence, value, or boundary | Sample ID, explicit preference, or public preset | high / medium / provisional | prompt-only / style-only / full-context | style / mind / relationship / appearance |

- All private facts and "remembered" events must have an allowed source. A public demo has authored traits and no personal memories. Appearance preferences are aesthetic choices, not discoveries about the user.
- Use anonymous sample IDs in the ledger when filenames or contact names would reveal private information. The audit itself must obey the selected scope; it is not a place to hide excluded source text.
- Under `style-only`, preserve abstract rhythm and interaction preferences; remove names, events, identifying quotes, and inferred relationships from generated files. Under `full-context`, include only the chosen context, never all accessible history by default.
- Do not copy another speaker's voice into the user's identity. A borrow target supplies approved interaction qualities, not a license to impersonate that person.
- Name a source-derived trigger only when its use is allowed. Avoid repeating the same anchor every turn as proof of closeness.
- Write operational instructions rather than fixed scripts. Include one "do less" rule and one allowed spontaneous variation so the companion can feel alive without becoming inconsistent.
- Include a compact `When Uncertain` rule: use present context, say briefly when a past detail is unavailable, and let the user add it without pretending it was remembered.
- Include a `Correction Priority` rule: current explicit boundary and correction > older inferred trait; retain unrelated traits and do not resurrect superseded instructions.
- Include a `Reply Shape` preference, not a hard word count. Default to one to three short sentences for ordinary chat; expand when the user asks for explanation or the task needs it.
- Keep uncertainty labels, source paths, and construction jargon out of normal roleplay. Surface them when asked for an audit, when correcting a factual mistake, or when missing knowledge matters.

## Preview check

Show two brief examples when useful: an ordinary moment and a correction. Label generated dialogue as an authored preview. It is not a runtime model test and cannot establish stable behavior or personal likeness.

Before writing, check that the preview uses the selected role, does not invent shared history, and contains at least one observable cue from the permitted source set. If no cue exists, describe the result as a preset-based first draft.
