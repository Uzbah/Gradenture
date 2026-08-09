import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import { api } from "../api";
import Logo from "../components/Logo";

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(""); setInfo(""); setBusy(true);
    try {
      await login(email, password);
      nav("/");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  const resend = async () => {
    setError("");
    const res = await api<{ message: string }>("/auth/resend-verification", {
      method: "POST", body: { email },
    });
    setInfo(res.message);
  };

  return (
    <div className="page-narrow">
      <Logo />
      <div className="card">
        <h1>Log in to CareerBridge</h1>
        <form onSubmit={submit}>
          <label>Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <label>Password</label>
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          {error && <p className="error">{error}</p>}
          {error.toLowerCase().includes("verify") && (
            <button type="button" className="ghost" onClick={resend}>Resend verification email</button>
          )}
          {info && <p className="success">{info}</p>}
          <button className="mt" disabled={busy} style={{ width: "100%" }}>
            {busy ? "Logging in…" : "Log in"}
          </button>
        </form>
        <p className="muted mt">
          No account? <Link to="/register">Register</Link> · <Link to="/forgot-password">Forgot password?</Link>
        </p>
      </div>
    </div>
  );
}
