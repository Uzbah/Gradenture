import { useEffect, useState } from "react";
import { api, Question, Review, User } from "../api";
import { useAuth } from "../auth";
import { useLookups } from "../lookups";

export default function Admin() {
  const [tab, setTab] = useState<"queue" | "users">("queue");
  return (
    <>
      <h1>Admin Panel</h1>
      <div className="tabs">
        <button className={tab === "queue" ? "active" : ""} onClick={() => setTab("queue")}>Moderation queue</button>
        <button className={tab === "users" ? "active" : ""} onClick={() => setTab("users")}>Users</button>
      </div>
      {tab === "queue" ? <Queue /> : <Users />}
    </>
  );
}

function Queue() {
  const { domainName, companyName } = useLookups();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [error, setError] = useState("");

  const load = () =>
    api<{ data: { questions: Question[]; reviews: Review[] } }>("/admin/queue")
      .then((r) => { setQuestions(r.data.questions); setReviews(r.data.reviews); })
      .catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

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
      <h2>Pending questions ({questions.length})</h2>
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

function Users() {
  const { user: me } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const isSuper = me?.role === "super_admin";

  const load = () =>
    api<{ data: User[] }>("/admin/users?limit=50").then((r) => setUsers(r.data)).catch((e) => setError(e.message));
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
          <tr><th>Email</th><th>Role</th><th>Onboarded</th><th>Actions</th></tr>
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
              <td>
                {u.id !== me?.id && (
                  <button className="small danger" onClick={() => suspend(u.id, u.email)}>Suspend</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
