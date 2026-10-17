import { FormEvent, useEffect, useState } from "react";
import {
  Box, Button, Card, DataList, Dialog, Flex, Heading, Strong, Table, Tabs, Text, TextField,
} from "@radix-ui/themes";
import { api, Company, CompanyEdit, CompanyManager, Flag, Question, Review, User } from "../api";
import { useAuth } from "../auth";
import {
  Choice, ConfirmDialog, Empty, Field, FormDialog, Notice, ReasonDialog, Tag,
} from "../components/ui";
import { useLookups } from "../lookups";

export default function Admin() {
  return (
    <>
      <Heading size="8" mb="5">Admin Panel</Heading>
      <Tabs.Root defaultValue="queue">
        <Tabs.List>
          <Tabs.Trigger value="queue">Moderation queue</Tabs.Trigger>
          <Tabs.Trigger value="flags">Flags</Tabs.Trigger>
          <Tabs.Trigger value="companies">Companies</Tabs.Trigger>
          <Tabs.Trigger value="users">Users</Tabs.Trigger>
        </Tabs.List>
        <Box pt="5">
          <Tabs.Content value="queue"><Queue /></Tabs.Content>
          <Tabs.Content value="flags"><Flags /></Tabs.Content>
          <Tabs.Content value="companies"><CompaniesAdmin /></Tabs.Content>
          <Tabs.Content value="users"><Users /></Tabs.Content>
        </Box>
      </Tabs.Root>
    </>
  );
}

function Queue() {
  const { domainName, companyName } = useLookups();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [edits, setEdits] = useState<CompanyEdit[]>([]);
  const [error, setError] = useState("");

  const load = () =>
    api<{ data: { questions: Question[]; reviews: Review[]; companies: Company[] } }>("/admin/queue")
      .then((r) => { setQuestions(r.data.questions); setReviews(r.data.reviews); setCompanies(r.data.companies); })
      .catch((e) => setError(e.message));

  const loadEdits = () =>
    api<{ data: CompanyEdit[] }>("/admin/company-edits")
      .then((r) => setEdits(r.data))
      .catch(() => {});

  useEffect(() => { load(); loadEdits(); }, []);

  const decideEdit = async (id: string, status: "approved" | "rejected", admin_note: string | null = null) => {
    setError("");
    try {
      await api(`/admin/company-edits/${id}`, { method: "PATCH", body: { status, admin_note } });
      loadEdits();
    } catch (err: any) { setError(err.message); }
  };

  const approveCompany = async (id: string) => {
    setError("");
    try {
      await api(`/admin/companies/${id}`, { method: "PATCH" });
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const moderate = async (kind: "questions" | "reviews", id: string, status: string, admin_note: string | null = null) => {
    setError("");
    try {
      await api(`/admin/${kind}/${id}`, { method: "PATCH", body: { status, admin_note } });
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const Actions = ({ kind, id }: { kind: "questions" | "reviews"; id: string }) => (
    <Flex gap="2" mt="3" wrap="wrap">
      <Button size="1" onClick={() => moderate(kind, id, "approved")}>Approve</Button>
      <ReasonDialog
        title="Reject submission" description="This note is sent to the submitter."
        confirmLabel="Reject" color="red"
        onSubmit={(note) => moderate(kind, id, "rejected", note)}
        trigger={<Button size="1" variant="soft" color="red">Reject</Button>}
      />
      <ReasonDialog
        title="Request an edit" description="Tell the submitter what to change."
        confirmLabel="Request edit"
        onSubmit={(note) => moderate(kind, id, "needs_edit", note)}
        trigger={<Button size="1" variant="soft" color="gray">Request edit</Button>}
      />
    </Flex>
  );

  return (
    <>
      <Notice error={error} />
      <Heading size="5" mb="3">Pending companies ({companies.length})</Heading>
      {companies.length === 0 && <Empty>Nothing to approve.</Empty>}
      {companies.map((c) => (
        <Card size="2" key={c.id} mb="3">
          <Flex gap="2" align="center" mb="1">
            <Strong>{c.name}</Strong>
            <Tag>{c.industry}</Tag>
          </Flex>
          {c.website && <Text as="p" size="2" color="gray">{c.website}</Text>}
          <Button size="1" mt="3" onClick={() => approveCompany(c.id)}>Approve</Button>
        </Card>
      ))}

      <Heading size="5" mt="6" mb="3">Pending profile edits ({edits.length})</Heading>
      {edits.length === 0 && <Empty>No profile changes awaiting review.</Empty>}
      {edits.map((ed) => (
        <Card size="2" key={ed.id} mb="3">
          <Flex gap="2" align="center" mb="3">
            <Strong>{ed.companies?.name ?? "Company"}</Strong>
            <Text size="1" color="gray">{new Date(ed.created_at).toLocaleDateString()}</Text>
          </Flex>
          <DataList.Root size="2">
            {Object.entries(ed.changes).map(([field, value]) => (
              <DataList.Item key={field}>
                <DataList.Label>{field}</DataList.Label>
                <DataList.Value>{String(value)}</DataList.Value>
              </DataList.Item>
            ))}
          </DataList.Root>
          <Flex gap="2" mt="3">
            <Button size="1" onClick={() => decideEdit(ed.id, "approved")}>Approve</Button>
            <ReasonDialog
              title="Reject profile edit" description="This note is sent to the company manager."
              confirmLabel="Reject" color="red"
              onSubmit={(note) => decideEdit(ed.id, "rejected", note)}
              trigger={<Button size="1" variant="soft" color="red">Reject</Button>}
            />
          </Flex>
        </Card>
      ))}

      <Heading size="5" mt="6" mb="3">Pending questions ({questions.length})</Heading>
      {questions.length === 0 && <Empty>Queue is empty.</Empty>}
      {questions.map((q) => (
        <Card size="2" key={q.id} mb="3">
          <Flex gap="2" align="center" wrap="wrap" mb="2">
            <Tag>{domainName(q.domain_id)}</Tag>
            <Tag>{companyName(q.company_id)}</Tag>
            <Tag value={q.difficulty} />
            <Text size="1" color="gray">{q.role_title} · {new Date(q.created_at).toLocaleDateString()}</Text>
          </Flex>
          <Text as="p">{q.question_text}</Text>
          {q.notes && <Text as="p" size="2" color="gray" mt="2">Notes: {q.notes}</Text>}
          <Actions kind="questions" id={q.id} />
        </Card>
      ))}

      <Heading size="5" mt="6" mb="3">Pending reviews ({reviews.length})</Heading>
      {reviews.length === 0 && <Empty>Queue is empty.</Empty>}
      {reviews.map((r) => (
        <Card size="2" key={r.id} mb="3">
          <Flex gap="2" align="center" wrap="wrap" mb="2">
            <Tag>{companyName(r.company_id)}</Tag>
            <Tag value={r.outcome} />
            <Text size="1" color="gray">{r.role_title} · {new Date(r.created_at).toLocaleDateString()}</Text>
          </Flex>
          <Text as="p">{r.review_text}</Text>
          <Actions kind="reviews" id={r.id} />
        </Card>
      ))}
    </>
  );
}

function Flags() {
  const { companyName } = useLookups();
  const [flags, setFlags] = useState<Flag[]>([]);
  const [error, setError] = useState("");

  const load = () =>
    api<{ data: Flag[] }>("/admin/flags").then((r) => setFlags(r.data)).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const act = async (id: string, status: "resolved" | "dismissed") => {
    setError("");
    try {
      await api(`/admin/flags/${id}`, { method: "PATCH", body: { status } });
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <>
      <Notice error={error} />
      <Heading size="5" mb="3">Open flags ({flags.length})</Heading>
      {flags.length === 0 && <Empty>No open flags.</Empty>}
      {flags.map((f) => (
        <Card size="2" key={f.id} mb="3">
          <Flex gap="2" align="center" mb="2">
            <Tag value={f.content_type} />
            {f.content && <Tag>{companyName(f.content.company_id)}</Tag>}
            <Text size="1" color="gray">{new Date(f.created_at).toLocaleDateString()}</Text>
          </Flex>
          <Text as="p"><Strong>Reason:</Strong> {f.reason}</Text>
          <Text as="p" size="2" color="gray" mt="1">
            {f.content ? (f.content.question_text ?? f.content.review_text) : "Content no longer exists."}
          </Text>
          <Flex gap="2" mt="3">
            <Button size="1" onClick={() => act(f.id, "resolved")}>Resolve</Button>
            <Button size="1" variant="soft" color="gray" onClick={() => act(f.id, "dismissed")}>Dismiss</Button>
          </Flex>
        </Card>
      ))}
    </>
  );
}

function CompaniesAdmin() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [q, setQ] = useState("");
  const [formFor, setFormFor] = useState<Company | "new" | null>(null);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");

  const load = () => {
    const params = new URLSearchParams({ limit: "50" });
    if (q.trim()) params.set("q", q.trim());
    api<{ data: Company[] }>(`/admin/companies?${params}`)
      .then((r) => setCompanies(r.data))
      .catch((e) => setError(e.message));
  };
  useEffect(() => {
    const t = setTimeout(load, 250);
    return () => clearTimeout(t);
  }, [q]);

  // Throws so CompanyForm can show the error inside its dialog.
  const save = async (body: Partial<Company>, id?: string) => {
    setError(""); setInfo("");
    if (id) await api(`/admin/companies/${id}`, { method: "PATCH", body });
    else await api("/admin/companies", { method: "POST", body });
    setInfo(id ? "Company updated" : "Company created");
    setFormFor(null);
    load();
  };

  const merge = async (from: Company, intoId: string) => {
    setError(""); setInfo("");
    try {
      const r = await api<{ message: string }>(`/admin/companies/${from.id}/merge`,
        { method: "POST", body: { into_id: intoId } });
      setInfo(r.message);
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  const editing = formFor && formFor !== "new" ? formFor : undefined;

  return (
    <>
      <Notice error={error} success={info} />

      <Flex justify="between" align="center" gap="3" mb="3" wrap="wrap">
        <Box flexGrow="1" maxWidth="300px">
          <TextField.Root placeholder="Search companies…" aria-label="Search companies" value={q}
                          onChange={(e) => setQ(e.target.value)} />
        </Box>
        <Button onClick={() => setFormFor("new")}>Add company</Button>
      </Flex>

      <FormDialog open={formFor !== null} onOpenChange={(o) => !o && setFormFor(null)}
                  title={editing ? `Edit ${editing.name}` : "New company"}>
        <CompanyForm key={editing?.id ?? "new"} company={editing} onSave={(b) => save(b, editing?.id)} />
      </FormDialog>

      <Table.Root variant="surface">
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeaderCell>Name</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Industry</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Status</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Actions</Table.ColumnHeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {companies.map((c) => (
            <Table.Row key={c.id} align="center">
              <Table.RowHeaderCell>{c.name}</Table.RowHeaderCell>
              <Table.Cell>{c.industry ?? "—"}</Table.Cell>
              <Table.Cell><Tag value={c.status === "approved" ? "approved" : "pending"} /></Table.Cell>
              <Table.Cell>
                <Flex gap="2" wrap="wrap">
                  <Button size="1" variant="soft" color="gray" onClick={() => setFormFor(c)}>Edit</Button>
                  {c.status !== "approved" && (
                    <Button size="1" onClick={() => save({ status: "approved" }, c.id).catch((e) => setError(e.message))}>
                      Approve
                    </Button>
                  )}
                  <MergeDialog company={c} others={companies.filter((o) => o.id !== c.id)} onMerge={(id) => merge(c, id)} />
                  <Dialog.Root>
                    <Dialog.Trigger><Button size="1" variant="soft" color="gray">Managers</Button></Dialog.Trigger>
                    <Dialog.Content maxWidth="480px">
                      <Dialog.Title>Managers of {c.name}</Dialog.Title>
                      <Dialog.Description size="2" color="gray" mb="4">
                        Managers may propose profile changes only. They cannot moderate the
                        questions or reviews written about this company.
                      </Dialog.Description>
                      <Managers company={c} />
                    </Dialog.Content>
                  </Dialog.Root>
                </Flex>
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
    </>
  );
}

function MergeDialog({ company, others, onMerge }: {
  company: Company; others: Company[]; onMerge: (intoId: string) => void;
}) {
  const [into, setInto] = useState("");
  const target = others.find((o) => o.id === into);
  return (
    <Dialog.Root onOpenChange={() => setInto("")}>
      <Dialog.Trigger><Button size="1" variant="soft" color="gray">Merge</Button></Dialog.Trigger>
      <Dialog.Content maxWidth="480px">
        <Dialog.Title>Merge {company.name}</Dialog.Title>
        <Dialog.Description size="2" mb="4">
          All its questions and reviews move to the target and <Strong>{company.name}</Strong> is
          deleted. This cannot be undone.
        </Dialog.Description>
        <Field label="Merge into">
          <Choice value={into} onChange={setInto} placeholder="Choose a company…"
                  options={others.map((o) => ({ value: o.id, label: o.name }))} />
        </Field>
        <Flex gap="3" mt="4" justify="end">
          <Dialog.Close><Button variant="soft" color="gray">Cancel</Button></Dialog.Close>
          <Dialog.Close>
            <Button color="red" disabled={!target} onClick={() => onMerge(into)}>
              {target ? `Merge into ${target.name}` : "Merge"}
            </Button>
          </Dialog.Close>
        </Flex>
      </Dialog.Content>
    </Dialog.Root>
  );
}

function Managers({ company }: { company: Company }) {
  const [managers, setManagers] = useState<CompanyManager[]>([]);
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");

  const load = () =>
    api<{ data: CompanyManager[] }>(`/admin/companies/${company.id}/managers`)
      .then((r) => setManagers(r.data))
      .catch((e) => setError(e.message));
  useEffect(() => { load(); }, [company.id]);

  const grant = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      await api(`/admin/companies/${company.id}/managers`, { method: "POST", body: { email } });
      setEmail(""); load();
    } catch (err: any) { setError(err.message); }
  };

  const revoke = async (userId: string) => {
    setError("");
    try {
      await api(`/admin/companies/${company.id}/managers/${userId}`, { method: "DELETE" });
      load();
    } catch (err: any) { setError(err.message); }
  };

  return (
    <>
      <Notice error={error} />
      {managers.length === 0 && <Empty>No managers assigned.</Empty>}
      <Flex direction="column" gap="2" mb="4">
        {managers.map((m) => (
          <Flex key={m.user_id} justify="between" align="center" gap="3">
            <Text size="2">{m.users?.email ?? m.user_id}</Text>
            <Button size="1" variant="soft" color="red" onClick={() => revoke(m.user_id)}>Revoke</Button>
          </Flex>
        ))}
      </Flex>
      <form onSubmit={grant}>
        <Flex gap="2">
          <TextField.Root style={{ flex: 1 }} type="email" required placeholder="user@example.com"
                          aria-label="Manager email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Button type="submit">Grant access</Button>
        </Flex>
      </form>
    </>
  );
}

function CompanyForm({ company, onSave }: {
  company?: Company;
  onSave: (body: Partial<Company>) => Promise<void>;
}) {
  const [form, setForm] = useState({
    name: company?.name ?? "",
    industry: company?.industry ?? "",
    website: company?.website ?? "",
    logo_url: company?.logo_url ?? "",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k: keyof typeof form) => (e: { target: { value: string } }) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      // drop blanks so PATCH never clears a field the admin left untouched
      await onSave(Object.fromEntries(Object.entries(form).filter(([, v]) => v !== "")));
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <form onSubmit={submit}>
      <Flex direction="column" gap="3" mt="3">
        <Field label="Name"><TextField.Root required value={form.name} onChange={set("name")} /></Field>
        <Field label="Industry"><TextField.Root value={form.industry} onChange={set("industry")} /></Field>
        <Field label="Website"><TextField.Root type="url" value={form.website} onChange={set("website")} /></Field>
        <Field label="Logo URL"><TextField.Root type="url" value={form.logo_url} onChange={set("logo_url")} /></Field>
        <Notice error={error} />
        <Flex justify="end"><Button type="submit" loading={busy}>{company ? "Save changes" : "Create"}</Button></Flex>
      </Flex>
    </form>
  );
}

const ROLES = ["user", "admin", "super_admin"].map((r) => ({ value: r, label: r }));

function Users() {
  const { user: me } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const isSuper = me?.role === "super_admin";

  const load = () =>
    api<{ data: User[] }>("/admin/users?limit=50").then((r) => setUsers(r.data)).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  const call = async (path: string, body: object | undefined, done: string) => {
    setError(""); setInfo("");
    try {
      await api(path, { method: "PATCH", body });
      setInfo(done);
      load();
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <>
      <Notice error={error} success={info} />
      <Table.Root variant="surface">
        <Table.Header>
          <Table.Row>
            <Table.ColumnHeaderCell>Email</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Role</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Onboarded</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Status</Table.ColumnHeaderCell>
            <Table.ColumnHeaderCell>Actions</Table.ColumnHeaderCell>
          </Table.Row>
        </Table.Header>
        <Table.Body>
          {users.map((u) => (
            <Table.Row key={u.id} align="center">
              <Table.RowHeaderCell>{u.email}</Table.RowHeaderCell>
              <Table.Cell>
                {isSuper && u.id !== me?.id ? (
                  <Choice size="1" value={u.role} options={ROLES}
                          onChange={(role) => call(`/admin/users/${u.id}/role`, { role }, "Role updated")} />
                ) : (
                  u.role
                )}
              </Table.Cell>
              <Table.Cell>{u.onboarding_complete ? "Yes" : "No"}</Table.Cell>
              <Table.Cell>{u.suspended_at ? <Tag value="suspended" /> : "active"}</Table.Cell>
              <Table.Cell>
                {/* plain admins may only suspend plain users (API-enforced too) */}
                {u.id !== me?.id && (isSuper || u.role === "user") && (
                  u.suspended_at ? (
                    <Button size="1" variant="soft" color="gray"
                            onClick={() => call(`/admin/users/${u.id}/unsuspend`, undefined, "User unsuspended")}>
                      Unsuspend
                    </Button>
                  ) : (
                    <ConfirmDialog
                      title={`Suspend ${u.email}?`}
                      description="They will no longer be able to log in."
                      confirmLabel="Suspend"
                      onConfirm={() => call(`/admin/users/${u.id}/suspend`, undefined, "User suspended")}
                      trigger={<Button size="1" variant="soft" color="red">Suspend</Button>}
                    />
                  )
                )}
              </Table.Cell>
            </Table.Row>
          ))}
        </Table.Body>
      </Table.Root>
    </>
  );
}
