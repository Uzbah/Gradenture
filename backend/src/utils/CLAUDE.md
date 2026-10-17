# backend/src/utils

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

- `sanitize.py` — `clean_text(text)`: removes NUL and other control characters (Postgres rejects `\x00`). It deliberately does **not** strip HTML: that used to mangle code such as `vector<int>` in interview questions. Safety comes from output encoding — React escapes text and emails are plain text — so never render user fields with `dangerouslySetInnerHTML`. Used on all user-submitted text and admin notes. `bleach` was removed.
