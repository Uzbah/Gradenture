import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiResponse } from "../api";
import Logo from "../components/Logo";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const res = await api<ApiResponse<null>>("/auth/forgot-password", {
        method: "POST", body: { email },
      });
      setMessage(res.msg);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <div className="page-narrow">
      <Logo />
      <div className="card">
        <h1>Forgot password</h1>
        <form onSubmit={submit}>
          <label>Email</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          {message && <p className="success">{message}</p>}
          {error && <p className="error">{error}</p>}
          <button className="mt" style={{ width: "100%" }}>Send reset link</button>
        </form>
        <p className="muted mt"><Link to="/login">Back to login</Link></p>
      </div>
    </div>
  );
}
