from src.config.supabase import maybe_row, supabase
from src.dependencies.exceptions import AppError

# ponytail: static topic lists keyed by domain slug; move to an admin-curated
# roadmaps table when admins need to edit content without a deploy
TOPICS: dict[str, list[str]] = {
    "software-engineering": [
        "Data Structures & Algorithms",
        "System Design Basics",
        "Databases & SQL",
        "REST APIs & HTTP",
        "Git & Version Control",
        "Testing & Debugging",
        "OOP & Design Patterns",
        "Behavioural / STAR Method",
    ],
    "data-science-ai": [
        "Statistics & Probability",
        "Python & Pandas",
        "SQL for Analytics",
        "Machine Learning Fundamentals",
        "Model Evaluation & Metrics",
        "Deep Learning Basics",
        "Data Storytelling & Visualization",
        "Behavioural / STAR Method",
    ],
    "finance-banking": [
        "Financial Statements",
        "Valuation Methods",
        "Excel & Financial Modeling",
        "Market & Economic Awareness",
        "Accounting Fundamentals",
        "Risk & Compliance Basics",
        "Behavioural / STAR Method",
    ],
    "marketing-sales": [
        "Marketing Fundamentals & 4Ps",
        "Digital Marketing Channels",
        "Analytics & KPIs",
        "Copywriting & Communication",
        "CRM & Sales Process",
        "Case Study Practice",
        "Behavioural / STAR Method",
    ],
    "product-management": [
        "Product Sense & Design Questions",
        "Metrics & Analytics",
        "Prioritization Frameworks",
        "Technical Fluency Basics",
        "Market & User Research",
        "Case Study Practice",
        "Behavioural / STAR Method",
    ],
    "human-resources": [
        "Recruitment & Selection",
        "Employment Law Basics",
        "Performance Management",
        "Compensation & Benefits",
        "HR Analytics",
        "Conflict Resolution",
        "Behavioural / STAR Method",
    ],
    "accounting": [
        "Journal Entries & Ledgers",
        "Financial Statements",
        "IFRS / GAAP Basics",
        "Taxation Fundamentals",
        "Auditing Basics",
        "Excel Skills",
        "Behavioural / STAR Method",
    ],
    "consulting": [
        "Case Interview Frameworks",
        "Market Sizing / Guesstimates",
        "Profitability Cases",
        "Mental Math & Charts",
        "Structured Communication",
        "Industry Awareness",
        "Behavioural / STAR Method",
    ],
    "ui-ux-design": [
        "UI vs UX Fundamentals",
        "User Research & Problem Discovery",
        "Wireframes, Mockups & Prototypes",
        "Figma (Auto Layout, Components, Libraries)",
        "Design Systems & Consistency",
        "Mobile & Responsive UX",
        "Portfolio & Case Studies",
        "Behavioural / STAR Method",
    ],
    "quality-assurance": [
        "SDLC & STLC",
        "Test Cases & Test Scenarios",
        "Manual & Exploratory Testing",
        "Bug Reporting (Priority vs Severity)",
        "API Testing (Postman)",
        "Test Automation (Cypress, POM)",
        "Performance Testing (JMeter)",
        "Behavioural / STAR Method",
    ],
}


def _get_user_domain(user_id: str) -> tuple[str, str]:
    row = maybe_row(
        supabase.table("users").select("domain_id, domains(slug)").eq("id", user_id)
    )
    if not row or not row.get("domain_id"):
        raise AppError(400, {"error": "Complete onboarding first"})
    return row["domain_id"], row["domains"]["slug"]


def get_prep(user: dict) -> dict:
    user_id = user["sub"]
    domain_id, slug = _get_user_domain(user_id)
    topics = TOPICS.get(slug, [])

    rows = (
        supabase.table("prep_progress")
        .select("topic, completed")
        .eq("user_id", user_id)
        .eq("domain_id", domain_id)
        .execute()
    ).data
    done = {r["topic"] for r in rows if r["completed"]}

    topic_list = [{"topic": t, "completed": t in done} for t in topics]
    completed_count = sum(1 for t in topic_list if t["completed"])
    score = round(100 * completed_count / len(topics)) if topics else 0

    return {"data": {"domain_id": domain_id, "topics": topic_list, "score": score}}


def toggle_topic(user: dict, topic: str, completed: bool) -> dict:
    user_id = user["sub"]
    domain_id, slug = _get_user_domain(user_id)
    if topic not in TOPICS.get(slug, []):
        raise AppError(400, {"error": "Unknown topic for your domain"})

    supabase.table("prep_progress").upsert(
        {
            "user_id":   user_id,
            "domain_id": domain_id,
            "topic":     topic,
            "completed": completed,
        },
        on_conflict="user_id,domain_id,topic",
    ).execute()

    return get_prep(user)


def list_bank_questions(
    page: int = 1,
    limit: int = 20,
    domain_id: str | None = None,
    company_id: str | None = None,
    role_title: str | None = None,
    q: str | None = None,
    question_type: str | None = None,
    difficulty: str | None = None,
) -> dict:
    """Curated question_bank — separate from community interview_questions."""
    page = max(1, page)
    limit = min(50, max(1, limit))
    offset = (page - 1) * limit

    query = supabase.table("question_bank").select(
        "id, domain_id, company_id, role_title, question_text, question_type, difficulty",
        count="exact",
    )
    for field, val in (
        ("domain_id", domain_id),
        ("company_id", company_id),
        ("role_title", role_title),
        ("question_type", question_type),
        ("difficulty", difficulty),
    ):
        if val:
            query = query.eq(field, val)

    query = query.order("role_title").order("question_text").range(offset, offset + limit - 1)
    # text_search returns a builder with no .order/.range, so it must come last
    if q:
        query = query.text_search("search", q, options={"type": "web_search", "config": "english"})

    result = query.execute()
    return {"data": result.data, "count": result.count}
