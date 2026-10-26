<div align="center">

# Shuixian.skill

### Your words, spoken back to you.

Bring your chosen chat history, journals, and writing. Build a mirror of your voice, then talk with it.

[Start with your agent](#start-with-your-agent) · [Install manually](#install-manually) · [中文](README.md) · [First-run guide](docs/quickstart.md) · [Actual conversations](docs/try-it.md)

</div>

<p align="center">
  <picture>
    <source media="(max-width: 600px)" srcset="assets/corpus-hero-mobile-v1.png" />
    <img src="assets/corpus-hero-v1.png" alt="Chinese illustrated guide: personal writing, your voice, your conversational mirror" width="920" />
  </picture>
</p>

**Your chat history already contains many sides of your voice.** The jokes, the careful explanations, the way you change your mind. Shuixian helps an agent organize those patterns into a readable, reusable skill so you can talk with a mirror shaped by your own language.

The main path is **personal corpus → expression patterns → saved mirror → conversation and correction**. Use chosen files across periods and situations. A short description or public preset is an optional preview; your own writing is the basis for a personal voice.

## Start with your agent

Give this to Codex or Claude Code with local file and terminal access:

```text
This Shuixian skill looks interesting:
https://github.com/Cyh29hao/shuixian-skill
Install it in my current project, import my chosen local WeChat history,
and build a mirror from my own messages so I can talk with my own voice.
Read the repository's SKILL.md and use this host's installation and invocation paths.
Ask together for any missing source directory, self-speaker label, or export scope.
If readable exports exist, proceed. If only encrypted databases exist,
check the version and extraction route before claiming they can be imported.
Save abstract voice patterns by default, preserve originals, and keep chats off GitHub.
```

If you already have an export, add its real path and your exact sender label. The agent can install, normalize the input, verify attribution, read selected passages, build the mirror, and try a conversation.

**A few-minute start depends on having readable material.**

| Material | Current route |
| --- | --- |
| Text, Markdown, JSON, JSONL exports | Primary quick-start path; common structures supported |
| Compatible older plaintext WeChat databases | Extract a chosen contact from `MicroMsg.db` and `MSG*.db`; verify the schema |
| A running WeChat client or encrypted databases only | Check version, permissions and export options first; no universal WeChat 4.x extraction or timing guarantee |

This is an agent task request, not a universal one-click promise. See the [WeChat guide](references/wechat-import.md).

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

## Star History

Thank you for every star. This date-based line chart uses the established Star History service; updates may be cached.

<a href="https://www.star-history.com/#Cyh29hao/shuixian-skill&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Cyh29hao/shuixian-skill&amp;type=Date&amp;theme=dark" />
    <img src="https://api.star-history.com/svg?repos=Cyh29hao/shuixian-skill&amp;type=Date&amp;theme=light" alt="GitHub Star history line chart for Cyh29hao/shuixian-skill" width="920" />
  </picture>
</a>

[Open Star History](https://www.star-history.com/#Cyh29hao/shuixian-skill&Date) · [Current stars](https://github.com/Cyh29hao/shuixian-skill/stargazers)

MIT licensed. The import layer drew on implementation ideas from the MIT-licensed `npy-skill` project.
