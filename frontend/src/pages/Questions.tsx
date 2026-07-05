import { FormEvent, useEffect, useState } from "react";
import { api, Question } from "../api";
import { useLookups } from "../lookups";

export default function Questions() {
  const { domains, companies, domainName, companyName, reloadCompanies } = useLookups();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({ domain_id: "", company_id: "", difficulty: "", question_type: "" });
  const [showForm, setShowForm] = useState(false);
  const [message, setMessage] = useState("");

  const load = () => {
    const params = new URLSearchParams({ page: String(page), limit: "20" });
    Object.entries(filters).forEach(([k, v]) => v && params.set(k, v));
    api<{ data: Question[]; count: number }>(`/questions/?${params}`)
      .then((r) => { setQuestions(r.data); setCount(r.count); })
      .catch(() => {});
  };
  useEffect(load, [page, filters]);

  const upvote = async (id: string) => {
    try {
      const res = await api<{ upvotes: number }>(`/questions/${id}/upvote`, { method: "POST" });
      setQuestions((qs) => qs.map((q) => (q.id === id ? { ...q, upvotes: res.upvotes } : q)));
    } catch (err: any) {
      setMessage(err.message);
    }
  };

  const flag = async (id: string) => {
    const reason = window.prompt("Why are you flagging this question? (min 5 characters)");
    if (!reason) return;
    try {
      await api(`/questions/${id}/flag`, { method: "POST", body: { reason } });
      setMessage("Flagged — thanks, an admin will review it.");
    } catch (err: any) {
      setMessage(err.message);
    }
  };

  return (
    <>
      <div className="row" style={{ justifyContent: "space-between", marginBottom: "1rem" }}>
        <h1 style={{ margin: 0 }}>Interview Questions</h1>
        <button onClick={() => setShowForm((s) => !s)}>{showForm ? "Close form" : "Submit a question"}</button>
      </div>

      {showForm && (
        <QuestionForm
          domains={domains}
          companies={companies}
          reloadCompanies={reloadCompanies}
          onDone={(msg) => { setMessage(msg); setShowForm(false); }}
        />
      )}
      {message && <p className="success">{message}</p>}

      <div className="filters">
        <select value={filters.domain_id} onChange={(e) => { setPage(1); setFilters({ ...filters, domain_id: e.target.value }); }}>
          <option value="">All domains</option>
          {domains.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>
        <select value={filters.company_id} onChange={(e) => { setPage(1); setFilters({ ...filters, company_id: e.target.value }); }}>
          <option value="">All companies</option>
          {companies.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select value={filters.difficulty} onChange={(e) => { setPage(1); setFilters({ ...filters, difficulty: e.target.value }); }}>
          <option value="">Any difficulty</option>
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
        <select value={filters.question_type} onChange={(e) => { setPage(1); setFilters({ ...filters, question_type: e.target.value }); }}>
          <option value="">Any type</option>
          <option value="technical">Technical</option>
          <option value="behavioural">Behavioural</option>
          <option value="hr">HR</option>
          <option value="case_study">Case study</option>
        </select>
      </div>

      {questions.length === 0 && <p className="muted">No questions match these filters yet.</p>}
      {questions.map((q) => (
        <div className="card" key={q.id}>
          <div className="row" style={{ marginBottom: "0.4rem" }}>
            <span className="badge">{domainName(q.domain_id)}</span>
            <span className="badge">{companyName(q.company_id)}</span>
            <span className={`badge ${q.difficulty}`}>{q.difficulty}</span>
            <span className="badge">{q.question_type.replace("_", " ")}</span>
            <span className="muted">{q.role_title} · asked {q.asked_date.slice(0, 7)}</span>
          </div>
          <p>{q.question_text}</p>
          {q.notes && <p className="muted">Notes: {q.notes}</p>}
          <div className="row mt">
            <button className="ghost" onClick={() => upvote(q.id)}>▲ {q.upvotes}</button>
            <button className="ghost" onClick={() => flag(q.id)}>⚑ Flag</button>
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

function QuestionForm({ domains, companies, reloadCompanies, onDone }: {
  domains: { id: string; name: string }[];
  companies: { id: string; name: string }[];
  reloadCompanies: () => void;
  onDone: (msg: string) => void;
}) {
  const [form, setForm] = useState({
    domain_id: "", company_id: "", role_title: "", question_text: "",
    question_type: "technical", difficulty: "medium", asked_month: "",
    notes: "", is_anonymous: false,
  });
  const [newCompany, setNewCompany] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k: string, v: any) => setForm((f) => ({ ...f, [k]: v }));

  const addCompany = async () => {
    setError("");
    try {
      await api("/companies/", { method: "POST", body: { name: newCompany } });
      setNewCompany("");
      reloadCompanies();
      setError("Company submitted — it will appear once an admin approves it.");
    } catch (err: any) {
      setError(err.message);
    }
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      await api("/questions/", {
        method: "POST",
        body: {
          domain_id: form.domain_id, company_id: form.company_id,
          role_title: form.role_title, question_text: form.question_text,
          question_type: form.question_type, difficulty: form.difficulty,
          asked_date: `${form.asked_month}-01`,
          notes: form.notes || null, is_anonymous: form.is_anonymous,
        },
      });
      onDone("Question submitted for review — you'll see it once approved.");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card">
      <h2>Submit an interview question</h2>
      <form onSubmit={submit}>
        <label>Domain</label>
        <select value={form.domain_id} onChange={(e) => set("domain_id", e.target.value)} required>
          <option value="">Select…</option>
          {domains.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>
        <label>Company</label>
        <select value={form.company_id} onChange={(e) => set("company_id", e.target.value)} required>
          <option value="">Select…</option>
          {companies.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <div className="row mt">
          <input placeholder="Company not listed? Add it" value={newCompany} onChange={(e) => setNewCompany(e.target.value)} style={{ flex: 1 }} />
          <button type="button" className="secondary" disabled={!newCompany.trim()} onClick={addCompany}>Add company</button>
        </div>
        <label>Role / job title</label>
        <input value={form.role_title} onChange={(e) => set("role_title", e.target.value)} maxLength={100} required placeholder="e.g. Backend Developer Intern" />
        <label>Question (min 20 characters)</label>
        <textarea value={form.question_text} onChange={(e) => set("question_text", e.target.value)} minLength={20} required />
        <div className="row">
          <div style={{ flex: 1 }}>
            <label>Type</label>
            <select value={form.question_type} onChange={(e) => set("question_type", e.target.value)}>
              <option value="technical">Technical</option>
              <option value="behavioural">Behavioural</option>
              <option value="hr">HR</option>
              <option value="case_study">Case study</option>
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label>Difficulty</label>
            <select value={form.difficulty} onChange={(e) => set("difficulty", e.target.value)}>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
          <div style={{ flex: 1 }}>
            <label>When asked</label>
            <input type="month" value={form.asked_month} onChange={(e) => set("asked_month", e.target.value)} required />
          </div>
        </div>
        <label>Notes (optional)</label>
        <textarea value={form.notes} onChange={(e) => set("notes", e.target.value)} maxLength={500} />
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
