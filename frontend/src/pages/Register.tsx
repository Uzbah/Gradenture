import { FormEvent, useState } from "react";
import { Button, Flex, Strong, Text, TextField } from "@radix-ui/themes";
import { api } from "../api";
import { AuthShell, Field, Notice, RLink } from "../components/ui";

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
      <AuthShell title="Check your email">
        <Text as="p" color="gray">
          We sent a verification link to <Strong>{email}</Strong>. Verify your email, then{" "}
          <RLink to="/login">log in</RLink>.
        </Text>
      </AuthShell>
    );

  return (
    <AuthShell title="Create your account">
      <form onSubmit={submit}>
        <Flex direction="column" gap="4">
          <Field label="Email">
            <TextField.Root size="3" type="email" autoComplete="email" value={email}
                            onChange={(e) => setEmail(e.target.value)} required />
          </Field>
          <Field label="Password" hint="At least 8 characters">
            <TextField.Root size="3" type="password" autoComplete="new-password" minLength={8} value={password}
                            onChange={(e) => setPassword(e.target.value)} required />
          </Field>
          <Notice error={error} />
          <Button size="3" loading={busy}>Register</Button>
        </Flex>
      </form>
      <Text as="p" size="2" color="gray" mt="4">
        Already registered? <RLink to="/login">Log in</RLink>
      </Text>
    </AuthShell>
  );
}
