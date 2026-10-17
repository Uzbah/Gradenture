import { FormEvent, useEffect, useState } from "react";
import { Box, Button, Card, Flex, Grid, Heading, Strong, Tabs, Text, TextArea, TextField } from "@radix-ui/themes";
import { api, MySubmissions } from "../api";
import { useAuth } from "../auth";
import { Choice, Empty, Field, Loading, Notice, Stat, Tag, toOpts } from "../components/ui";
import { GOALS, SKILL_LEVELS, useLookups } from "../lookups";

const STATUS_LABEL: Record<string, string> = {
  approved: "Live",
  pending: "In review",
  needs_edit: "Edit requested",
  rejected: "Not approved",
};

export default function Profile() {
  return (
    <>
      <Heading size="8" mb="5">Profile</Heading>
      <Tabs.Root defaultValue="submissions">
        <Tabs.List>
          <Tabs.Trigger value="submissions">My submissions</Tabs.Trigger>
          <Tabs.Trigger value="profile">Profile details</Tabs.Trigger>
          <Tabs.Trigger value="password">Password</Tabs.Trigger>
        </Tabs.List>
        <Box pt="5">
          <Tabs.Content value="submissions"><Submissions /></Tabs.Content>
          <Tabs.Content value="profile"><ProfileForm /></Tabs.Content>
          <Tabs.Content value="password"><PasswordForm /></Tabs.Content>
        </Box>
      </Tabs.Root>
    </>
  );
}

function Submissions() {
  const { companyName } = useLookups();
  const [data, setData] = useState<MySubmissions | null>(null);
  const [editing, setEditing] = useState<string | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const load = () =>
    api<{ data: MySubmissions }>("/users/me/submissions")
      .then((r) => setData(r.data))
      .catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  if (error && !data) return <Notice error={error} />;
  if (!data) return <Loading />;

  const all = [...data.questions, ...data.reviews];
  const count = (s: string) => all.filter((x) => x.status === s).length;

  const resubmit = async (kind: "questions" | "reviews", id: string, body: object) => {
    setError(""); setMessage("");
    try {
      await api(`/${kind}/${id}`, { method: "PATCH", body });
      setEditing(null);
      setMessage("Resubmitted. A moderator will review it again.");
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <>
      <Grid columns={{ initial: "2", md: "4" }} gap="3" mb="5">
        <Stat value={all.length} label="Submitted" />
        <Stat value={count("pending")} label="In review" />
        <Stat value={count("needs_edit")} label="Edit requested" />
        <Stat highlight value={count("approved")} label="Live contributions" />
      </Grid>
      <Notice error={error} success={message} />

      <Heading size="5" mb="3">Questions ({data.questions.length})</Heading>
      {data.questions.length === 0 && <Empty>You haven't submitted any questions yet.</Empty>}
      {data.questions.map((q) => (
        <Card size="2" key={q.id} mb="3">
          <Header status={q.status} company={companyName(q.company_id)} role={q.role_title} date={q.created_at} />
          {editing === q.id ? (
            <EditForm
              minLength={20}
              initial={q.question_text}
              initialNotes={q.notes ?? ""}
              onCancel={() => setEditing(null)}
              onSave={(text, notes) =>
                resubmit("questions", q.id, { question_text: text, notes: notes || null })}
            />
          ) : (
            <Text as="p">{q.question_text}</Text>
          )}
          <Footer note={q.admin_note} status={q.status} editing={editing === q.id} onEdit={() => setEditing(q.id)} />
        </Card>
      ))}

      <Heading size="5" mt="6" mb="3">Reviews ({data.reviews.length})</Heading>
      {data.reviews.length === 0 && <Empty>You haven't written any reviews yet.</Empty>}
      {data.reviews.map((r) => (
        <Card size="2" key={r.id} mb="3">
          <Header status={r.status} company={companyName(r.company_id)} role={r.role_title} date={r.created_at} />
          {editing === r.id ? (
            <EditForm
              minLength={50}
              initial={r.review_text}
              onCancel={() => setEditing(null)}
              onSave={(text) => resubmit("reviews", r.id, { review_text: text })}
            />
          ) : (
            <Text as="p">{r.review_text}</Text>
          )}
          <Footer note={r.admin_note} status={r.status} editing={editing === r.id} onEdit={() => setEditing(r.id)} />
        </Card>
      ))}
    </>
  );
}

function Header({ status, company, role, date }: { status: string; company: string; role: string; date: string }) {
  return (
    <Flex gap="2" align="center" wrap="wrap" mb="2">
      <Tag value={status}>{STATUS_LABEL[status]}</Tag>
      <Tag>{company}</Tag>
      <Text size="1" color="gray">{role} · {new Date(date).toLocaleDateString()}</Text>
    </Flex>
  );
}

function Footer({ note, status, editing, onEdit }: {
  note?: string; status: string; editing: boolean; onEdit: () => void;
}) {
  return (
    <>
      {note && status !== "approved" && (
        <Text as="p" size="2" color="gray" mt="3"><Strong>Moderator note:</Strong> {note}</Text>
      )}
      {status === "needs_edit" && !editing && (
        <Button size="1" mt="3" onClick={onEdit}>Edit &amp; resubmit</Button>
      )}
    </>
  );
}

function EditForm({ initial, initialNotes, minLength, onSave, onCancel }: {
  initial: string;
  initialNotes?: string;
  minLength: number;
  onSave: (text: string, notes: string) => void;
  onCancel: () => void;
}) {
  const [text, setText] = useState(initial);
  const [notes, setNotes] = useState(initialNotes ?? "");
  return (
    <form onSubmit={(e) => { e.preventDefault(); onSave(text, notes); }}>
      <Flex direction="column" gap="3" mt="2">
        <TextArea rows={4} aria-label="Text" value={text} onChange={(e) => setText(e.target.value)} minLength={minLength} required />
        {initialNotes !== undefined && (
          <Field label="Notes (optional)">
            <TextArea value={notes} onChange={(e) => setNotes(e.target.value)} maxLength={500} />
          </Field>
        )}
        <Flex gap="2">
          <Button type="submit" size="1">Resubmit for review</Button>
          <Button type="button" size="1" variant="soft" color="gray" onClick={onCancel}>Cancel</Button>
        </Flex>
      </Flex>
    </form>
  );
}

function ProfileForm() {
  const { user, refresh } = useAuth();
  const { domains } = useLookups();
  const [form, setForm] = useState({
    domain_id: user?.domain_id ?? "",
    skill_level: user?.skill_level ?? "beginner",
    goal: user?.goal ?? "internship",
    university: user?.university ?? "",
  });
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k: keyof typeof form) => (v: string) => setForm((f) => ({ ...f, [k]: v }));

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(""); setMessage(""); setBusy(true);
    try {
      // Same fields as onboarding, so the onboarding endpoint is the profile update.
      await api("/users/onboarding", { method: "PATCH", body: form });
      await refresh();
      setMessage("Profile saved.");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card size="3" style={{ maxWidth: 520 }} asChild>
      <form onSubmit={submit}>
        <Flex direction="column" gap="4">
          <Field label="Email"><TextField.Root value={user?.email ?? ""} disabled /></Field>
          <Field label="Primary domain" hint="Your Prep roadmap follows this domain. Progress in other domains is kept.">
            <Choice value={form.domain_id} onChange={set("domain_id")} options={toOpts(domains)}
                    placeholder="Select a domain…" required />
          </Field>
          <Field label="Skill level">
            <Choice value={form.skill_level} onChange={set("skill_level")} options={SKILL_LEVELS} />
          </Field>
          <Field label="Goal">
            <Choice value={form.goal} onChange={set("goal")} options={GOALS} />
          </Field>
          <Field label="University">
            <TextField.Root value={form.university} onChange={(e) => set("university")(e.target.value)}
                            minLength={2} maxLength={100} required />
          </Field>
          <Notice error={error} success={message} />
          <Box><Button loading={busy}>Save changes</Button></Box>
        </Flex>
      </form>
    </Card>
  );
}

function PasswordForm() {
  const [current, setCurrent] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(""); setMessage("");
    if (password !== confirm) return setError("Passwords don't match.");
    setBusy(true);
    try {
      await api("/auth/reset-password", {
        method: "POST", body: { password, current_password: current },
      });
      setCurrent(""); setPassword(""); setConfirm("");
      setMessage("Password updated.");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card size="3" style={{ maxWidth: 520 }} asChild>
      <form onSubmit={submit}>
        <Flex direction="column" gap="4">
          <Field label="Current password">
            <TextField.Root type="password" autoComplete="current-password" value={current}
                            onChange={(e) => setCurrent(e.target.value)} required />
          </Field>
          <Field label="New password" hint="At least 8 characters">
            <TextField.Root type="password" autoComplete="new-password" minLength={8} maxLength={128} value={password}
                            onChange={(e) => setPassword(e.target.value)} required />
          </Field>
          <Field label="Confirm new password">
            <TextField.Root type="password" autoComplete="new-password" minLength={8} maxLength={128} value={confirm}
                            onChange={(e) => setConfirm(e.target.value)} required />
          </Field>
          <Notice error={error} success={message} />
          <Box><Button loading={busy}>Update password</Button></Box>
        </Flex>
      </form>
    </Card>
  );
}
