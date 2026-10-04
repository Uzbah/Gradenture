import { FormEvent, useEffect, useState } from "react";
import { api, ApiResponse, Company, CompanyEdit, CompanyManager, Flag, PageData, Question, Review, User } from "../api";
import { useAuth } from "../auth";
import { useLookups } from "../lookups";

export default function Admin() {
  const [tab, setTab] = useState<"queue" | "flags" | "companies" | "users">("queue");
  return (
    <>
      <h1>Admin Panel</h1>
      <div className="tabs">
        <button className={tab === "queue" ? "active" : ""} onClick={() => setTab("queue")}>Moderation queue</button>
        <button className={tab === "flags" ? "active" : ""} onClick={() => setTab("flags")}>Flags</button>
        <button className={tab === "companies" ? "active" : ""} onClick={() => setTab("companies")}>Companies</button>
        <button className={tab === "users" ? "active" : ""} onClick={() => setTab("users")}>Users</button>
      </div>
      {tab === "queue" && <Queue />}
      {tab === "flags" && <Flags />}
      {tab === "companies" && <CompaniesAdmin />}
      {tab === "users" && <Users />}
    </>
  );
}

function Queue() {
  const { domainName, companyName } = useLookups();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [edits, setEdits] = useState<CompanyEdit[]>([]);
  const [error, setError] = useState("");

  const load = () =>
    api<ApiResponse<{ questions: Question[]; reviews: Review[]; companies: Company[] }>>("/admin/queue")
      .then((r) => { setQuestions(r.data.questions); setReviews(r.data.reviews); setCompanies(r.data.companies); })
      .catch((e) => setError(e.message));

  const loadEdits = () =>
    api<ApiResponse<CompanyEdit[]>>("/admin/company-edits")
      .then((r) => setEdits(r.data))
      .catch(() => {});

  useEffect(() => { load(); loadEdits(); }, []);

  const decideEdit = async (id: string, status: "approved" | "rejected") => {
    let admin_note: string | null = null;
    if (status === "rejected") admin_note = window.prompt("Why is this rejected?") ?? "";
    try {
      await api(`/admin/company-edits/${id}`, { method: "PATCH", body: { status, admin_note } });
      loadEdits();
    } catch (err: any) { setError(err.message); }
  };

  const approveCompany = async (id: string) => {
    try {
      await api(`/admin/companies/${id}`, { method: "PATCH" });
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const moderate = async (kind: "questions" | "reviews", id: string, status: string) => {
    let admin_note: string | null = null;
    if (status !== "approved") {
      admin_note = window.prompt(`Note to the submitter (${status}):`) ?? "";
    }
    try {
      await api(`/admin/${kind}/${id}`, { method: "PATCH", body: { status, admin_note } });
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const Actions = ({ kind, id }: { kind: "questions" | "reviews"; id: string }) => (
    <div className="row mt">
      <button className="small" onClick={() => moderate(kind, id, "approved")}>Approve</button>
      <button className="small danger" onClick={() => moderate(kind, id, "rejected")}>Reject</button>
      <button className="small secondary" onClick={() => moderate(kind, id, "needs_edit")}>Request edit</button>
    </div>
  );

  return (
    <>
      {error && <p className="error">{error}</p>}
      <h2>Pending companies ({companies.length})</h2>
      {companies.length === 0 && <p className="muted">Nothing to approve 🎉</p>}
      {companies.map((c) => (
        <div className="card" key={c.id}>
          <div className="row" style={{ marginBottom: "0.4rem" }}>
            <strong>{c.name}</strong>
            {c.industry && <span className="badge">{c.industry}</span>}
          </div>
          {c.website && <p className="muted">{c.website}</p>}
          <div className="row mt">
            <button className="small" onClick={() => approveCompany(c.id)}>Approve</button>
          </div>
        </div>
      ))}

      <h2 className="mt">Pending profile edits ({edits.length})</h2>
      {edits.length === 0 && <p className="muted">No profile changes awaiting review.</p>}
      {edits.map((ed) => (
        <div className="card" key={ed.id}>
          <div className="row" style={{ marginBottom: "0.4rem" }}>
            <strong>{ed.companies?.name ?? "Company"}</strong>
            <span className="muted">{new Date(ed.created_at).toLocaleDateString()}</span>
          </div>
          <table>
            <tbody>
              {Object.entries(ed.changes).map(([field, value]) => (
                <tr key={field}><td>{field}</td><td>{String(value)}</td></tr>
              ))}
            </tbody>
          </table>
          <div className="row mt">
            <button className="small" onClick={() => decideEdit(ed.id, "approved")}>Approve</button>
            <button className="small danger" onClick={() => decideEdit(ed.id, "rejected")}>Reject</button>
          </div>
        </div>
      ))}

      <h2 className="mt">Pending questions ({questions.length})</h2>
      {questions.length === 0 && <p className="muted">Queue is empty 🎉</p>}
      {questions.map((q) => (
        <div className="card" key={q.id}>
          <div className="row" style={{ marginBottom: "0.4rem" }}>
            <span className="badge">{domainName(q.domain_id)}</span>
            <span className="badge">{companyName(q.company_id)}</span>
            <span className={`badge ${q.difficulty}`}>{q.difficulty}</span>
            <span className="muted">{q.role_title} · {new Date(q.created_at).toLocaleDateString()}</span>
          </div>
          <p>{q.question_text}</p>
          {q.notes && <p className="muted">Notes: {q.notes}</p>}
          <Actions kind="questions" id={q.id} />
        </div>
      ))}

      <h2 className="mt">Pending reviews ({reviews.length})</h2>
      {reviews.length === 0 && <p className="muted">Queue is empty 🎉</p>}
      {reviews.map((r) => (
        <div className="card" key={r.id}>
          <div className="row" style={{ marginBottom: "0.4rem" }}>
            <span className="badge">{companyName(r.company_id)}</span>
            {r.outcome && <span className="badge">{r.outcome}</span>}
            <span className="muted">{r.role_title} · {new Date(r.created_at).toLocaleDateString()}</span>
          </div>
          <p>{r.review_text}</p>
          <Actions kind="reviews" id={r.id} />
        </div>
      ))}
    </>
  );
}

function Flags() {
  const { companyName } = useLookups();
  const [flags, setFlags] = useState<Flag[]>([]);
  const [error, setError] = useState("");

  const load = () =>
    api<ApiResponse<Flag[]>>("/admin/flags").then((r) => setFlags(r.data)).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const act = async (id: string, status: "resolved" | "dismissed") => {
    setError("");
    try {
      await api(`/admin/flags/${id}`, { method: "PATCH", body: { status } });
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <>
      {error && <p className="error">{error}</p>}
      <h2>Open flags ({flags.length})</h2>
      {flags.length === 0 && <p className="muted">No open flags 🎉</p>}
      {flags.map((f) => (
        <div className="card" key={f.id}>
          <div className="row" style={{ marginBottom: "0.4rem" }}>
            <span className="badge">{f.content_type}</span>
            {f.content && <span className="badge">{companyName(f.content.company_id)}</span>}
            <span className="muted">{new Date(f.created_at).toLocaleDateString()}</span>
          </div>
          <p><strong>Reason:</strong> {f.reason}</p>
          {f.content ? (
            <p className="muted">{f.content.question_text ?? f.content.review_text}</p>
          ) : (
            <p className="muted">Content no longer exists.</p>
          )}
          <div className="row mt">
            <button className="small" onClick={() => act(f.id, "resolved")}>Resolve</button>
            <button className="small secondary" onClick={() => act(f.id, "dismissed")}>Dismiss</button>
          </div>
        </div>
      ))}
    </>
  );
}

function CompaniesAdmin() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [q, setQ] = useState("");
  const [editing, setEditing] = useState<Company | null>(null);
  const [creating, setCreating] = useState(false);
  const [merging, setMerging] = useState<Company | null>(null);
  const [managing, setManaging] = useState<Company | null>(null);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");

  const load = () => {
    const params = new URLSearchParams({ size: "50" });
    if (q.trim()) params.set("q", q.trim());
    api<ApiResponse<PageData<Company>>>(`/admin/companies?${params}`)
      .then((r) => setCompanies(r.data.items))
      .catch((e) => setError(e.message));
  };
  useEffect(() => {
    const t = setTimeout(load, 250);
    return () => clearTimeout(t);
  }, [q]);

  const save = async (body: Partial<Company>, id?: string) => {
    setError(""); setInfo("");
    try {
      if (id) await api(`/admin/companies/${id}`, { method: "PATCH", body });
      else await api("/admin/companies", { method: "POST", body });
      setInfo(id ? "Company updated" : "Company created");
      setEditing(null); setCreating(false);
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const merge = async (from: Company, intoId: string) => {
    const into = companies.find((c) => c.id === intoId);
    if (!into || !window.confirm(
      `Merge "${from.name}" into "${into.name}"? All its questions and reviews move across and "${from.name}" is deleted. This cannot be undone.`
    )) return;
    setError(""); setInfo("");
    try {
      const r = await api<ApiResponse<unknown>>(`/admin/companies/${from.id}/merge`,
        { method: "POST", body: { into_id: intoId } });
      setInfo(r.msg);
      setMerging(null);
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <>
      {error && <p className="error">{error}</p>}
      {info && <p className="success">{info}</p>}

      <div className="row" style={{ justifyContent: "space-between", marginBottom: "0.75rem" }}>
        <input placeholder="Search companies…" value={q}
               onChange={(e) => setQ(e.target.value)} style={{ maxWidth: 280 }} />
        <button className="small" onClick={() => { setCreating(true); setEditing(null); }}>
          Add company
        </button>
      </div>

      {creating && <CompanyForm onSave={(b) => save(b)} onCancel={() => setCreating(false)} />}

      <div className="card">
        <table>
          <thead>
            <tr><th>Name</th><th>Industry</th><th>Status</th><th>Actions</th></tr>
          </thead>
          <tbody>
            {companies.map((c) => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td>{c.industry ?? "—"}</td>
                <td>
                  {c.status === "approved"
                    ? <span className="badge easy">approved</span>
                    : <span className="badge">pending</span>}
                </td>
                <td>
                  <div className="row">
                    <button className="small secondary"
                            onClick={() => { setEditing(c); setCreating(false); }}>Edit</button>
                    {c.status !== "approved" && (
                      <button className="small" onClick={() => save({ status: "approved" }, c.id)}>
                        Approve
                      </button>
                    )}
                    <button className="small secondary"
                            onClick={() => setMerging(merging?.id === c.id ? null : c)}>Merge</button>
                    <button className="small secondary"
                            onClick={() => setManaging(managing?.id === c.id ? null : c)}>Managers</button>
                  </div>
                  {managing?.id === c.id && <Managers company={c} onError={setError} />}
                  {merging?.id === c.id && (
                    <select defaultValue="" style={{ marginTop: "0.4rem" }}
                            onChange={(e) => e.target.value && merge(c, e.target.value)}>
                      <option value="">Merge into…</option>
                      {companies.filter((o) => o.id !== c.id).map((o) => (
                        <option key={o.id} value={o.id}>{o.name}</option>
                      ))}
                    </select>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {editing && (
        <CompanyForm company={editing} onSave={(b) => save(b, editing.id)}
                     onCancel={() => setEditing(null)} />
      )}
    </>
  );
}

function Managers({ company, onError }: { company: Company; onError: (m: string) => void }) {
  const [managers, setManagers] = useState<CompanyManager[]>([]);
  const [email, setEmail] = useState("");

  const load = () =>
    api<ApiResponse<CompanyManager[]>>(`/admin/companies/${company.id}/managers`)
      .then((r) => setManagers(r.data))
      .catch((e) => onError(e.message));
  useEffect(() => { load(); }, [company.id]);

  const grant = async (e: FormEvent) => {
    e.preventDefault();
    try {
      await api(`/admin/companies/${company.id}/managers`, { method: "POST", body: { email } });
      setEmail(""); load();
    } catch (err: any) { onError(err.message); }
  };

  const revoke = async (userId: string) => {
    try {
      await api(`/admin/companies/${company.id}/managers/${userId}`, { method: "DELETE" });
      load();
    } catch (err: any) { onError(err.message); }
  };

  return (
    <div className="card mt">
      <h3>Managers of {company.name}</h3>
      <p className="muted">
        Managers may propose profile changes only. They cannot moderate the
        questions or reviews written about this company.
      </p>
      {managers.length === 0 && <p className="muted">No managers assigned.</p>}
      {managers.map((m) => (
        <div className="row mt" key={m.user_id} style={{ justifyContent: "space-between" }}>
          <span>{m.users?.email ?? m.user_id}</span>
          <button className="small danger" onClick={() => revoke(m.user_id)}>Revoke</button>
        </div>
      ))}
      <form className="row mt" onSubmit={grant}>
        <input type="email" required placeholder="user@example.com"
               value={email} onChange={(e) => setEmail(e.target.value)} />
        <button className="small" type="submit">Grant access</button>
      </form>
    </div>
  );
}

function CompanyForm({ company, onSave, onCancel }: {
  company?: Company;
  onSave: (body: Partial<Company>) => void;
  onCancel: () => void;
}) {
  const [form, setForm] = useState({
    name: company?.name ?? "",
    industry: company?.industry ?? "",
    website: company?.website ?? "",
    logo_url: company?.logo_url ?? "",
  });
  const set = (k: keyof typeof form) => (e: { target: { value: string } }) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  return (
    <form className="card mt" onSubmit={(e) => {
      e.preventDefault();
      // drop blanks so PATCH never clears a field the admin left untouched
      onSave(Object.fromEntries(Object.entries(form).filter(([, v]) => v !== "")));
    }}>
      <h3>{company ? `Edit ${company.name}` : "New company"}</h3>
      <div className="filters mt">
        <input required placeholder="Name" value={form.name} onChange={set("name")} />
        <input placeholder="Industry" value={form.industry} onChange={set("industry")} />
        <input type="url" placeholder="Website" value={form.website} onChange={set("website")} />
        <input type="url" placeholder="Logo URL" value={form.logo_url} onChange={set("logo_url")} />
      </div>
      <div className="row mt">
        <button type="submit">{company ? "Save changes" : "Create"}</button>
        <button type="button" className="secondary" onClick={onCancel}>Cancel</button>
      </div>
    </form>
  );
}

function Users() {
  const { user: me } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const isSuper = me?.role === "super_admin";

  const load = () =>
    api<ApiResponse<PageData<User>>>("/admin/users?size=50")
      .then((r) => setUsers(r.data.items)).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const setRole = async (id: string, role: string) => {
    setError(""); setInfo("");
    try {
      await api(`/admin/users/${id}/role`, { method: "PATCH", body: { role } });
      setInfo("Role updated");
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const suspend = async (id: string, email: string) => {
    if (!window.confirm(`Suspend ${email}? They will no longer be able to log in.`)) return;
    setError(""); setInfo("");
    try {
      await api(`/admin/users/${id}/suspend`, { method: "PATCH" });
      setInfo("User suspended");
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const unsuspend = async (id: string) => {
    setError(""); setInfo("");
    try {
      await api(`/admin/users/${id}/unsuspend`, { method: "PATCH" });
      setInfo("User unsuspended");
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="card">
      {error && <p className="error">{error}</p>}
      {info && <p className="success">{info}</p>}
      <table>
        <thead>
          <tr><th>Email</th><th>Role</th><th>Onboarded</th><th>Status</th><th>Actions</th></tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.email}</td>
              <td>
                {isSuper && u.id !== me?.id ? (
                  <select value={u.role} style={{ width: "auto" }} onChange={(e) => setRole(u.id, e.target.value)}>
                    <option value="user">user</option>
                    <option value="admin">admin</option>
                    <option value="super_admin">super_admin</option>
                  </select>
                ) : (
                  u.role
                )}
              </td>
              <td>{u.onboarding_complete ? "✓" : "—"}</td>
              <td>{u.suspended_at ? <span className="badge hard">suspended</span> : "active"}</td>
              <td>
                {u.id !== me?.id && (
                  u.suspended_at ? (
                    <button className="small secondary" onClick={() => unsuspend(u.id)}>Unsuspend</button>
                  ) : (
                    <button className="small danger" onClick={() => suspend(u.id, u.email)}>Suspend</button>
                  )
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
