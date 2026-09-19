import { FormEvent, useEffect, useState } from "react";
import { api, ApiResponse, PageData, Review } from "../api";
import { useLookups } from "../lookups";

export default function Reviews() {
  const { domains, companies, domainName, companyName } = useLookups();
  const [reviews, setReviews] = useState<Review[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({ company_id: "", domain_id: "" });
  const [showForm, setShowForm] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    const params = new URLSearchParams({ page: String(page), size: "20" });
    Object.entries(filters).forEach(([k, v]) => v && params.set(k, v));
    api<ApiResponse<PageData<Review>>>(`/reviews/?${params}`)
      .then((r) => { setReviews(r.data.items); setCount(r.data.total); })
      .catch(() => {});
  }, [page, filters]);

  const flag = async (id: string) => {
    const reason = window.prompt("Why are you flagging this review? (min 5 characters)");
    if (!reason) return;
    try {
      await api(`/reviews/${id}/flag`, { method: "POST", body: { reason } });
      setMessage("Flagged — thanks, an admin will review it.");
    } catch (err: any) {
      setMessage(err.message);
    }
  };

  return (
    <>
      <div className="row" style={{ justifyContent: "space-between", marginBottom: "1rem" }}>
        <h1 style={{ margin: 0 }}>Company Interview Reviews</h1>
        <button onClick={() => setShowForm((s) => !s)}>{showForm ? "Close form" : "Write a review"}</button>
      </div>

      {showForm && (
        <ReviewForm domains={domains} companies={companies}
          onDone={(msg) => { setMessage(msg); setShowForm(false); }} />
      )}
      {message && <p className="success">{message}</p>}

      <div className="filters">
        <select value={filters.company_id} onChange={(e) => { setPage(1); setFilters({ ...filters, company_id: e.target.value }); }}>
          <option value="">All companies</option>
          {companies.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select value={filters.domain_id} onChange={(e) => { setPage(1); setFilters({ ...filters, domain_id: e.target.value }); }}>
          <option value="">All domains</option>
          {domains.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>
      </div>

      {reviews.length === 0 && <p className="muted">No reviews yet.</p>}
      {reviews.map((r) => (
        <div className="card" key={r.id}>
          <div className="row" style={{ marginBottom: "0.4rem" }}>
            <span className="badge">{companyName(r.company_id)}</span>
            {r.domain_id && <span className="badge">{domainName(r.domain_id)}</span>}
            {r.difficulty && <span className={`badge ${r.difficulty}`}>{r.difficulty}</span>}
            {r.outcome && <span className="badge">{r.outcome}</span>}
            <span className="muted">{r.role_title} · {r.interview_date.slice(0, 7)}</span>
          </div>
          <p>{r.review_text}</p>
          <div className="row mt">
            <button className="ghost" onClick={() => flag(r.id)}>⚑ Flag</button>
          </div>
        </div>
      ))}

      {count > 20 && (
        <div className="row">
          <button className="secondary small" disabled={page === 1} onClick={() => setPage(page - 1)}>Prev</button>
          <span className="muted">Page {page} of {Math.ceil(count / 20)}</span>
          <button className="secondary small" disabled={page >= Math.ceil(count / 20)} onClick={() => setPage(page + 1)}>Next</button>
        </div>
      )}
    </>
  );
}

function ReviewForm({ domains, companies, onDone }: {
  domains: { id: string; name: string }[];
  companies: { id: string; name: string }[];
  onDone: (msg: string) => void;
}) {
  const [form, setForm] = useState({
    company_id: "", domain_id: "", role_title: "", review_text: "",
    interview_month: "", difficulty: "", outcome: "", is_anonymous: false,
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k: string, v: any) => setForm((f) => ({ ...f, [k]: v }));

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      await api("/reviews/", {
        method: "POST",
        body: {
          company_id: form.company_id,
          domain_id: form.domain_id || null,
          role_title: form.role_title,
          review_text: form.review_text,
          interview_date: `${form.interview_month}-01`,
          difficulty: form.difficulty || null,
          outcome: form.outcome || null,
          is_anonymous: form.is_anonymous,
        },
      });
      onDone("Review submitted for moderation — it will go live once approved.");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card">
      <h2>Write an interview review</h2>
      <form onSubmit={submit}>
        <label>Company</label>
        <select value={form.company_id} onChange={(e) => set("company_id", e.target.value)} required>
          <option value="">Select…</option>
          {companies.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <label>Domain (optional)</label>
        <select value={form.domain_id} onChange={(e) => set("domain_id", e.target.value)}>
          <option value="">—</option>
          {domains.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>
        <label>Role applied for</label>
        <input value={form.role_title} onChange={(e) => set("role_title", e.target.value)} maxLength={100} required />
        <label>Your review (min 50 characters)</label>
        <textarea value={form.review_text} onChange={(e) => set("review_text", e.target.value)} minLength={50} required />
        <div className="row">
          <div style={{ flex: 1 }}>
            <label>Difficulty</label>
            <select value={form.difficulty} onChange={(e) => set("difficulty", e.target.value)}>
              <option value="">—</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label>Outcome</label>
            <select value={form.outcome} onChange={(e) => set("outcome", e.target.value)}>
              <option value="">—</option>
              <option value="offer">Offer received</option>
              <option value="rejected">Rejected</option>
              <option value="pending">Pending</option>
              <option value="withdrew">Withdrew</option>
              <option value="ghosted">Ghosted</option>
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label>Interview date</label>
            <input type="month" value={form.interview_month} onChange={(e) => set("interview_month", e.target.value)} required />
          </div>
        </div>
        <label style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <input type="checkbox" style={{ width: "auto" }} checked={form.is_anonymous} onChange={(e) => set("is_anonymous", e.target.checked)} />
          Submit anonymously
        </label>
        {error && <p className="error">{error}</p>}
        <button className="mt" disabled={busy}>{busy ? "Submitting…" : "Submit for review"}</button>
      </form>
    </div>
  );
}
