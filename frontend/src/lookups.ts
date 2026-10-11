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

// ponytail: fetches first 50 companies only; add search/pagination when the list outgrows one dropdown
export function useLookups() {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);

  const reloadCompanies = () =>
    api<{ data: Company[] }>("/companies/?limit=50").then((r) => setCompanies(r.data)).catch(() => {});

  useEffect(() => {
    api<{ data: Domain[] }>("/domains").then((r) => setDomains(r.data)).catch(() => {});
    reloadCompanies();
  }, []);

  const domainName = (id?: string) => domains.find((d) => d.id === id)?.name ?? "—";
  const companyName = (id?: string) => companies.find((c) => c.id === id)?.name ?? "—";

  return { domains, companies, domainName, companyName, reloadCompanies };
}
