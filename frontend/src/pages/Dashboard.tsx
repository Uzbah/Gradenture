import { useEffect, useState } from "react";
import { Link as RouterLink } from "react-router-dom";
import { Box, Button, Card, Flex, Grid, Heading, Text } from "@radix-ui/themes";
import { api, Application, Question } from "../api";
import { useAuth } from "../auth";
import { Empty, RLink, Stat, Tag } from "../components/ui";

// ponytail: users have no name column, so guess it from the email:
// "taufeeq.mustafa@x.com" -> "Taufeeq". Use the real field if one is added.
const firstName = (email: string) => {
  const part = email.split("@")[0].split(/[._+\-\d]/).find(Boolean) ?? "";
  return part.charAt(0).toUpperCase() + part.slice(1).toLowerCase();
};

const ACTIONS = [
  { to: "/questions", label: "Submit a question" },
  { to: "/reviews", label: "Write a review" },
  { to: "/applications", label: "Track an application" },
  { to: "/resume", label: "Analyze my resume" },
];

export default function Dashboard() {
  const { user } = useAuth();
  const [apps, setApps] = useState<Application[]>([]);
  const [questionCount, setQuestionCount] = useState<number | null>(null);
  const [recent, setRecent] = useState<Question[]>([]);
  const [prepScore, setPrepScore] = useState<number | null>(null);

  useEffect(() => {
    api<{ data: Application[] }>("/applications/?limit=50").then((r) => setApps(r.data)).catch(() => {});
    api<{ data: Question[]; count: number }>("/questions/?limit=5")
      .then((r) => { setRecent(r.data); setQuestionCount(r.count); })
      .catch(() => {});
    api<{ data: { score: number } }>("/prep/").then((r) => setPrepScore(r.data.score)).catch(() => {});
  }, []);

  const count = (s: string) => apps.filter((a) => a.status === s).length;

  return (
    <>
      <Heading size="8" mb="5">Welcome back, {firstName(user?.email ?? "")}</Heading>
      <Grid columns={{ initial: "2", sm: "3", md: "5" }} gap="3" mb="5">
        <Stat value={count("applied")} label="Applied" />
        <Stat value={count("interview")} label="Interviews" />
        <Stat value={count("offer")} label="Offers" />
        <Stat value={questionCount ?? "—"} label="Community questions" />
        <Stat highlight value={prepScore !== null ? `${prepScore}%` : "—"}
              label={<RLink to="/prep" underline="always">Preparedness</RLink>} />
      </Grid>

      <Card size="3" mb="4">
        <Heading size="5" mb="3">Latest interview questions</Heading>
        {recent.length === 0 && (
          <Empty>No approved questions yet. <RLink to="/questions">Be the first to submit one</RLink>.</Empty>
        )}
        <Flex direction="column" gap="3">
          {recent.map((q) => (
            <Flex key={q.id} gap="2" align="start">
              <Tag value={q.difficulty} />
              <Text size="2">
                {q.question_text.slice(0, 120)}{q.question_text.length > 120 ? "…" : ""}
                <Text color="gray"> — {q.role_title}</Text>
              </Text>
            </Flex>
          ))}
        </Flex>
        <Box mt="4"><RLink to="/questions" size="2">Browse all questions →</RLink></Box>
      </Card>

      <Card size="3">
        <Heading size="5" mb="3">Quick actions</Heading>
        <Flex gap="3" wrap="wrap">
          {ACTIONS.map((a) => (
            <Button key={a.to} asChild variant="soft">
              <RouterLink to={a.to}>{a.label}</RouterLink>
            </Button>
          ))}
        </Flex>
      </Card>
    </>
  );
}
