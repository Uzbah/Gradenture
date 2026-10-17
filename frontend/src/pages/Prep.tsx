import { useEffect, useState } from "react";
import { Box, Card, Flex, Heading, Text } from "@radix-ui/themes";
import { api, BankQuestion } from "../api";
import { CheckField, Empty, Loading, Notice, Tag } from "../components/ui";
import { useLookups } from "../lookups";

interface PrepData {
  domain_id: string;
  topics: { topic: string; completed: boolean }[];
  score: number;
}

export function ProgressRing({ score, size = 120 }: { score: number; size?: number }) {
  const stroke = 10;
  const r = (size - stroke) / 2;
  const circ = 2 * Math.PI * r;
  return (
    <svg width={size} height={size} role="img" aria-label={`Preparedness ${score}%`}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--gray-a4)" strokeWidth={stroke} />
      <circle
        cx={size / 2} cy={size / 2} r={r} fill="none"
        stroke="var(--accent-9)" strokeWidth={stroke} strokeLinecap="round"
        strokeDasharray={circ} strokeDashoffset={circ * (1 - score / 100)}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
        style={{ transition: "stroke-dashoffset 0.4s" }}
      />
      <text x="50%" y="50%" textAnchor="middle" dominantBaseline="central"
        fontSize={size / 4.5} fontWeight="700" fill="var(--gray-12)">
        {score}%
      </text>
    </svg>
  );
}

export default function Prep() {
  const [data, setData] = useState<PrepData | null>(null);
  const [error, setError] = useState("");
  const [bank, setBank] = useState<BankQuestion[]>([]);
  const { companyName } = useLookups();

  useEffect(() => {
    api<{ data: PrepData }>("/prep/").then((r) => setData(r.data)).catch((e) => setError(e.message));
  }, []);

  // ponytail: first 50 only (API cap); add paging when a domain outgrows it
  useEffect(() => {
    if (!data?.domain_id) return;
    api<{ data: BankQuestion[] }>(`/prep/questions?domain_id=${data.domain_id}&limit=50`)
      .then((r) => setBank(r.data)).catch(() => {});
  }, [data?.domain_id]);

  const toggle = async (topic: string, completed: boolean) => {
    // optimistic update
    setData((d) => d && {
      ...d,
      topics: d.topics.map((t) => (t.topic === topic ? { ...t, completed } : t)),
    });
    try {
      const res = await api<{ data: PrepData }>("/prep/", {
        method: "PATCH", body: { topic, completed },
      });
      setData(res.data);
    } catch (err: any) {
      setError(err.message);
    }
  };

  if (error && !data) return <><Heading size="8" mb="5">Interview Prep</Heading><Notice error={error} /></>;
  if (!data) return <Loading />;

  const done = data.topics.filter((t) => t.completed).length;

  return (
    <>
      <Heading size="8" mb="5">Interview Prep</Heading>
      <Notice error={error} />
      <Card size="3" mb="4">
        <Flex gap="5" align="center" wrap="wrap">
          <ProgressRing score={data.score} />
          <Box>
            <Heading size="5" mb="1">Preparedness score</Heading>
            <Text as="p" size="2" color="gray">
              {done} of {data.topics.length} topics studied in your domain.
              {data.score === 100 ? " You're interview-ready!" : " Check off topics as you study them."}
            </Text>
          </Box>
        </Flex>
      </Card>

      <Card size="3" mb="4">
        <Heading size="5" mb="2">Roadmap topics</Heading>
        <div className="divided">
          {data.topics.map((t) => (
            <Box key={t.topic} py="2">
              <CheckField checked={t.completed} onChange={(v) => toggle(t.topic, v)}>
                <Text color={t.completed ? "gray" : undefined}
                      style={{ textDecoration: t.completed ? "line-through" : undefined }}>
                  {t.topic}
                </Text>
              </CheckField>
            </Box>
          ))}
        </div>
      </Card>

      <Card size="3">
        <Heading size="5" mb="2">Practice questions ({bank.length})</Heading>
        {bank.length === 0 && <Empty>No practice questions for your domain yet.</Empty>}
        <div className="divided">
          {bank.map((q) => (
            <Box key={q.id} py="3">
              <Flex gap="2" align="center" wrap="wrap" mb="1">
                {q.company_id && <Tag>{companyName(q.company_id)}</Tag>}
                {q.question_type !== "technical" && <Tag value={q.question_type} />}
                <Text size="1" color="gray">{q.role_title}</Text>
              </Flex>
              <Text as="p" size="2">{q.question_text}</Text>
            </Box>
          ))}
        </div>
      </Card>
    </>
  );
}
