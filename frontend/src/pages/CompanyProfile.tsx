import { FormEvent, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Box, Button, Card, Flex, Grid, Heading, Link, Tabs, Text, TextField } from "@radix-ui/themes";
import { api, BankQuestion, Company, Question, Review, safeUrl } from "../api";
import { Empty, Field, Loading, Notice, RLink, Stat, Tag } from "../components/ui";
import { useLookups } from "../lookups";

export default function CompanyProfile() {
  const { companyId } = useParams();
  const { domainName } = useLookups();
  const [company, setCompany] = useState<Company | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [bank, setBank] = useState<BankQuestion[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [canManage, setCanManage] = useState(false);
  const [editing, setEditing] = useState(false);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!companyId) return;
    api<{ data: Company }>(`/companies/${companyId}`)
      .then((r) => setCompany(r.data))
      .catch((e) => setError(e.message));
    api<{ data: Question[] }>(`/questions/?company_id=${companyId}&limit=50`)
      .then((r) => setQuestions(r.data)).catch(() => {});
    api<{ data: BankQuestion[] }>(`/prep/questions?company_id=${companyId}&limit=50`)
      .then((r) => setBank(r.data)).catch(() => {});
    api<{ data: Review[] }>(`/reviews/?company_id=${companyId}&limit=50`)
      .then((r) => setReviews(r.data)).catch(() => {});
    api<{ data: Company[] }>("/companies/managed")
      .then((r) => setCanManage(r.data.some((c) => c.id === companyId)))
      .catch(() => {});
  }, [companyId]);

  if (error) return <Notice error={error} />;
  if (!company) return <Loading />;

  const offers = reviews.filter((r) => r.outcome === "offer").length;
  const withOutcome = reviews.filter((r) => r.outcome && r.outcome !== "pending").length;
  // community (approved) + curated question_bank, rendered the same way
  const allQuestions: (Question | BankQuestion)[] = [...questions, ...bank];

  return (
    <>
      <RLink to="/companies" size="2" color="gray">← All companies</RLink>

      <Card size="3" my="4">
        <Flex justify="between" align="start" gap="3" wrap="wrap">
          <Box>
            <Heading size="8" mb="2">{company.name}</Heading>
            <Flex gap="3" align="center" wrap="wrap">
              <Tag>{company.industry}</Tag>
              {safeUrl(company.website) && (
                <Link size="2" href={safeUrl(company.website)} target="_blank" rel="noreferrer">{company.website}</Link>
              )}
            </Flex>
          </Box>
          {canManage && (
            <Button variant="soft" color="gray" onClick={() => setEditing((v) => !v)}>
              {editing ? "Cancel" : "Manage profile"}
            </Button>
          )}
        </Flex>
      </Card>

      <Notice success={notice} />
      {editing && (
        <ManageProfile company={company} onDone={(msg) => { setNotice(msg); setEditing(false); }} />
      )}

      <Grid columns="3" gap="3" mb="5">
        <Stat value={allQuestions.length} label="Questions" />
        <Stat value={reviews.length} label="Reviews" />
        <Stat value={withOutcome ? `${Math.round((offers / withOutcome) * 100)}%` : "—"} label="Offer rate" />
      </Grid>

      <Tabs.Root defaultValue="questions">
        <Tabs.List>
          <Tabs.Trigger value="questions">Questions ({allQuestions.length})</Tabs.Trigger>
          <Tabs.Trigger value="reviews">Reviews ({reviews.length})</Tabs.Trigger>
        </Tabs.List>
        <Box pt="4">
          <Tabs.Content value="questions">
            {allQuestions.length === 0 && <Empty>No approved questions for {company.name} yet.</Empty>}
            {allQuestions.map((q) => (
              <Card size="2" key={q.id} mb="3">
                <Flex gap="2" align="center" wrap="wrap" mb="2">
                  <Tag>{domainName(q.domain_id)}</Tag>
                  <Tag value={q.difficulty} />
                  <Text size="1" color="gray">{q.role_title}</Text>
                </Flex>
                <Text as="p">{q.question_text}</Text>
              </Card>
            ))}
          </Tabs.Content>
          <Tabs.Content value="reviews">
            {reviews.length === 0 && <Empty>No approved reviews for {company.name} yet.</Empty>}
            {reviews.map((r) => (
              <Card size="2" key={r.id} mb="3">
                <Flex gap="2" align="center" wrap="wrap" mb="2">
                  <Tag value={r.outcome} />
                  <Text size="1" color="gray">
                    {r.role_title} · {new Date(r.interview_date).toLocaleDateString()}
                  </Text>
                </Flex>
                <Text as="p">{r.review_text}</Text>
              </Card>
            ))}
          </Tabs.Content>
        </Box>
      </Tabs.Root>
    </>
  );
}

function ManageProfile({ company, onDone }: { company: Company; onDone: (msg: string) => void }) {
  const [form, setForm] = useState({
    name: company.name,
    industry: company.industry ?? "",
    website: company.website ?? "",
    logo_url: company.logo_url ?? "",
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k: keyof typeof form) => (e: { target: { value: string } }) =>
    setForm((f) => ({ ...f, [k]: e.target.value }));

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    // send only what actually changed
    const changes = Object.fromEntries(
      Object.entries(form).filter(([k, v]) => v !== "" && v !== (company as any)[k])
    );
    if (Object.keys(changes).length === 0) return setError("Nothing changed.");
    setBusy(true);
    try {
      await api(`/companies/${company.id}/edit-request`, { method: "POST", body: changes });
      onDone("Submitted for review — an admin will approve the changes before they go live.");
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <Card size="3" mb="4" asChild>
      <form onSubmit={submit}>
        <Heading size="5" mb="1">Propose profile changes</Heading>
        <Text as="p" size="2" color="gray" mb="4">
          Edits are reviewed by a Gradenture admin before they appear. You cannot
          edit the questions or reviews on this page.
        </Text>
        <Grid columns={{ initial: "1", sm: "2" }} gap="3" mb="4">
          <Field label="Name"><TextField.Root required value={form.name} onChange={set("name")} /></Field>
          <Field label="Industry"><TextField.Root value={form.industry} onChange={set("industry")} /></Field>
          <Field label="Website"><TextField.Root type="url" value={form.website} onChange={set("website")} /></Field>
          <Field label="Logo URL"><TextField.Root type="url" value={form.logo_url} onChange={set("logo_url")} /></Field>
        </Grid>
        <Notice error={error} />
        <Button type="submit" loading={busy}>Submit for review</Button>
      </form>
    </Card>
  );
}
