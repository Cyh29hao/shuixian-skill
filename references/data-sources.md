# Data Sources

Use this file to choose the lightest viable input path.

## Supported in this scaffold

- prompt-only descriptions
- pasted self-descriptions
- pasted chat excerpts
- exported text chat logs
- decrypted WeChat desktop databases
- screenshots and images as secondary evidence

## Intake recommendation order

1. start with prompt-only if the user wants privacy
2. add a few representative snippets if the voice still feels generic
3. add longer logs only when the user wants higher fidelity

## Notes on chat imports

The current scaffold includes an experimental WeChat desktop adapter:

- `tools/wechat_decryptor.py` for best-effort key lookup and database decryption
- `tools/wechat_importer.py` for contact listing and transcript extraction
- `tools/source_importer.py` for generic text and image archival

Keep the claims modest:

- decryption is best-effort
- transcript extraction is the stable layer
- manual pasted text is still the fallback when local database extraction fails
