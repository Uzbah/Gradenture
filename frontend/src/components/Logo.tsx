// "C." wordmark — matches the CareerBridge Mono + Lime system.
export default function Logo({ onDark = false }: { onDark?: boolean }) {
  return (
    <div className="logo">
      <span className={"logo-mark" + (onDark ? " on-dark" : "")}>
        C<span className="logo-dot">.</span>
      </span>
      <span className="logo-word">CareerBridge</span>
    </div>
  );
}
