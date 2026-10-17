import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Flex, Text, TextField } from "@radix-ui/themes";
import { useAuth } from "../auth";
import { api } from "../api";
import { AuthShell, Field, Notice, RLink } from "../components/ui";

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
    try {
      const res = await api<{ message: string }>("/auth/resend-verification", {
        method: "POST", body: { email },
      });
      setInfo(res.message);
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <AuthShell title="Log in to Gradenture">
      <form onSubmit={submit}>
        <Flex direction="column" gap="4">
          <Field label="Email">
            <TextField.Root size="3" type="email" autoComplete="email" value={email}
                            onChange={(e) => setEmail(e.target.value)} required />
          </Field>
          <Field label="Password">
            <TextField.Root size="3" type="password" autoComplete="current-password" value={password}
                            onChange={(e) => setPassword(e.target.value)} required />
          </Field>
          <Notice error={error} success={info} />
          {error.toLowerCase().includes("verify") && (
            <Button type="button" variant="soft" color="gray" onClick={resend}>Resend verification email</Button>
          )}
          <Button size="3" loading={busy}>Log in</Button>
        </Flex>
      </form>
      <Text as="p" size="2" color="gray" mt="4">
        No account? <RLink to="/register">Register</RLink> · <RLink to="/forgot-password">Forgot password?</RLink>
      </Text>
    </AuthShell>
  );
}
