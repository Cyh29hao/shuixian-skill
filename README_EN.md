<div align="center">

# Shuixian.skill

### The words you have written, growing into a voice you can talk with.

Your chat history, journals and writing → your expression → a conversation with yourself.

**[Explore the web entrance ↗](https://cyh29hao.github.io/shuixian-skill/)** · [Bring my chats](#bring-your-chats) · [Start with your agent](#start-with-your-agent) · [Install manually](#install-manually) · [中文](README.md)

Listed in [colleague-skill Gallery](https://titanwings.github.io/colleague-skill-site/gallery/shuixian-skill/) · [EverythingSkill](https://everythingskill.net/skills/shuixian-skill)

</div>

> “I tried to organize my files and ended up with three new folders.”
>
> “The files haven't moved in, but you've built them three new homes.”

Translated excerpt from an [actual synthetic-corpus trial](docs/experiments/corpus-onboarding-2026-10-27.md#陌生-agent-从候选技能开始的一次上手), not a likeness claim. The aim is a familiar way of answering, rather than the same generic reassurance for every sentence.

<p align="center">
  <picture>
    <source media="(max-width: 600px)" srcset="assets/corpus-hero-mobile-v1.png" />
    <img src="assets/corpus-hero-v1.png" alt="Chinese illustrated guide: your writing, your voice, your mirror" width="760" />
  </picture>
</p>

**Your own writing comes first.** Chosen records ground cadence, phrasing and interaction patterns in a saved, correctable mirror. Relationship framing is optional. Public presets are only a preview when no corpus is ready.

## Star History

Thank you for every star. This date-based line chart uses the established Star History service; updates may be cached.

<a href="https://www.star-history.com/#Cyh29hao/shuixian-skill&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Cyh29hao/shuixian-skill&amp;type=Date&amp;theme=dark" />
    <img src="https://api.star-history.com/svg?repos=Cyh29hao/shuixian-skill&amp;type=Date&amp;theme=light" alt="GitHub Star history line chart for Cyh29hao/shuixian-skill" width="620" />
  </picture>
</a>

[Open Star History](https://www.star-history.com/#Cyh29hao/shuixian-skill&Date) · [Current stars](https://github.com/Cyh29hao/shuixian-skill/stargazers)


## Start with your agent

Give this to Codex or Claude Code with local file access. Replace the path and sender label with your own.

```text
Install https://github.com/Cyh29hao/shuixian-skill in my current project.
My selected chat exports are in D:/My writing/; the sender named Qinghe is me.
Build a mirror from my own expression so I can talk with my own voice.
Save abstract voice patterns first and preserve originals.
Ask together for anything essential that's missing, then start a conversation.
```

If the records are still inside WeChat, say so: the agent should help establish an export route. Readable exports are the quick path; encrypted databases still have version and access limits. [WeChat scope](references/wechat-import.md).

## Bring your chats

Start with what you already have; no need to hand-format your entire history.

| Material | Lightest route |
| --- | --- |
| One file or a folder of exports | Let the agent preview counts and speakers; identify yourself |
| Telegram / ChatGPT JSON or common chat CSV / TSV | Use the lightweight import entry; see exact supported shapes in the [guide](docs/importing.md) |
| Journals, notes, pasted writing | Save TXT / Markdown and explicitly confirm single authorship |
| A running WeChat client or raw databases only | Establish a readable export first using the [WeChat guide](references/wechat-import.md) |
| Screenshots | A vision-capable agent can transcribe for confirmation; these scripts include no OCR |

For manual use, run from the installed builder:

```sh
python .agents/skills/create-shuixian/tools/import_chat.py "D:/My writing"
```

In Claude Code, replace `.agents` with `.claude`. Preview the speakers, select yourself, and receive organized transcripts, a profile and a ready-to-paste next prompt. Existing outputs are preserved. This prepares material; a statistical pass does not mean the model has learned your whole identity. [Import guide](docs/importing.md).

## From corpus to conversation

<p align="center">
  <picture>
    <source media="(max-width: 600px)" srcset="assets/corpus-flow-mobile-v1.png" />
    <img src="assets/corpus-flow-v1.png" alt="Chinese four-step guide: choose writing, identify your messages, organize voice patterns, talk and correct" width="920" />
  </picture>
</p>

1. Choose your material and scope. Several contexts are more informative than one repeated catchphrase.
2. Identify your own messages. Other speakers, quotations, and copied material are distinct sources.
3. Organize, then read in batches. Statistics help navigation; actual passages support cadence, phrasing, humor, and register choices.
4. Save a mirror and talk. Correct a concrete mismatch; persist requested changes with rollback versions.

This guides the host model with skill files and selected material; it does not train new model weights. Relationship framing is optional: talking to yourself does not require choosing romance or a fictional appearance.

[The 12,000-message synthetic import and conversation experiment](docs/experiments/corpus-onboarding-2026-10-27.md) records 6,000 messages per speaker, actual commands and timings, and the limits of a repetitive synthetic corpus. It does not establish personal likeness or end-to-end setup speed.

## Install manually

Requires Git, Python 3.9+, and the corresponding agent. Core import, generation and updates need no extra Python packages. Run the matching command in your project.

**Codex**

```sh
git clone https://github.com/Cyh29hao/shuixian-skill .agents/skills/create-shuixian
```

In the same project, invoke `$create-shuixian` with your chosen corpus path and sender label.

**Claude Code**

```sh
git clone https://github.com/Cyh29hao/shuixian-skill .claude/skills/create-shuixian
```

In the same project, invoke `/create-shuixian` with your material. Codex detects skill changes; reopen/restart if discovery has not refreshed. Claude Code can refresh newly added directories with `/reload-skills`.

Clone refuses an existing nonempty destination. Inspect an existing installation instead of deleting your mirrors. See the [installation guide](docs/installation.md) for personal paths, Windows, output directories and checks, and the [Claude Code guide](docs/CLAUDE.md) for host-specific details and validation limits.

## Correct and save

```text
That sounded like a coach. I would joke about the actual problem first.
Change only that, keep the rest of the voice, and retry one reply.
```

To keep the correction, ask the builder to update the mirror, replace conflicting old instructions, and report its actual path, invocation name, and version. A changed reply and a saved update are separate results. [Update and rollback guide](docs/quickstart.md#6-保存纠偏并确认没有改坏其他地方).

## No corpus ready? Try a public voice

Read [actual conversations](docs/try-it.md), or try a public preset. It has not learned your voice.

```sh
python .agents/skills/create-shuixian/tools/demo_builder.py --preset close-friend-same-form --base-dir .agents/skills
```

Use the invocation name printed by the command. For Claude Code, replace both `.agents` paths with `.claude`. Other presets and small-sample previews remain in the [first-run guide](docs/quickstart.md).

## Sources and scope

Generic readable exports are the primary input. WeChat databases, iMessage and screenshots have specific format, platform or host requirements: [import channels](references/import-channels.md).

Mirrors are readable skill, voice, mind, relationship and optional appearance files, with versioned changes. Large histories are organized locally and selected passages read by the host. Archiving source text is a separate choice. `style-only` retains abstract expression patterns by agreement; it is not automatic anonymization.

The host may send read material to its model service. Local files do not make the workflow offline. Identity transfer, independent consciousness, complete personal memory and subjective likeness are not established capabilities. [Privacy and safety](references/privacy-and-safety.md).


## Community listings and sharing

| Link | Relationship |
| --- | --- |
| [colleague-skill Gallery](https://titanwings.github.io/colleague-skill-site/gallery/shuixian-skill/) | Community listing with author attribution and repository link |
| [EverythingSkill](https://everythingskill.net/skills/shuixian-skill) | Skill directory listing; its older setup copy may lag this repository |
| [Socialistic share page](https://socialistic.ai/en/skill/shuixian-skill-7137db/) | Third-party community entry offered in [Issue #1](https://github.com/Cyh29hao/shuixian-skill/issues/1); page reachable, signed-in model chat untested |

These are listings and community sharing, not claimed commercial endorsements. Third-party sites have their own sign-in and data terms; this project does not send your corpus to them automatically.

MIT licensed. The import layer drew on implementation ideas from the MIT-licensed `npy-skill` project.
