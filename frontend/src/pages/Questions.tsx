import { FormEvent, useEffect, useState } from "react";
import { Button, Card, Flex, Grid, Heading, Text, TextArea, TextField } from "@radix-ui/themes";
import { api, BankQuestion, Question } from "../api";
import Icon from "../components/Icon";
import {
  CheckField, Choice, Empty, Field, FormDialog, Notice, PageHeader, Pager, ReasonDialog, Tag, toOpts,
} from "../components/ui";
import { DIFFICULTIES, QUESTION_TYPES, useLookups } from "../lookups";

const PER_PAGE = 20;

export default function Questions() {
  const { domains, companies, domainName, companyName, reloadCompanies } = useLookups();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [bank, setBank] = useState<BankQuestion[]>([]);
  const [bankCount, setBankCount] = useState(0);
  const [bankPage, setBankPage] = useState(1);
  const [filters, setFilters] = useState({ domain_id: "", company_id: "", difficulty: "", question_type: "" });
  const [showForm, setShowForm] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const query = (p: number) => {
    const params = new URLSearchParams({ page: String(p), limit: String(PER_PAGE) });
    Object.entries(filters).forEach(([k, v]) => v && params.set(k, v));
    return params;
  };

  // community submissions (approved only)
  useEffect(() => {
    api<{ data: Question[]; count: number }>(`/questions/?${query(page)}`)
      .then((r) => { setQuestions(r.data); setCount(r.count); })
      .catch((e) => setError(e.message));
  }, [page, filters]);

  // curated question_bank, same filters
  useEffect(() => {
    api<{ data: BankQuestion[]; count: number }>(`/prep/questions?${query(bankPage)}`)
      .then((r) => { setBank(r.data); setBankCount(r.count); })
      .catch(() => {});
  }, [bankPage, filters]);

  const setFilter = (k: keyof typeof filters) => (v: string) => {
    setPage(1); setBankPage(1);
    setFilters((f) => ({ ...f, [k]: v }));
  };

  const upvote = async (id: string) => {
    setError("");
    try {
      const res = await api<{ upvotes: number }>(`/questions/${id}/upvote`, { method: "POST" });
      setQuestions((qs) => qs.map((q) => (q.id === id ? { ...q, upvotes: res.upvotes } : q)));
    } catch (err: any) {
      setError(err.message);
    }
  };

  const flag = async (id: string, reason: string) => {
    setError(""); setMessage("");
    try {
      await api(`/questions/${id}/flag`, { method: "POST", body: { reason } });
      setMessage("Flagged — thanks, an admin will review it.");
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <>
      <PageHeader title="Interview Questions">
        <FormDialog open={showForm} onOpenChange={setShowForm} title="Submit an interview question"
                    trigger={<Button>Submit a question</Button>}>
          <QuestionForm
            domains={domains}
            companies={companies}
            reloadCompanies={reloadCompanies}
            onDone={(msg) => { setMessage(msg); setShowForm(false); }}
          />
        </FormDialog>
      </PageHeader>

      <Notice error={error} success={message} />

      <Flex gap="2" wrap="wrap" mb="5">
        <Choice value={filters.domain_id} onChange={setFilter("domain_id")} options={toOpts(domains)} all="All domains" />
        <Choice value={filters.company_id} onChange={setFilter("company_id")} options={toOpts(companies)} all="All companies" />
        <Choice value={filters.difficulty} onChange={setFilter("difficulty")} options={DIFFICULTIES} all="Any difficulty" />
        <Choice value={filters.question_type} onChange={setFilter("question_type")} options={QUESTION_TYPES} all="Any type" />
      </Flex>

      <Heading size="5" mb="3">Community submissions ({count})</Heading>
      {questions.length === 0 && <Empty>No community questions match these filters yet.</Empty>}
      {questions.map((q) => (
        <Card size="2" key={q.id} mb="3">
          <Flex gap="2" align="center" wrap="wrap" mb="2">
            <Tag>{domainName(q.domain_id)}</Tag>
            <Tag>{companyName(q.company_id)}</Tag>
            <Tag value={q.difficulty} />
            <Tag value={q.question_type} />
            <Text size="1" color="gray">{q.role_title} · asked {q.asked_date.slice(0, 7)}</Text>
          </Flex>
          <Text as="p">{q.question_text}</Text>
          {q.notes && <Text as="p" size="2" color="gray" mt="2">Notes: {q.notes}</Text>}
          <Flex gap="4" mt="3" ml="1">
            <Button size="1" variant="ghost" color="gray" onClick={() => upvote(q.id)} aria-label={`Upvote (${q.upvotes})`}>
              <Icon name="up" size={14} /> {q.upvotes}
            </Button>
            <ReasonDialog
              title="Flag this question"
              description="Tell the moderators what's wrong (min 5 characters)."
              minLength={5} confirmLabel="Flag" color="red"
              onSubmit={(reason) => flag(q.id, reason)}
              trigger={<Button size="1" variant="ghost" color="gray"><Icon name="flag" size={14} /> Flag</Button>}
            />
          </Flex>
        </Card>
      ))}
      <Pager page={page} pages={Math.ceil(count / PER_PAGE)} onPage={setPage} />

      <Heading size="5" mt="6" mb="3">From the interview question pool ({bankCount})</Heading>
      {bank.length === 0 && <Empty>No pool questions match these filters.</Empty>}
      {bank.map((q) => (
        <Card size="2" key={q.id} mb="3">
          <Flex gap="2" align="center" wrap="wrap" mb="2">
            <Tag>{domainName(q.domain_id)}</Tag>
            {q.company_id && <Tag>{companyName(q.company_id)}</Tag>}
            <Tag value={q.difficulty} />
            <Tag value={q.question_type} />
            <Text size="1" color="gray">{q.role_title}</Text>
          </Flex>
          <Text as="p">{q.question_text}</Text>
        </Card>
      ))}
      <Pager page={bankPage} pages={Math.ceil(bankCount / PER_PAGE)} onPage={setBankPage} />
    </>
  );
}

function QuestionForm({ domains, companies, reloadCompanies, onDone }: {
  domains: { id: string; name: string }[];
  companies: { id: string; name: string }[];
  reloadCompanies: () => void;
  onDone: (msg: string) => void;
}) {
  const [form, setForm] = useState({
    domain_id: "", company_id: "", role_title: "", question_text: "",
    question_type: "technical", difficulty: "medium", asked_month: "",
    notes: "", is_anonymous: false,
  });
  const [newCompany, setNewCompany] = useState("");
  const [error, setError] = useState("");
  const [info, setInfo] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k: keyof typeof form) => (v: string | boolean) => setForm((f) => ({ ...f, [k]: v }));

  const addCompany = async () => {
    setError(""); setInfo("");
    try {
      await api("/companies/", { method: "POST", body: { name: newCompany } });
      setNewCompany("");
      reloadCompanies();
      setInfo("Company submitted — it will appear once an admin approves it.");
    } catch (err: any) {
      setError(err.message);
    }
  };

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      await api("/questions/", {
        method: "POST",
        body: {
          domain_id: form.domain_id, company_id: form.company_id,
          role_title: form.role_title, question_text: form.question_text,
          question_type: form.question_type, difficulty: form.difficulty,
          asked_date: `${form.asked_month}-01`,
          notes: form.notes || null, is_anonymous: form.is_anonymous,
        },
      });
      onDone("Question submitted for review — you'll see it once approved.");
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
          <Field label="Domain">
            <Choice value={form.domain_id} onChange={set("domain_id")} options={toOpts(domains)} required />
          </Field>
          <Field label="Company">
            <Choice value={form.company_id} onChange={set("company_id")} options={toOpts(companies)} required />
          </Field>
        </Grid>
        <Flex gap="2">
          <TextField.Root style={{ flex: 1 }} placeholder="Company not listed? Add it" aria-label="New company name"
                          value={newCompany} onChange={(e) => setNewCompany(e.target.value)} />
          <Button type="button" variant="soft" color="gray" disabled={!newCompany.trim()} onClick={addCompany}>
            Add company
          </Button>
        </Flex>
        <Notice success={info} />
        <Field label="Role / job title">
          <TextField.Root value={form.role_title} onChange={(e) => set("role_title")(e.target.value)}
                          maxLength={100} required placeholder="e.g. Backend Developer Intern" />
        </Field>
        <Field label="Question" hint="At least 20 characters">
          <TextArea rows={4} value={form.question_text} onChange={(e) => set("question_text")(e.target.value)}
                    minLength={20} required />
        </Field>
        <Grid columns={{ initial: "1", sm: "3" }} gap="3">
          <Field label="Type">
            <Choice value={form.question_type} onChange={set("question_type")} options={QUESTION_TYPES} />
          </Field>
          <Field label="Difficulty">
            <Choice value={form.difficulty} onChange={set("difficulty")} options={DIFFICULTIES} />
          </Field>
          <Field label="When asked">
            <TextField.Root type="month" value={form.asked_month}
                            onChange={(e) => set("asked_month")(e.target.value)} required />
          </Field>
        </Grid>
        <Field label="Notes (optional)">
          <TextArea value={form.notes} onChange={(e) => set("notes")(e.target.value)} maxLength={500} />
        </Field>
        <CheckField checked={form.is_anonymous} onChange={set("is_anonymous")}>Submit anonymously</CheckField>
        <Notice error={error} />
        <Flex justify="end"><Button loading={busy}>Submit for review</Button></Flex>
      </Flex>
    </form>
  );
}
