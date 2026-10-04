import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import Logo from "../components/Logo";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      await api("/auth/register", { method: "POST", body: { email, password } });
      setDone(true);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  if (done)
    return (
      <div className="page-narrow">
        <Logo />
        <div className="card center">
          <h1>Check your email</h1>
          <p className="muted">
            We sent a verification link to <strong>{email}</strong>. Verify your email, then{" "}
            <Link to="/login">log in</Link>.
          </p>
        </div>
      </div>
    );

  return (
    <div className="page-narrow">
      <Logo />
      <div className="card">
        <h1>Create your account</h1>
        <form onSubmit={submit}>
          <label>Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <label>Password (min 8 characters)</label>
          <input type="password" minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} required />
          {error && <p className="error">{error}</p>}
          <button className="mt" disabled={busy} style={{ width: "100%" }}>
            {busy ? "Creating…" : "Register"}
          </button>
        </form>
        <p className="muted mt">
          Already registered? <Link to="/login">Log in</Link>
        </p>
      </div>
    </div>
  );
}
