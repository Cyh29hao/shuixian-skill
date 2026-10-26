# Import Channels

Use this file when the user wants to import material from sources beyond WeChat.

## Supported channels in this version

- compatible older plaintext WeChat desktop databases (not universal client extraction)
- iMessage `chat.db`
- exported transcript text files
- exported JSON and JSONL chat logs
- screenshots and images
- manual pasted snippets

## Suggested order

1. Use the personal corpus the user selected: chat exports, journals, notes or writing. Keep scope and author attribution explicit.
2. Use readable transcript exports before acquiring raw device databases. More records are useful only when their authorship and context are clear.
3. Normalize and profile larger collections, then read diverse user-message passages in batches; `corpus-workflow.md` separates full mechanical counts from actual model reading.
4. Archive source text only if chosen. A style-only mirror need not retain its original transcripts.

## Current scripts

- `tools/wechat_decryptor.py`
- `tools/wechat_importer.py`
- `tools/imessage_importer.py`
- `tools/transcript_importer.py`
- `tools/source_importer.py`

## Optional dependencies and actual scope

The public presets, skill writer, generic transcript importer, source archiver,
and profiler use Python's standard library. `pypinyin` is optional for natural
Chinese-name slugs; without it, an explicit ASCII `--slug` is the predictable path.

`requirements.txt` lists optional packages used by the broader toolkit:
`psutil`, `pycryptodome`, and Windows-only `pymem` are used by the legacy experimental WeChat
decryptor, whose availability does not establish reliable key validation or current-client compatibility; see `wechat-import.md`. `PyYAML` supports external skill validation. Install only when that route
is needed and within the user's environment permissions. README artwork rendering
uses Pillow, a maintainer tool rather than a companion runtime dependency.

Screenshots need a host that can understand images; the bundled Python tools do
not provide standalone OCR. iMessage reads a local macOS database. Generic
imports support common nested message structures, not every vendor schema or
every multimodal attachment. Check the reported message count and inspect a small
sample before analyzing a large export.

Use `mirror_profiler.py --self-name <your-sender-label>` when the transcript does
not use a recognized self label. Multiple aliases can be supplied by repeating
the flag. If the user cannot be identified, keep user traits unknown instead of
substituting all speakers. Relations and topics remain keyword clues to verify.

## Positioning

Keep the product promise honest:

- WeChat and iMessage are convenience adapters.
- Generic transcript import is the stable fallback.
- The real long-term contract is "normalize input into analyzable transcript files."
- With a compatible selected plaintext WeChat history, a contact report can help choose a subset. Do not list all contacts from a live account before the user has chosen that scope.
- When transcript volume grows, run `tools/mirror_profiler.py` so the mirror is built from organized signals instead of raw logs alone.
