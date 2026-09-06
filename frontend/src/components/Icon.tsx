// Inline SVG icons, 24px grid, stroke 1.8–2.4, round caps — matches the
// Mono + Lime design system (see frontend/CLAUDE.md / design.md).
const PATHS: Record<string, string> = {
  home: "M3 10.5 12 3l9 7.5V21h-6v-6h-6v6H3Z",
  questions: "M12 3 2 8.2l10 5 10-5L12 3ZM2 13.4l10 5 10-5",
  prep: "M4 19V5a2 2 0 0 1 2-2h14v16H6a2 2 0 0 0-2 2Zm0 0a2 2 0 0 1 2-1h14",
  tracker: "M4 4h4v16H4Zm6 0h4v10h-4Zm6 0h4v7h-4Z",
  reviews: "M12 3l2.6 6.6L21 10l-5 4.6L17.4 21 12 17.3 6.6 21 8 14.6 3 10l6.4-.4L12 3Z",
  resume: "M6 3h8l5 5v13a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Zm8 0v5h5M9 13h6M9 17h6",
  admin: "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3Z",
  logout: "M9 4H5v16h4M14 8l4 4-4 4M18 12H9",
};

export default function Icon({
  name,
  size = 20,
  strokeWidth = 1.8,
}: {
  name: keyof typeof PATHS;
  size?: number;
  strokeWidth?: number;
}) {
  const d = PATHS[name];
  if (!d) return null;
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={d} />
    </svg>
  );
}
