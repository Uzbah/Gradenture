import { FormEvent, useRef, useState } from "react";
import { Badge, Box, Button, Card, Flex, Heading, Text, TextArea } from "@radix-ui/themes";
import { api } from "../api";
import { Field, Notice } from "../components/ui";

interface Analysis {
  score: number;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  improvements: string[];
  keyword_gaps: string[];
}

export default function Resume() {
  const fileRef = useRef<HTMLInputElement>(null);
  const [jd, setJd] = useState("");
  const [result, setResult] = useState<Analysis | null>(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    const file = fileRef.current?.files?.[0];
    if (!file) return;
    setError(""); setResult(null); setBusy(true);
    const fd = new FormData();
    fd.append("resume", file);
    if (jd.trim()) fd.append("job_description", jd.trim());
    try {
      const res = await api<{ data: Analysis }>("/resume/analyze", { method: "POST", body: fd });
      setResult(res.data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <Heading size="8" mb="5">AI Resume Analyzer</Heading>
      <Card size="3" mb="4" asChild>
        <form onSubmit={submit}>
          <Flex direction="column" gap="4">
            <Field label="Resume" hint="PDF or DOCX, max 5MB">
              <input className="file-input" type="file" ref={fileRef} accept=".pdf,.docx" required />
            </Field>
            <Field label="Job description (optional)" hint="Enables keyword gap analysis">
              <TextArea rows={5} value={jd} onChange={(e) => setJd(e.target.value)}
                        placeholder="Paste the job description here…" />
            </Field>
            <Notice error={error} />
            <Flex align="center" gap="3" wrap="wrap">
              <Button size="3" loading={busy}>Analyze</Button>
              <Text size="2" color="gray">
                {busy ? "Analyzing… this takes ~15s." : "Limited to 3 analyses per hour."}
              </Text>
            </Flex>
          </Flex>
        </form>
      </Card>

      {result && (
        <Card size="3">
          <Flex align="center" gap="3" mb="3">
            <Heading size="6">Score</Heading>
            <Badge size="3" variant="solid">{result.score}/10</Badge>
          </Flex>
          <Text as="p">{result.summary}</Text>
          <Section title="Strengths" items={result.strengths} />
          <Section title="Weaknesses" items={result.weaknesses} />
          <Section title="Improvements" items={result.improvements} />
          <Section title="Missing keywords" items={result.keyword_gaps} />
        </Card>
      )}
    </>
  );
}

function Section({ title, items }: { title: string; items: string[] }) {
  if (!items?.length) return null;
  return (
    <Box mt="4">
      <Heading size="4" mb="2">{title}</Heading>
      <ul style={{ paddingLeft: "1.25rem", margin: 0 }}>
        {items.map((s, i) => <li key={i}><Text size="2">{s}</Text></li>)}
      </ul>
    </Box>
  );
}
