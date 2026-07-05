import { FormEvent, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";

// Supabase recovery links redirect with #access_token=...&type=recovery
export default function ResetPassword() {
  const token = useMemo(() => {
    const params = new URLSearchParams(window.location.hash.slice(1));
    return params.get("access_token") ?? "";
  }, []);
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const res = await api<{ message: string }>("/auth/reset-password", {
        method: "POST", body: { password }, token,
      });
      setMessage(res.message);
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (!token)
    return (
      <div className="page-narrow">
        <div className="card center">
          <h1>Invalid reset link</h1>
          <p className="muted">This link is missing its token. <Link to="/forgot-password">Request a new one</Link>.</p>
        </div>
      </div>
    );

  return (
    <div className="page-narrow">
      <div className="card">
        <h1>Set a new password</h1>
        <form onSubmit={submit}>
          <label>New password (min 8 characters)</label>
          <input type="password" minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} required />
          {message && <p className="success">{message} <Link to="/login">Log in</Link></p>}
          {error && <p className="error">{error}</p>}
          <button className="mt" style={{ width: "100%" }}>Reset password</button>
        </form>
      </div>
    </div>
  );
}
