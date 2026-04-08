# WeChat Import

Use this file when the user wants to import WeChat desktop chat history.

## Supported workflow

### Step 1. Decrypt local databases

Keep the WeChat desktop client logged in, then run:

```powershell
python tools/wechat_decryptor.py --find-key-only
python tools/wechat_decryptor.py --key "<hex-key>" --db-dir "<WeChat data dir>" --output "./decrypted"
```

If automatic key lookup fails, ask the user to supply a key from tools such as PyWxDump or WeChatMsg and continue with `--key`.

### Step 2. List contacts

```powershell
python tools/wechat_importer.py --list-contacts --db-dir "./decrypted"
```

### Step 3. Build a contact report when the user has broad history

```powershell
python tools/wechat_importer.py --contact-report --db-dir "./decrypted" --output "./wechat-contact-report.md"
```

Use this when the user imported a lot of WeChat history and needs help deciding which relationships to analyze first.

### Step 4. Extract one transcript

```powershell
python tools/wechat_importer.py --extract --db-dir "./decrypted" --target "<contact name>" --output "./wechat-messages.txt"
```

### Step 5. Archive into a generated mirror

```powershell
python tools/wechat_importer.py --extract --db-dir "./decrypted" --target "<contact name>" --output "./wechat-messages.txt" --archive-to "./.agents/skills/shuixian-<slug>"
```

## Product stance

- Treat automatic WeChat key extraction as best-effort, not guaranteed.
- Prefer not to promise one-click success across all WeChat versions.
- If decryption fails, fall back to exported text, screenshots, or user-pasted snippets.
- Make the privacy tradeoff explicit before importing.
