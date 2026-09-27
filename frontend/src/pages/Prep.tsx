import { useEffect, useState } from "react";
import { api, BankQuestion } from "../api";
import { useLookups } from "../lookups";

interface PrepData {
  domain_id: string;
  topics: { topic: string; completed: boolean }[];
  score: number;
}

export function ProgressRing({ score, size = 120 }: { score: number; size?: number }) {
  const stroke = 10;
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  return (
    <svg width={size} height={size} role="img" aria-label={`Preparedness ${score}%`}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--border)" strokeWidth={stroke} />
      <circle
        cx={size / 2} cy={size / 2} r={r} fill="none"
        stroke="var(--primary)" strokeWidth={stroke} strokeLinecap="round"
        strokeDasharray={circ} strokeDashoffset={circ * (1 - score / 100)}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
        style={{ transition: "stroke-dashoffset 0.4s" }}
      />
      <text x="50%" y="50%" textAnchor="middle" dominantBaseline="central"
        fontSize={size / 4.5} fontWeight="700" fill="var(--text)">
        {score}%
      </text>
    </svg>
  );
}

export default function Prep() {
  const [data, setData] = useState<PrepData | null>(null);
  const [error, setError] = useState("");
  const [bank, setBank] = useState<BankQuestion[]>([]);
  const { companyName } = useLookups();

  useEffect(() => {
    api<{ data: PrepData }>("/prep/").then((r) => setData(r.data)).catch((e) => setError(e.message));
  }, []);

  // ponytail: first 50 only (API cap); add paging when a domain outgrows it
  useEffect(() => {
    if (!data?.domain_id) return;
    api<{ data: BankQuestion[] }>(`/prep/questions?domain_id=${data.domain_id}&limit=50`)
      .then((r) => setBank(r.data)).catch(() => {});
  }, [data?.domain_id]);

  const toggle = async (topic: string, completed: boolean) => {
    // optimistic update
    setData((d) => d && {
      ...d,
      topics: d.topics.map((t) => (t.topic === topic ? { ...t, completed } : t)),
    });
    try {
      const res = await api<{ data: PrepData }>("/prep/", {
        method: "PATCH", body: { topic, completed },
      });
      setData(res.data);
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (error) return <><h1>Interview Prep</h1><p className="error">{error}</p></>;
  if (!data) return <p className="muted">Loading…</p>;

  const done = data.topics.filter((t) => t.completed).length;

  return (
    <>
      <h1>Interview Prep</h1>
      <div className="card">
        <div className="row" style={{ gap: "1.5rem" }}>
          <ProgressRing score={data.score} />
          <div>
            <h2 style={{ marginBottom: "0.25rem" }}>Preparedness score</h2>
            <p className="muted">
              {done} of {data.topics.length} topics studied in your domain.
              {data.score === 100 ? " You're interview-ready! 🎉" : " Check off topics as you study them."}
            </p>
          </div>
        </div>
      </div>
      <div className="card">
        <h2>Roadmap topics</h2>
        {data.topics.map((t) => (
          <label key={t.topic} style={{ display: "flex", gap: "0.6rem", alignItems: "center", padding: "0.45rem 0", margin: 0, fontWeight: 400, cursor: "pointer", borderBottom: "1px solid var(--border)" }}>
            <input
              type="checkbox"
              style={{ width: "auto" }}
              checked={t.completed}
              onChange={(e) => toggle(t.topic, e.target.checked)}
            />
            <span style={{ textDecoration: t.completed ? "line-through" : "none", color: t.completed ? "var(--muted)" : "var(--text)" }}>
              {t.topic}
            </span>
          </label>
        ))}
      </div>
      <div className="card">
        <h2>Practice questions ({bank.length})</h2>
        {bank.length === 0 && <p className="muted">No practice questions for your domain yet.</p>}
        {bank.map((q) => (
          <div key={q.id} style={{ padding: "0.6rem 0", borderBottom: "1px solid var(--border)" }}>
            <div className="row" style={{ marginBottom: "0.3rem" }}>
              {q.company_id && <span className="badge">{companyName(q.company_id)}</span>}
              {q.question_type !== "technical" && <span className="badge">{q.question_type}</span>}
              <span className="muted">{q.role_title}</span>
            </div>
            <p style={{ margin: 0 }}>{q.question_text}</p>
          </div>
        ))}
      </div>
    </>
  );
}
