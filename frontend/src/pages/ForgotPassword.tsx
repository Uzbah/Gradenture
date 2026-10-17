import { FormEvent, useState } from "react";
import { Button, Flex, Text, TextField } from "@radix-ui/themes";
import { api } from "../api";
import { AuthShell, Field, Notice, RLink } from "../components/ui";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      const res = await api<{ message: string }>("/auth/forgot-password", {
        method: "POST", body: { email },
      });
      setMessage(res.message);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <AuthShell title="Forgot password">
      <form onSubmit={submit}>
        <Flex direction="column" gap="4">
          <Field label="Email">
            <TextField.Root size="3" type="email" autoComplete="email" value={email}
                            onChange={(e) => setEmail(e.target.value)} required />
          </Field>
          <Notice error={error} success={message} />
          <Button size="3" loading={busy}>Send reset link</Button>
        </Flex>
      </form>
      <Text as="p" size="2" mt="4"><RLink to="/login">Back to login</RLink></Text>
    </AuthShell>
  );
}
