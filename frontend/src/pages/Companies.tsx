import { useEffect, useState } from "react";
import { Link as RouterLink } from "react-router-dom";
import { Box, Card, Grid, Text, TextField } from "@radix-ui/themes";
import { api, Company } from "../api";
import Icon from "../components/Icon";
import { Empty, Notice, PageHeader, Pager, Tag } from "../components/ui";

const PER_PAGE = 24;

export default function Companies() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [q, setQ] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    // debounce so typing doesn't fire a request per keystroke
    const t = setTimeout(() => {
      const params = new URLSearchParams({ page: String(page), limit: String(PER_PAGE) });
      if (q.trim()) params.set("q", q.trim());
      api<{ data: Company[]; count: number }>(`/companies/?${params}`)
        .then((r) => { setCompanies(r.data); setCount(r.count); setError(""); })
        .catch((e) => setError(e.message));
    }, 250);
    return () => clearTimeout(t);
  }, [page, q]);

  return (
    <>
      <PageHeader title="Companies">
        <Text size="2" color="gray">{count} in the registry</Text>
      </PageHeader>

      <Box mb="4" maxWidth="420px">
        <TextField.Root size="3" placeholder="Search companies…" aria-label="Search companies" value={q}
                        onChange={(e) => { setQ(e.target.value); setPage(1); }}>
          <TextField.Slot><Icon name="search" size={16} /></TextField.Slot>
        </TextField.Root>
      </Box>

      <Notice error={error} />
      {companies.length === 0 && !error && (
        <Empty>{q ? `No companies match “${q}”.` : "No companies yet."}</Empty>
      )}

      <Grid columns={{ initial: "1", xs: "2", md: "3" }} gap="3">
        {companies.map((c) => (
          <Card key={c.id} size="2" asChild>
            <RouterLink to={`/companies/${c.id}`}>
              <Text as="div" weight="bold">{c.name}</Text>
              {c.industry && <Box mt="2"><Tag>{c.industry}</Tag></Box>}
            </RouterLink>
          </Card>
        ))}
      </Grid>

      <Pager page={page} pages={Math.ceil(count / PER_PAGE)} onPage={setPage} />
    </>
  );
}
