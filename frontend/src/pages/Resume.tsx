import { FormEvent, useRef, useState } from "react";
import { api } from "../api";

interface Analysis {
  score: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  improvements: string[];
  keyword_gaps: string[];
}

export default function Resume() {
  const fileRef = useRef<HTMLInputElement>(null);
  const [jd, setJd] = useState("");
  const [result, setResult] = useState<Analysis | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    setError(""); setResult(null); setBusy(true);
    const fd = new FormData();
    fd.append("resume", file);
    if (jd.trim()) fd.append("job_description", jd.trim());
    try {
      const res = await api<{ data: Analysis }>("/resume/analyze", { method: "POST", body: fd });
      setResult(res.data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <h1>AI Resume Analyzer</h1>
      <div className="card">
        <form onSubmit={submit}>
          <label>Resume (PDF or DOCX, max 5MB)</label>
          <input type="file" ref={fileRef} accept=".pdf,.docx" required />
          <label>Job description (optional — enables keyword gap analysis)</label>
          <textarea value={jd} onChange={(e) => setJd(e.target.value)} placeholder="Paste the job description here…" />
          {error && <p className="error">{error}</p>}
          <button className="mt" disabled={busy}>{busy ? "Analyzing… (this takes ~15s)" : "Analyze"}</button>
          <p className="muted mt">Limited to 3 analyses per hour.</p>
        </form>
      </div>

      {result && (
        <div className="card">
          <h2>Score: {result.score}/10</h2>
          <p>{result.summary}</p>
          <Section title="Strengths" items={result.strengths} />
          <Section title="Weaknesses" items={result.weaknesses} />
          <Section title="Improvements" items={result.improvements} />
          {result.keyword_gaps?.length > 0 && <Section title="Missing keywords" items={result.keyword_gaps} />}
        </div>
      )}
    </>
  );
}

function Section({ title, items }: { title: string; items: string[] }) {
  if (!items?.length) return null;
  return (
    <div className="mt">
      <h3>{title}</h3>
      <ul style={{ paddingLeft: "1.25rem" }}>
        {items.map((s, i) => <li key={i}>{s}</li>)}
      </ul>
    </div>
  );
}
