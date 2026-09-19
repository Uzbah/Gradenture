import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, ApiResponse, Company, PageData } from "../api";

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
      const params = new URLSearchParams({ page: String(page), size: String(PER_PAGE) });
      if (q.trim()) params.set("q", q.trim());
      api<ApiResponse<PageData<Company>>>(`/companies/?${params}`)
        .then((r) => { setCompanies(r.data.items); setCount(r.data.total); })
        .catch((e) => setError(e.message));
    }, 250);
    return () => clearTimeout(t);
  }, [page, q]);

  const pages = Math.max(1, Math.ceil(count / PER_PAGE));

  return (
    <>
      <div className="row" style={{ justifyContent: "space-between", marginBottom: "1rem" }}>
        <h1 style={{ margin: 0 }}>Companies</h1>
        <span className="muted">{count} in the registry</span>
      </div>

      <div className="filters">
        <input
          placeholder="Search companies…"
          value={q}
          onChange={(e) => { setQ(e.target.value); setPage(1); }}
        />
      </div>

      {error && <p className="error">{error}</p>}
      {companies.length === 0 && !error && (
        <p className="muted">{q ? `No companies match “${q}”.` : "No companies yet."}</p>
      )}

      <div className="stat-grid">
        {companies.map((c) => (
          <Link key={c.id} to={`/companies/${c.id}`} className="card" style={{ display: "block" }}>
            <strong>{c.name}</strong>
            <div className="row mt">
              {c.industry && <span className="badge">{c.industry}</span>}
            </div>
          </Link>
        ))}
      </div>

      {pages > 1 && (
        <div className="row mt" style={{ justifyContent: "center" }}>
          <button className="small secondary" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
            Previous
          </button>
          <span className="muted">Page {page} of {pages}</span>
          <button className="small secondary" disabled={page >= pages} onClick={() => setPage((p) => p + 1)}>
            Next
          </button>
        </div>
      )}
    </>
  );
}
