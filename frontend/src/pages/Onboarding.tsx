import { FormEvent, useEffect, useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { Button, Flex, TextField } from "@radix-ui/themes";
import { api, Domain } from "../api";
import { useAuth } from "../auth";
import { AuthShell, Choice, Field, Loading, Notice, toOpts } from "../components/ui";
import { GOALS, SKILL_LEVELS } from "../lookups";

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

  if (loading) return <Loading />;
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
    <AuthShell title="Welcome! Tell us about yourself">
      <form onSubmit={submit}>
        <Flex direction="column" gap="4">
          <Field label="Primary domain">
            <Choice size="3" value={domainId} onChange={setDomainId} options={toOpts(domains)}
                    placeholder="Select a domain…" required />
          </Field>
          <Field label="Skill level">
            <Choice size="3" value={skillLevel} onChange={setSkillLevel} options={SKILL_LEVELS} />
          </Field>
          <Field label="Goal">
            <Choice size="3" value={goal} onChange={setGoal} options={GOALS} />
          </Field>
          <Field label="University">
            <TextField.Root size="3" value={university} onChange={(e) => setUniversity(e.target.value)}
                            minLength={2} maxLength={100} required placeholder="e.g. FAST-NUCES Karachi" />
          </Field>
          <Notice error={error} />
          <Button size="3" loading={busy}>Complete onboarding</Button>
        </Flex>
      </form>
    </AuthShell>
  );
}
