from src.config.supabase import supabase
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
}


def _get_user_domain(user_id: str) -> tuple[str, str]:
    result = (
        supabase.table("users")
        .select("domain_id, domains(slug)")
        .eq("id", user_id)
        .maybe_single()
        .execute()
    )
    if not result.data or not result.data.get("domain_id"):
        raise AppError(400, {"error": "Complete onboarding first"})
    return result.data["domain_id"], result.data["domains"]["slug"]


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
