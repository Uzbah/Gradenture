import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, Company, Question, Review } from "../api";
import { useLookups } from "../lookups";

export default function CompanyProfile() {
  const { companyId } = useParams();
  const { domainName } = useLookups();
  const [company, setCompany] = useState<Company | null>(null);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [tab, setTab] = useState<"questions" | "reviews">("questions");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!companyId) return;
    api<{ data: Company }>(`/companies/${companyId}`)
      .then((r) => setCompany(r.data))
      .catch((e) => setError(e.message));
    api<{ data: Question[] }>(`/questions/?company_id=${companyId}&limit=50`)
      .then((r) => setQuestions(r.data)).catch(() => {});
    api<{ data: Review[] }>(`/reviews/?company_id=${companyId}&limit=50`)
      .then((r) => setReviews(r.data)).catch(() => {});
  }, [companyId]);

  if (error) return <p className="error">{error}</p>;
  if (!company) return <p className="muted">Loading…</p>;

  const offers = reviews.filter((r) => r.outcome === "offer").length;
  const withOutcome = reviews.filter((r) => r.outcome && r.outcome !== "pending").length;

  return (
    <>
      <Link to="/companies" className="muted">← All companies</Link>

      <div className="card mt">
        <h1 style={{ marginBottom: "0.5rem" }}>{company.name}</h1>
        <div className="row">
          {company.industry && <span className="badge">{company.industry}</span>}
          {company.website && (
            <a href={company.website} target="_blank" rel="noreferrer">{company.website}</a>
          )}
        </div>
      </div>

      <div className="stat-grid mt">
        <div className="stat"><strong>{questions.length}</strong><span className="muted">Questions</span></div>
        <div className="stat"><strong>{reviews.length}</strong><span className="muted">Reviews</span></div>
        <div className="stat">
          <strong>{withOutcome ? `${Math.round((offers / withOutcome) * 100)}%` : "—"}</strong>
          <span className="muted">Offer rate</span>
        </div>
      </div>

      <div className="tabs mt">
        <button className={tab === "questions" ? "active" : ""} onClick={() => setTab("questions")}>
          Questions ({questions.length})
        </button>
        <button className={tab === "reviews" ? "active" : ""} onClick={() => setTab("reviews")}>
          Reviews ({reviews.length})
        </button>
      </div>

      {tab === "questions" ? (
        questions.length === 0 ? (
          <p className="muted">No approved questions for {company.name} yet.</p>
        ) : (
          questions.map((q) => (
            <div className="card" key={q.id}>
              <div className="row" style={{ marginBottom: "0.4rem" }}>
                <span className="badge">{domainName(q.domain_id)}</span>
                <span className={`badge ${q.difficulty}`}>{q.difficulty}</span>
                <span className="muted">{q.role_title}</span>
              </div>
              <p>{q.question_text}</p>
            </div>
          ))
        )
      ) : reviews.length === 0 ? (
        <p className="muted">No approved reviews for {company.name} yet.</p>
      ) : (
        reviews.map((r) => (
          <div className="card" key={r.id}>
            <div className="row" style={{ marginBottom: "0.4rem" }}>
              {r.outcome && <span className="badge">{r.outcome}</span>}
              <span className="muted">
                {r.role_title} · {new Date(r.interview_date).toLocaleDateString()}
              </span>
            </div>
            <p>{r.review_text}</p>
          </div>
        ))
      )}
    </>
  );
}
