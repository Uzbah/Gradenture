import { FormEvent, useEffect, useState } from "react";
import { Button, Card, Flex, Grid, Text, TextArea, TextField } from "@radix-ui/themes";
import { api, Review } from "../api";
import Icon from "../components/Icon";
import {
  CheckField, Choice, Empty, Field, FormDialog, Notice, PageHeader, Pager, ReasonDialog, Tag, toOpts,
} from "../components/ui";
import { DIFFICULTIES, OUTCOMES, useLookups } from "../lookups";

const PER_PAGE = 20;

export default function Reviews() {
  const { domains, companies, domainName, companyName } = useLookups();
  const [reviews, setReviews] = useState<Review[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({ company_id: "", domain_id: "" });
  const [showForm, setShowForm] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    const params = new URLSearchParams({ page: String(page), limit: String(PER_PAGE) });
    Object.entries(filters).forEach(([k, v]) => v && params.set(k, v));
    api<{ data: Review[]; count: number }>(`/reviews/?${params}`)
      .then((r) => { setReviews(r.data); setCount(r.count); })
      .catch((e) => setError(e.message));
  }, [page, filters]);

  const setFilter = (k: keyof typeof filters) => (v: string) => {
    setPage(1);
    setFilters((f) => ({ ...f, [k]: v }));
  };

  const flag = async (id: string, reason: string) => {
    setError(""); setMessage("");
    try {
      await api(`/reviews/${id}/flag`, { method: "POST", body: { reason } });
      setMessage("Flagged — thanks, an admin will review it.");
    } catch (err: any) {
      setError(err.message);
    }
  };

  return (
    <>
      <PageHeader title="Company Interview Reviews">
        <FormDialog open={showForm} onOpenChange={setShowForm} title="Write an interview review"
                    trigger={<Button>Write a review</Button>}>
          <ReviewForm domains={domains} companies={companies}
                      onDone={(msg) => { setMessage(msg); setShowForm(false); }} />
        </FormDialog>
      </PageHeader>

      <Notice error={error} success={message} />

      <Flex gap="2" wrap="wrap" mb="5">
        <Choice value={filters.company_id} onChange={setFilter("company_id")} options={toOpts(companies)} all="All companies" />
        <Choice value={filters.domain_id} onChange={setFilter("domain_id")} options={toOpts(domains)} all="All domains" />
      </Flex>

      {reviews.length === 0 && <Empty>No reviews yet.</Empty>}
      {reviews.map((r) => (
        <Card size="2" key={r.id} mb="3">
          <Flex gap="2" align="center" wrap="wrap" mb="2">
            <Tag>{companyName(r.company_id)}</Tag>
            {r.domain_id && <Tag>{domainName(r.domain_id)}</Tag>}
            <Tag value={r.difficulty} />
            <Tag value={r.outcome} />
            <Text size="1" color="gray">{r.role_title} · {r.interview_date.slice(0, 7)}</Text>
          </Flex>
          <Text as="p">{r.review_text}</Text>
          <Flex mt="3" ml="1">
            <ReasonDialog
              title="Flag this review"
              description="Tell the moderators what's wrong (min 5 characters)."
              minLength={5} confirmLabel="Flag" color="red"
              onSubmit={(reason) => flag(r.id, reason)}
              trigger={<Button size="1" variant="ghost" color="gray"><Icon name="flag" size={14} /> Flag</Button>}
            />
          </Flex>
        </Card>
      ))}

      <Pager page={page} pages={Math.ceil(count / PER_PAGE)} onPage={setPage} />
    </>
  );
}

function ReviewForm({ domains, companies, onDone }: {
  domains: { id: string; name: string }[];
  companies: { id: string; name: string }[];
  onDone: (msg: string) => void;
}) {
  const [form, setForm] = useState({
    company_id: "", domain_id: "", role_title: "", review_text: "",
    interview_month: "", difficulty: "", outcome: "", is_anonymous: false,
  });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const set = (k: keyof typeof form) => (v: string | boolean) => setForm((f) => ({ ...f, [k]: v }));

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError(""); setBusy(true);
    try {
      await api("/reviews/", {
        method: "POST",
        body: {
          company_id: form.company_id,
          domain_id: form.domain_id || null,
          role_title: form.role_title,
          review_text: form.review_text,
          interview_date: `${form.interview_month}-01`,
          difficulty: form.difficulty || null,
          outcome: form.outcome || null,
          is_anonymous: form.is_anonymous,
        },
      });
      onDone("Review submitted for moderation — it will go live once approved.");
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
            <Choice value={form.company_id} onChange={set("company_id")} options={toOpts(companies)} required />
          </Field>
          <Field label="Domain (optional)">
            <Choice value={form.domain_id} onChange={set("domain_id")} options={toOpts(domains)} all="—" />
          </Field>
        </Grid>
        <Field label="Role applied for">
          <TextField.Root value={form.role_title} onChange={(e) => set("role_title")(e.target.value)} maxLength={100} required />
        </Field>
        <Field label="Your review" hint="At least 50 characters">
          <TextArea rows={5} value={form.review_text} onChange={(e) => set("review_text")(e.target.value)}
                    minLength={50} required />
        </Field>
        <Grid columns={{ initial: "1", sm: "3" }} gap="3">
          <Field label="Difficulty">
            <Choice value={form.difficulty} onChange={set("difficulty")} options={DIFFICULTIES} all="—" />
          </Field>
          <Field label="Outcome">
            <Choice value={form.outcome} onChange={set("outcome")} options={OUTCOMES} all="—" />
          </Field>
          <Field label="Interview date">
            <TextField.Root type="month" value={form.interview_month}
                            onChange={(e) => set("interview_month")(e.target.value)} required />
          </Field>
        </Grid>
        <CheckField checked={form.is_anonymous} onChange={set("is_anonymous")}>Submit anonymously</CheckField>
        <Notice error={error} />
        <Flex justify="end"><Button loading={busy}>Submit for review</Button></Flex>
      </Flex>
    </form>
  );
}
