# backend/src/utils

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

- `sanitize.py` — `clean_text(text)`: regex-strips anything that looks like an HTML tag. Used on question text/notes, review text, application notes, admin notes. Not a full sanitizer; the frontend relies on React escaping, so never render these fields with `dangerouslySetInnerHTML`. `bleach` is installed and used directly only in `users_service.complete_onboarding`.
