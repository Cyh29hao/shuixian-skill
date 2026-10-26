# Data Sources

Use this file to choose a viable input path for the user's requested corpus and scope.

## Supported in this version

- prompt-only descriptions
- pasted self-descriptions
- pasted chat excerpts
- exported text chat logs
- decrypted WeChat desktop databases
- iMessage `chat.db`
- transcript exports in `.txt`, `.md`, `.json`, and `.jsonl`
- screenshots and images as secondary evidence

## Intake recommendation order

1. Use already chosen personal writing or exported transcripts as the primary path. Multiple files and periods may be included; distinguish the user's own messages from other speakers.
2. Organize larger corpora mechanically, then read a bounded diverse selection; see `corpus-workflow.md`. Do not imply that the model read every imported message.
3. Use raw local databases only for the requested account/range and a verified compatible adapter. A live encrypted WeChat installation is not a ready-made transcript.
4. If no readable corpus is ready or the user prefers less disclosure, offer prompt-only or a few representative snippets as an optional first draft.

## Notes on imports

The current scaffold includes multiple adapters:

- `tools/wechat_decryptor.py` for best-effort WeChat key lookup and decryption
- `tools/wechat_importer.py` for WeChat contact listing, contact reports, and transcript extraction
- `tools/imessage_importer.py` for iMessage extraction
- `tools/transcript_importer.py` for generic transcript exports
- `tools/mirror_profiler.py` for a middle-layer relationship and value report
- `tools/source_importer.py` for generic text and image archival

Keep the claims modest:

- decryption is best-effort
- transcript extraction is the stable layer
- manual pasted text is still the fallback when raw local extraction fails
