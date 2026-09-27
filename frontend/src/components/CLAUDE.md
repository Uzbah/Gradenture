# frontend/src/components

> **Keep this file current.** If you add, remove, rename, or materially change any file in this folder, update this CLAUDE.md in the same change. A stale CLAUDE.md is worse than none.

Tiny presentational pieces shared across pages. No state, no API calls.

- `Icon.tsx` — inline SVG icons on a 24px grid keyed by name (`home`, `prep`, `questions`, `reviews`, `companies`, `tracker`, `resume`, `admin`, `logout`). Add a path to `PATHS` to add an icon.
- `Logo.tsx` — "C." wordmark; `onDark` prop for the sidebar variant.
