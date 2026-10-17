# frontend/src/components

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

Shared presentational pieces. No API calls. Pages import Radix Themes
components directly; this folder only holds compositions used in 2+ places.

- `Icon.tsx` — inline SVG icons on a 24px grid keyed by name (nav icons + `logout`, `x`, `up`, `flag`, `search`). Add a path to `PATHS` to add an icon.
- `ui.tsx` — `Field` (label wrapper → real label association), `Choice` (Radix Select; `all` adds an "any" option reported as `""`, since Radix forbids empty item values), `CheckField`, `Tag` (enum value → toned Badge + label; free text → gray), `Notice` (Callout for error/success), `Stat`, `Pager`, `PageHeader`, `RLink` (router link styled as Radix Link), `AuthShell`, `Loading`, `Empty`, and dialogs: `FormDialog`, `ReasonDialog` (replaces `window.prompt`; cancel = no action), `ConfirmDialog` (replaces `window.confirm`).
