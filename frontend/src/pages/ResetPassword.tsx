import { FormEvent, useMemo, useState } from "react";
import { Button, Flex, Text, TextField } from "@radix-ui/themes";
import { api } from "../api";
import { AuthShell, Field, Notice, RLink } from "../components/ui";

// Supabase recovery links redirect with #access_token=...&type=recovery
export default function ResetPassword() {
  const token = useMemo(() => {
    const params = new URLSearchParams(window.location.hash.slice(1));
    return params.get("access_token") ?? "";
  }, []);
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      const res = await api<{ message: string }>("/auth/reset-password", {
        method: "POST", body: { password }, token,
      });
      setMessage(res.message);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  if (!token)
    return (
      <AuthShell title="Invalid reset link">
        <Text as="p" color="gray">
          This link is missing its token. <RLink to="/forgot-password">Request a new one</RLink>.
        </Text>
      </AuthShell>
    );

  return (
    <AuthShell title="Set a new password">
      <form onSubmit={submit}>
        <Flex direction="column" gap="4">
          <Field label="New password" hint="At least 8 characters">
            <TextField.Root size="3" type="password" autoComplete="new-password" minLength={8} value={password}
                            onChange={(e) => setPassword(e.target.value)} required />
          </Field>
          <Notice error={error} success={message} />
          {message && <RLink to="/login">Go to log in →</RLink>}
          <Button size="3" loading={busy}>Reset password</Button>
        </Flex>
      </form>
    </AuthShell>
  );
}
