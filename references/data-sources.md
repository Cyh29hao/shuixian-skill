# Data Sources

Use this file to choose the lightest viable input path.

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

1. start with prompt-only if the user wants privacy
2. add a few representative snippets if the voice still feels generic
3. add exported transcripts when the user wants higher fidelity
4. use raw local databases only when the user explicitly wants deeper import

## Notes on imports

The current scaffold includes multiple adapters:

- `tools/wechat_decryptor.py` for best-effort WeChat key lookup and decryption
- `tools/wechat_importer.py` for WeChat contact listing, contact reports, and transcript extraction
- `tools/imessage_importer.py` for iMessage extraction
- `tools/transcript_importer.py` for generic transcript exports
- `tools/source_importer.py` for generic text and image archival

Keep the claims modest:

- decryption is best-effort
- transcript extraction is the stable layer
- manual pasted text is still the fallback when raw local extraction fails
