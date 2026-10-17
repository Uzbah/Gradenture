import { FormEvent, useEffect, useState } from "react";
import { Button, Card, Flex, Grid, IconButton, Link, Text, TextArea, TextField } from "@radix-ui/themes";
import { api, Application, safeUrl } from "../api";
import Icon from "../components/Icon";
import { Choice, ConfirmDialog, Field, FormDialog, Notice, PageHeader } from "../components/ui";

const COLUMNS: { value: Application["status"]; label: string }[] = [
  { value: "applied", label: "Applied" },
  { value: "interview", label: "Interview" },
  { value: "offer", label: "Offer" },
  { value: "rejected", label: "Rejected" },
  { value: "closed", label: "Closed" },
];

export default function Applications() {
  const [apps, setApps] = useState<Application[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [error, setError] = useState("");

  const load = () =>
    api<{ data: Application[] }>("/applications/?limit=50").then((r) => setApps(r.data)).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const move = async (app: Application, status: Application["status"]) => {
    setApps((a) => a.map((x) => (x.id === app.id ? { ...x, status } : x)));
    try {
      await api(`/applications/${app.id}`, { method: "PATCH", body: { status } });
    } catch (err: any) {
      setError(err.message);
      load();
    }
  };

  const remove = async (app: Application) => {
    try {
      await api(`/applications/${app.id}`, { method: "DELETE" });
      setApps((a) => a.filter((x) => x.id !== app.id));
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <>
      <PageHeader title="Opportunity Tracker">
        <FormDialog open={showForm} onOpenChange={setShowForm} title="New application"
                    trigger={<Button>Add application</Button>}>
          <AppForm onDone={() => { setShowForm(false); load(); }} />
        </FormDialog>
      </PageHeader>
      <Notice error={error} />

      <Grid columns={{ initial: "1", sm: "2", md: "3", lg: "5" }} gap="3" align="start">
        {COLUMNS.map((col) => {
          const items = apps.filter((a) => a.status === col.value);
          return (
            <div className="kanban-col" key={col.value}>
              <Text as="div" size="1" weight="bold" color="gray" className="eyebrow" mb="3">
                {col.label} ({items.length})
              </Text>
              <Flex direction="column" gap="2">
                {items.map((app) => (
                  <Card key={app.id} size="1">
                    <Text as="div" size="2" weight="bold">{app.company_name}</Text>
                    <Text as="div" size="2" color="gray">{app.role_title}</Text>
                    {app.deadline && <Text as="div" size="1" color="gray">Deadline: {app.deadline}</Text>}
                    {safeUrl(app.job_url) && (
                      <Link size="1" href={safeUrl(app.job_url)} target="_blank" rel="noreferrer">Job link</Link>
                    )}
                    {app.notes && <Text as="p" size="1" color="gray" mt="1">{app.notes}</Text>}
                    <Flex justify="between" align="center" mt="2">
                      <Choice size="1" value={app.status} options={COLUMNS}
                              onChange={(v) => move(app, v as Application["status"])} />
                      <ConfirmDialog
                        title="Delete application?"
                        description={`Your application to ${app.company_name} will be removed. This can't be undone.`}
                        confirmLabel="Delete"
                        onConfirm={() => remove(app)}
                        trigger={
                          <IconButton size="1" variant="ghost" color="gray" aria-label={`Delete application to ${app.company_name}`}>
                            <Icon name="x" size={14} />
                          </IconButton>
                        }
                      />
                    </Flex>
                  </Card>
                ))}
              </Flex>
            </div>
          );
        })}
      </Grid>
    </>
  );
}

function AppForm({ onDone }: { onDone: () => void }) {
  const [form, setForm] = useState({
    company_name: "", role_title: "", applied_date: "", deadline: "", job_url: "", notes: "",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k: keyof typeof form) => (e: { target: { value: string } }) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      await api("/applications/", {
        method: "POST",
        body: {
          company_name: form.company_name,
          role_title: form.role_title,
          applied_date: form.applied_date || null,
          deadline: form.deadline || null,
          job_url: form.job_url || null,
          notes: form.notes || null,
        },
      });
      onDone();
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form onSubmit={submit}>
      <Flex direction="column" gap="3" mt="3">
        <Grid columns={{ initial: "1", sm: "2" }} gap="3">
          <Field label="Company">
            <TextField.Root value={form.company_name} onChange={set("company_name")} required maxLength={100} />
          </Field>
          <Field label="Role title">
            <TextField.Root value={form.role_title} onChange={set("role_title")} required maxLength={100} />
          </Field>
          <Field label="Applied date">
            <TextField.Root type="date" value={form.applied_date} onChange={set("applied_date")} />
          </Field>
          <Field label="Deadline">
            <TextField.Root type="date" value={form.deadline} onChange={set("deadline")} />
          </Field>
        </Grid>
        <Field label="Job URL (optional)">
          <TextField.Root type="url" value={form.job_url} onChange={set("job_url")} />
        </Field>
        <Field label="Notes (optional)">
          <TextArea value={form.notes} onChange={set("notes")} maxLength={1000} />
        </Field>
        <Notice error={error} />
        <Flex justify="end"><Button loading={busy}>Add</Button></Flex>
      </Flex>
    </form>
  );
}
