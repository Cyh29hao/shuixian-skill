# Import Channels

Use this file when the user wants to import material from sources beyond WeChat.

## Supported channels in this version

- WeChat desktop databases
- iMessage `chat.db`
- exported transcript text files
- exported JSON and JSONL chat logs
- screenshots and images
- manual pasted snippets

## Suggested order

1. Start with the lightest source that already captures the user's voice.
2. Use transcript exports before asking for raw device databases unless the user specifically wants high fidelity.
3. Archive normalized transcripts, not only raw exports.

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
`psutil`, `pycryptodome`, and Windows-only `pymem` support the best-effort WeChat
route; `PyYAML` supports external skill validation. Install only when that route
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
- When the user imports broad WeChat history, generate a contact report first so analysis can focus on the relationships that matter most.
- When transcript volume grows, run `tools/mirror_profiler.py` so the mirror is built from organized signals instead of raw logs alone.
