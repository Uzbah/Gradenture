// "G." wordmark — matches the Gradenture Mono + Lime system.
export default function Logo({ onDark = false }: { onDark?: boolean }) {
  return (
    <div className="logo">
      <span className={"logo-mark" + (onDark ? " on-dark" : "")}>
        G<span className="logo-dot">.</span>
      </span>
      <span className="logo-word">Gradenture</span>
    </div>
  );
}
