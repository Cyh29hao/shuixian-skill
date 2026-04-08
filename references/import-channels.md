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

## Positioning

Keep the product promise honest:

- WeChat and iMessage are convenience adapters.
- Generic transcript import is the stable fallback.
- The real long-term contract is "normalize input into analyzable transcript files."
- When the user imports broad WeChat history, generate a contact report first so analysis can focus on the relationships that matter most.
- When transcript volume grows, run `tools/mirror_profiler.py` so the mirror is built from organized signals instead of raw logs alone.
