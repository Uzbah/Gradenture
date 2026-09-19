import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiResponse, Application, PageData, Question } from "../api";
import { useAuth } from "../auth";

export default function Dashboard() {
  const { user } = useAuth();
  const [apps, setApps] = useState<Application[]>([]);
  const [questionCount, setQuestionCount] = useState<number | null>(null);
  const [recent, setRecent] = useState<Question[]>([]);
  const [prepScore, setPrepScore] = useState<number | null>(null);

  useEffect(() => {
    api<ApiResponse<PageData<Application>>>("/applications/?size=50")
      .then((r) => setApps(r.data.items)).catch(() => {});
    api<ApiResponse<PageData<Question>>>("/questions/?size=5")
      .then((r) => { setRecent(r.data.items); setQuestionCount(r.data.total); })
      .catch(() => {});
    api<ApiResponse<{ score: number }>>("/prep/").then((r) => setPrepScore(r.data.score)).catch(() => {});
  }, []);

  const count = (s: string) => apps.filter((a) => a.status === s).length;

  return (
    <>
      <h1>Welcome back{user?.university ? `, ${user.email.split("@")[0]}` : ""} 👋</h1>
      <div className="stat-grid">
        <div className="stat"><div className="num">{count("applied")}</div><div className="label">Applied</div></div>
        <div className="stat"><div className="num">{count("interview")}</div><div className="label">Interviews</div></div>
        <div className="stat"><div className="num">{count("offer")}</div><div className="label">Offers</div></div>
        <div className="stat"><div className="num">{questionCount ?? "—"}</div><div className="label">Community questions</div></div>
        <div className="stat"><div className="num">{prepScore !== null ? `${prepScore}%` : "—"}</div><div className="label"><Link to="/prep">Preparedness</Link></div></div>
      </div>
      <div className="card">
        <h2>Latest interview questions</h2>
        {recent.length === 0 && <p className="muted">No approved questions yet. <Link to="/questions">Be the first to submit one</Link>.</p>}
        {recent.map((q) => (
          <p key={q.id} style={{ marginBottom: "0.5rem" }}>
            <span className={`badge ${q.difficulty}`}>{q.difficulty}</span>{" "}
            {q.question_text.slice(0, 120)}{q.question_text.length > 120 ? "…" : ""}
            <span className="muted"> — {q.role_title}</span>
          </p>
        ))}
        <p className="mt"><Link to="/questions">Browse all questions →</Link></p>
      </div>
      <div className="card">
        <h2>Quick actions</h2>
        <div className="row">
          <Link to="/questions"><button className="secondary">Submit a question</button></Link>
          <Link to="/reviews"><button className="secondary">Write a review</button></Link>
          <Link to="/applications"><button className="secondary">Track an application</button></Link>
          <Link to="/resume"><button className="secondary">Analyze my resume</button></Link>
        </div>
      </div>
    </>
  );
}
