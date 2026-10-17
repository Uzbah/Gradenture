import { FormEvent, useEffect, useState } from "react";
import { api, MySubmissions } from "../api";
import { useAuth } from "../auth";
import { GOALS, SKILL_LEVELS, useLookups } from "../lookups";

const STATUS_BADGE: Record<string, string> = {
  approved: "easy",
  pending: "medium",
  needs_edit: "medium",
  rejected: "hard",
};
const STATUS_LABEL: Record<string, string> = {
  approved: "Live",
  pending: "In review",
  needs_edit: "Edit requested",
  rejected: "Not approved",
};

export default function Profile() {
  const [tab, setTab] = useState<"submissions" | "profile" | "password">("submissions");
  return (
    <>
      <h1>Profile</h1>
      <div className="tabs">
        <button className={tab === "submissions" ? "active" : ""} onClick={() => setTab("submissions")}>My submissions</button>
        <button className={tab === "profile" ? "active" : ""} onClick={() => setTab("profile")}>Profile details</button>
        <button className={tab === "password" ? "active" : ""} onClick={() => setTab("password")}>Password</button>
      </div>
      {tab === "submissions" && <Submissions />}
      {tab === "profile" && <ProfileForm />}
      {tab === "password" && <PasswordForm />}
    </>
  );
}

function Submissions() {
  const { companyName } = useLookups();
  const [data, setData] = useState<MySubmissions | null>(null);
  const [editing, setEditing] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const load = () =>
    api<{ data: MySubmissions }>("/users/me/submissions")
      .then((r) => setData(r.data))
      .catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  if (error && !data) return <p className="error">{error}</p>;
  if (!data) return <p className="muted">Loading…</p>;

  const all = [...data.questions, ...data.reviews];
  const count = (s: string) => all.filter((x) => x.status === s).length;

  const resubmit = async (kind: "questions" | "reviews", id: string, body: object) => {
    setError(""); setMessage("");
    try {
      await api(`/${kind}/${id}`, { method: "PATCH", body });
      setEditing(null);
      setMessage("Resubmitted. A moderator will review it again.");
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <>
      <div className="stat-grid">
        <div className="stat"><div className="num">{all.length}</div><div className="label">Submitted</div></div>
        <div className="stat"><div className="num">{count("pending")}</div><div className="label">In review</div></div>
        <div className="stat"><div className="num">{count("needs_edit")}</div><div className="label">Edit requested</div></div>
        <div className="stat"><div className="num">{count("approved")}</div><div className="label">Live contributions</div></div>
      </div>
      {message && <p className="success">{message}</p>}
      {error && <p className="error">{error}</p>}

      <h2 className="mt">Questions ({data.questions.length})</h2>
      {data.questions.length === 0 && <p className="muted">You haven't submitted any questions yet.</p>}
      {data.questions.map((q) => (
        <div className="card" key={q.id}>
          <Header status={q.status} company={companyName(q.company_id)} role={q.role_title} date={q.created_at} />
          {editing === q.id ? (
            <EditForm
              minLength={20}
              initial={q.question_text}
              initialNotes={q.notes ?? ""}
              onCancel={() => setEditing(null)}
              onSave={(text, notes) =>
                resubmit("questions", q.id, { question_text: text, notes: notes || null })}
            />
          ) : (
            <p>{q.question_text}</p>
          )}
          <Footer note={q.admin_note} status={q.status} editing={editing === q.id} onEdit={() => setEditing(q.id)} />
        </div>
      ))}

      <h2 className="mt">Reviews ({data.reviews.length})</h2>
      {data.reviews.length === 0 && <p className="muted">You haven't written any reviews yet.</p>}
      {data.reviews.map((r) => (
        <div className="card" key={r.id}>
          <Header status={r.status} company={companyName(r.company_id)} role={r.role_title} date={r.created_at} />
          {editing === r.id ? (
            <EditForm
              minLength={50}
              initial={r.review_text}
              onCancel={() => setEditing(null)}
              onSave={(text) => resubmit("reviews", r.id, { review_text: text })}
            />
          ) : (
            <p>{r.review_text}</p>
          )}
          <Footer note={r.admin_note} status={r.status} editing={editing === r.id} onEdit={() => setEditing(r.id)} />
        </div>
      ))}
    </>
  );
}

function Header({ status, company, role, date }: { status: string; company: string; role: string; date: string }) {
  return (
    <div className="row" style={{ marginBottom: "0.4rem" }}>
      <span className={`badge ${STATUS_BADGE[status] ?? ""}`}>{STATUS_LABEL[status] ?? status}</span>
      <span className="badge">{company}</span>
      <span className="muted">{role} · {new Date(date).toLocaleDateString()}</span>
    </div>
  );
}

function Footer({ note, status, editing, onEdit }: {
  note?: string; status: string; editing: boolean; onEdit: () => void;
}) {
  return (
    <>
      {note && status !== "approved" && <p className="muted mt"><strong>Moderator note:</strong> {note}</p>}
      {status === "needs_edit" && !editing && (
        <div className="row mt"><button className="small" onClick={onEdit}>Edit &amp; resubmit</button></div>
      )}
    </>
  );
}

function EditForm({ initial, initialNotes, minLength, onSave, onCancel }: {
  initial: string;
  initialNotes?: string;
  minLength: number;
  onSave: (text: string, notes: string) => void;
  onCancel: () => void;
}) {
  const [text, setText] = useState(initial);
  const [notes, setNotes] = useState(initialNotes ?? "");
  return (
    <form className="mt" onSubmit={(e) => { e.preventDefault(); onSave(text, notes); }}>
      <textarea value={text} onChange={(e) => setText(e.target.value)} minLength={minLength} required />
      {initialNotes !== undefined && (
        <>
          <label>Notes (optional)</label>
          <textarea value={notes} onChange={(e) => setNotes(e.target.value)} maxLength={500} />
        </>
      )}
      <div className="row mt">
        <button type="submit" className="small">Resubmit for review</button>
        <button type="button" className="small secondary" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  );
}

function ProfileForm() {
  const { user, refresh } = useAuth();
  const { domains } = useLookups();
  const [form, setForm] = useState({
    domain_id: user?.domain_id ?? "",
    skill_level: user?.skill_level ?? "beginner",
    goal: user?.goal ?? "internship",
    university: user?.university ?? "",
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k: keyof typeof form) => (e: { target: { value: string } }) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(""); setMessage(""); setBusy(true);
    try {
      // Same fields as onboarding, so the onboarding endpoint is the profile update.
      await api("/users/onboarding", { method: "PATCH", body: form });
      await refresh();
      setMessage("Profile saved.");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="card" style={{ maxWidth: 520 }}>
      <form onSubmit={submit}>
        <label>Email</label>
        <input value={user?.email ?? ""} disabled />
        <label>Primary domain</label>
        <select value={form.domain_id} onChange={set("domain_id")} required>
          <option value="">Select a domain…</option>
          {domains.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>
        <p className="muted" style={{ marginTop: "0.3rem" }}>
          Your Prep roadmap follows this domain. Progress in other domains is kept.
        </p>
        <label>Skill level</label>
        <select value={form.skill_level} onChange={set("skill_level")}>
          {SKILL_LEVELS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <label>Goal</label>
        <select value={form.goal} onChange={set("goal")}>
          {GOALS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
        </select>
        <label>University</label>
        <input value={form.university} onChange={set("university")} minLength={2} maxLength={100} required />
        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error}</p>}
        <button className="mt" disabled={busy}>{busy ? "Saving…" : "Save changes"}</button>
      </form>
    </div>
  );
}

function PasswordForm() {
  const [current, setCurrent] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(""); setMessage("");
    if (password !== confirm) return setError("Passwords don't match.");
    try {
      await api("/auth/reset-password", {
        method: "POST", body: { password, current_password: current },
      });
      setCurrent(""); setPassword(""); setConfirm("");
      setMessage("Password updated.");
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="card" style={{ maxWidth: 520 }}>
      <form onSubmit={submit}>
        <label>Current password</label>
        <input type="password" autoComplete="current-password" value={current}
               onChange={(e) => setCurrent(e.target.value)} required />
        <label>New password (min 8 characters)</label>
        <input type="password" minLength={8} maxLength={128} value={password}
               onChange={(e) => setPassword(e.target.value)} required />
        <label>Confirm new password</label>
        <input type="password" minLength={8} maxLength={128} value={confirm}
               onChange={(e) => setConfirm(e.target.value)} required />
        {message && <p className="success">{message}</p>}
        {error && <p className="error">{error}</p>}
        <button className="mt">Update password</button>
      </form>
    </div>
  );
}
