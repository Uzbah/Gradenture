import { useEffect, useState } from "react";
import { api, Company, Domain } from "./api";

// Shared by Onboarding and Profile; values match the users table CHECKs.
export const SKILL_LEVELS = [
  { value: "beginner", label: "Beginner" },
  { value: "intermediate", label: "Intermediate" },
  { value: "advanced", label: "Advanced" },
];
export const GOALS = [
  { value: "internship", label: "Internship hunting" },
  { value: "first_job", label: "First full-time job" },
  { value: "switch_career", label: "Switch career" },
  { value: "level_up", label: "General upskilling" },
];

// ponytail: the whole approved registry, paged 50 at a time (the API cap) and
// cached for the session. Previously only the first 50 loaded, so company #51+
// showed as "—" and could not be picked. Replace the <select>s with server-side
// search (/companies?q=) once the registry reaches a few hundred.
let domainsCache: Promise<Domain[]> | null = null;
let companiesCache: Promise<Company[]> | null = null;

async function fetchAllCompanies(): Promise<Company[]> {
  const all: Company[] = [];
  for (let page = 1; ; page++) {
    const r = await api<{ data: Company[]; count: number }>(`/companies/?limit=50&page=${page}`);
    all.push(...r.data);
    if (r.data.length === 0 || all.length >= r.count) return all;
  }
}

export function useLookups() {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);

  const loadCompanies = (fresh = false) => {
    if (fresh || !companiesCache) {
      companiesCache = fetchAllCompanies();
      companiesCache.catch(() => { companiesCache = null; });
    }
    companiesCache.then(setCompanies).catch(() => {});
  };

  useEffect(() => {
    domainsCache ??= api<{ data: Domain[] }>("/domains").then((r) => r.data);
    domainsCache.then(setDomains).catch(() => { domainsCache = null; });
    loadCompanies();
  }, []);

  const domainName = (id?: string) => domains.find((d) => d.id === id)?.name ?? "—";
  const companyName = (id?: string) => companies.find((c) => c.id === id)?.name ?? "—";

  return { domains, companies, domainName, companyName, reloadCompanies: () => loadCompanies(true) };
}

// Enum options for <Choice>; values match the DB CHECKs / Postgres enums.
export const DIFFICULTIES = [
  { value: "easy", label: "Easy" },
  { value: "medium", label: "Medium" },
  { value: "hard", label: "Hard" },
];
export const QUESTION_TYPES = [
  { value: "technical", label: "Technical" },
  { value: "behavioural", label: "Behavioural" },
  { value: "hr", label: "HR" },
  { value: "case_study", label: "Case study" },
];
export const OUTCOMES = [
  { value: "offer", label: "Offer received" },
  { value: "rejected", label: "Rejected" },
  { value: "pending", label: "Pending" },
  { value: "withdrew", label: "Withdrew" },
  { value: "ghosted", label: "Ghosted" },
];
