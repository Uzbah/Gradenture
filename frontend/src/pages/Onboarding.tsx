import { FormEvent, useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { api, Domain } from "../api";
import { useAuth } from "../auth";

export default function Onboarding() {
  const { user, loading, refresh } = useAuth();
  const nav = useNavigate();
  const [domains, setDomains] = useState<Domain[]>([]);
  const [domainId, setDomainId] = useState("");
  const [skillLevel, setSkillLevel] = useState("beginner");
  const [goal, setGoal] = useState("internship");
  const [university, setUniversity] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api<{ data: Domain[] }>("/domains").then((res) => setDomains(res.data)).catch(() => {});
  }, []);

  if (loading) return <div className="page center muted">Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (user.onboarding_complete) return <Navigate to="/" replace />;

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      await api("/users/onboarding", {
        method: "PATCH",
        body: { domain_id: domainId, skill_level: skillLevel, goal, university },
      });
      await refresh();
      nav("/");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="page-narrow">
      <div className="card">
        <h1>Welcome! Tell us about yourself</h1>
        <form onSubmit={submit}>
          <label>Primary domain</label>
          <select value={domainId} onChange={(e) => setDomainId(e.target.value)} required>
            <option value="">Select a domain…</option>
            {domains.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
          <label>Skill level</label>
          <select value={skillLevel} onChange={(e) => setSkillLevel(e.target.value)}>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
          <label>Goal</label>
          <select value={goal} onChange={(e) => setGoal(e.target.value)}>
            <option value="internship">Internship hunting</option>
            <option value="first_job">First full-time job</option>
            <option value="switch_career">Switch career</option>
            <option value="level_up">General upskilling</option>
          </select>
          <label>University</label>
          <input value={university} onChange={(e) => setUniversity(e.target.value)} minLength={2} maxLength={100} required placeholder="e.g. FAST-NUCES Karachi" />
          {error && <p className="error">{error}</p>}
          <button className="mt" disabled={busy} style={{ width: "100%" }}>
            {busy ? "Saving…" : "Complete onboarding"}
          </button>
        </form>
      </div>
    </div>
  );
}
