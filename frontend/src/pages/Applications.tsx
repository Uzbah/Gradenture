import { FormEvent, useEffect, useState } from "react";
import { api, Application } from "../api";

const COLUMNS: { key: Application["status"]; label: string }[] = [
  { key: "applied", label: "Applied" },
  { key: "interview", label: "Interview" },
  { key: "offer", label: "Offer" },
  { key: "rejected", label: "Rejected" },
  { key: "closed", label: "Closed" },
];

export default function Applications() {
  const [apps, setApps] = useState<Application[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState("");

  const load = () =>
    api<{ data: Application[] }>("/applications/?limit=50").then((r) => setApps(r.data)).catch(() => {});
  useEffect(() => { load(); }, []);

  const move = async (app: Application, status: Application["status"]) => {
    setApps((a) => a.map((x) => (x.id === app.id ? { ...x, status } : x)));
    try {
      await api(`/applications/${app.id}`, { method: "PATCH", body: { status } });
    } catch (err: any) {
      setError(err.message);
      load();
    }
  };

  const remove = async (app: Application) => {
    if (!window.confirm(`Delete application to ${app.company_name}?`)) return;
    try {
      await api(`/applications/${app.id}`, { method: "DELETE" });
      setApps((a) => a.filter((x) => x.id !== app.id));
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <>
      <div className="row" style={{ justifyContent: "space-between", marginBottom: "1rem" }}>
        <h1 style={{ margin: 0 }}>Opportunity Tracker</h1>
        <button onClick={() => setShowForm((s) => !s)}>{showForm ? "Close" : "Add application"}</button>
      </div>
      {showForm && <AppForm onDone={() => { setShowForm(false); load(); }} />}
      {error && <p className="error">{error}</p>}

      <div className="kanban">
        {COLUMNS.map((col) => (
          <div className="col" key={col.key}>
            <h3>{col.label} ({apps.filter((a) => a.status === col.key).length})</h3>
            {apps.filter((a) => a.status === col.key).map((app) => (
              <div className="card" key={app.id}>
                <strong>{app.company_name}</strong>
                <div className="muted">{app.role_title}</div>
                {app.deadline && <div className="muted">Deadline: {app.deadline}</div>}
                {app.job_url && <div><a href={app.job_url} target="_blank" rel="noreferrer">Job link</a></div>}
                {app.notes && <div className="muted" style={{ fontSize: "0.8rem" }}>{app.notes}</div>}
                <div className="row mt">
                  <select
                    value={app.status}
                    style={{ width: "auto", fontSize: "0.8rem", padding: "0.2rem 0.4rem" }}
                    onChange={(e) => move(app, e.target.value as Application["status"])}
                  >
                    {COLUMNS.map((c) => <option key={c.key} value={c.key}>{c.label}</option>)}
                  </select>
                  <button className="ghost small" onClick={() => remove(app)}>✕</button>
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </>
  );
}

function AppForm({ onDone }: { onDone: () => void }) {
  const [form, setForm] = useState({
    company_name: "", role_title: "", applied_date: "", deadline: "", job_url: "", notes: "",
  });
  const [error, setError] = useState("");
  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await api("/applications/", {
        method: "POST",
        body: {
          company_name: form.company_name,
          role_title: form.role_title,
          applied_date: form.applied_date || null,
          deadline: form.deadline || null,
          job_url: form.job_url || null,
          notes: form.notes || null,
        },
      });
      onDone();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="card">
      <h2>New application</h2>
      <form onSubmit={submit}>
        <div className="row">
          <div style={{ flex: 1 }}>
            <label>Company</label>
            <input value={form.company_name} onChange={(e) => set("company_name", e.target.value)} required maxLength={100} />
          </div>
          <div style={{ flex: 1 }}>
            <label>Role title</label>
            <input value={form.role_title} onChange={(e) => set("role_title", e.target.value)} required maxLength={100} />
          </div>
        </div>
        <div className="row">
          <div style={{ flex: 1 }}>
            <label>Applied date</label>
            <input type="date" value={form.applied_date} onChange={(e) => set("applied_date", e.target.value)} />
          </div>
          <div style={{ flex: 1 }}>
            <label>Deadline</label>
            <input type="date" value={form.deadline} onChange={(e) => set("deadline", e.target.value)} />
          </div>
        </div>
        <label>Job URL (optional)</label>
        <input type="url" value={form.job_url} onChange={(e) => set("job_url", e.target.value)} />
        <label>Notes (optional)</label>
        <textarea value={form.notes} onChange={(e) => set("notes", e.target.value)} maxLength={1000} />
        {error && <p className="error">{error}</p>}
        <button className="mt">Add</button>
      </form>
    </div>
  );
}
