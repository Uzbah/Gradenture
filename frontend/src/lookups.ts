import { useEffect, useState } from "react";
import { api, ApiResponse, Company, Domain, PageData } from "./api";

// ponytail: fetches first 50 companies only; add search/pagination when the list outgrows one dropdown
export function useLookups() {
  const [domains, setDomains] = useState<Domain[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);

  const reloadCompanies = () =>
    api<ApiResponse<PageData<Company>>>("/companies/?size=50")
      .then((r) => setCompanies(r.data.items)).catch(() => {});

  useEffect(() => {
    api<ApiResponse<Domain[]>>("/domains").then((r) => setDomains(r.data)).catch(() => {});
    reloadCompanies();
  }, []);

  const domainName = (id?: string) => domains.find((d) => d.id === id)?.name ?? "—";
  const companyName = (id?: string) => companies.find((c) => c.id === id)?.name ?? "—";

  return { domains, companies, domainName, companyName, reloadCompanies };
}
