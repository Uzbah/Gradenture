"use client";

import { useState, useMemo } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

// ── Types ──────────────────────────────────────────────────────────────────────
type QuestionTab = "All" | "DSA" | "OOP" | "System Design" | "SQL";

interface Stage {
  num:   number;
  title: string;
  desc:  string;
}

interface Question {
  id:      number;
  text:    string;
  tags:    string[];
  round:   string;
  year:    string;
  upvotes: number;
}

interface Experience {
  id:      number;
  name:    string;
  role:    string;
  date:    string;
  outcome: "Offered" | "Rejected" | "Pending";
  summary: string;
  tips:    string[];
}

// ── Static mock data (CloudScale Solutions) ────────────────────────────────────
const COMPANY = {
  name:       "CloudScale Solutions",
  sector:     "SaaS",
  city:       "Karachi, PK",
  website:    "cloudscale.io",
  difficulty: "Medium",
  domains:    ["Backend", "Cloud", "Docker"],
  tags:       ["Asks DSA", "Take-home project", "Negotiable Salary", "Remote Friendly"],
  rounds:     3,
  format:     "Onsite",
  duration:   "45–60 min",
  icon:       "cloud",
  stages: [
    { num: 1, title: "HR Screening Call",     desc: "General background, salary expectations & culture fit." },
    { num: 2, title: "Technical Assessment",  desc: "Take-home project or live coding (DSA + backend system)." },
    { num: 3, title: "System Design Panel",   desc: "Design a scalable API or distributed service with 2 engineers." },
  ] as Stage[],
  tips: [
    "Brush up on Docker networking and container orchestration basics.",
    "Expect at least one LeetCode medium on arrays or graphs.",
    "They value clean code over brute-force solutions.",
    "System design should mention horizontal scaling and caching.",
    "Ask about the tech stack early — they appreciate curiosity.",
  ],
};

const QUESTIONS: Question[] = [
  { id: 1, text: "Given a list of server logs, find the top-K most frequent error codes.",  tags: ["Heap", "HashMap"],         round: "Technical", year: "2024", upvotes: 14 },
  { id: 2, text: "Design a URL shortener service. Discuss DB schema and cache layer.",       tags: ["System Design", "Cache"],  round: "Panel",     year: "2024", upvotes: 21 },
  { id: 3, text: "Explain the difference between Docker volumes and bind mounts.",           tags: ["Docker", "DevOps"],        round: "HR",        year: "2023", upvotes: 9  },
  { id: 4, text: "Implement a Least Recently Used (LRU) cache in Python.",                  tags: ["DSA", "OOP"],              round: "Technical", year: "2024", upvotes: 17 },
  { id: 5, text: "Write a SQL query to find employees who earn more than their manager.",    tags: ["SQL", "Joins"],            round: "Technical", year: "2023", upvotes: 11 },
  { id: 6, text: "How would you design a rate-limiter for a REST API?",                     tags: ["System Design", "API"],    round: "Panel",     year: "2024", upvotes: 19 },
  { id: 7, text: "What are SOLID principles? Give a real-world example for each.",          tags: ["OOP"],                     round: "Technical", year: "2023", upvotes: 8  },
  { id: 8, text: "Find the longest substring without repeating characters.",                tags: ["DSA", "Sliding Window"],   round: "Technical", year: "2024", upvotes: 13 },
];

const EXPERIENCES: Experience[] = [
  {
    id:      1,
    name:    "Hamza R.",
    role:    "Backend Engineer Intern",
    date:    "March 2024",
    outcome: "Offered",
    summary: "3 rounds over 2 weeks. HR was straightforward. Take-home was a Node.js REST API with JWT auth and pagination — 48 hours. Final panel asked about Docker and system design. Team was welcoming and gave feedback.",
    tips:    ["Submit clean, well-documented code for the take-home.", "Review Docker Compose before the panel.", "Negotiate — they have room."],
  },
  {
    id:      2,
    name:    "Ayesha K.",
    role:    "Full-Stack Developer",
    date:    "January 2024",
    outcome: "Rejected",
    summary: "Made it to the system design round but struggled with the caching layer question. Feedback was helpful — they said my solution was correct but lacked depth on trade-offs. Would apply again.",
    tips:    ["Study CAP theorem.", "Think out loud during design.", "Prepare a Redis-based caching example."],
  },
];

const TABS: QuestionTab[] = ["All", "DSA", "OOP", "System Design", "SQL"];

const TAB_FILTER: Record<QuestionTab, (q: Question) => boolean> = {
  "All":           ()  => true,
  "DSA":           (q) => q.tags.some((t) => ["DSA", "Heap", "HashMap", "Sliding Window"].includes(t)),
  "OOP":           (q) => q.tags.includes("OOP"),
  "System Design": (q) => q.tags.includes("System Design"),
  "SQL":           (q) => q.tags.includes("SQL"),
};

const OUTCOME_STYLES: Record<string, string> = {
  Offered:  "bg-green-50 text-green-700",
  Rejected: "bg-red-50 text-red-700",
  Pending:  "bg-amber-50 text-amber-700",
};

const DIFF_STYLES: Record<string, string> = {
  Easy:   "bg-green-50 text-green-700",
  Medium: "bg-amber-50 text-amber-700",
  Hard:   "bg-red-50 text-red-700",
};

// ── Sub-components ─────────────────────────────────────────────────────────────
function InterviewProcessCard() {
  return (
    <div className="bg-white rounded-2xl p-6 shadow-[0_10px_30px_rgba(0,0,0,0.04)] space-y-5">
      <h2 className="font-bold text-base tracking-tight">Interview Process</h2>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3 text-center">
        {[
          { label: "Rounds",   value: COMPANY.rounds   },
          { label: "Format",   value: COMPANY.format   },
          { label: "Duration", value: COMPANY.duration },
        ].map(({ label, value }) => (
          <div key={label} className="bg-[#f3f3f3] rounded-xl p-3">
            <p className="text-[10px] font-bold uppercase tracking-widest text-[#777587] mb-1">{label}</p>
            <p className="font-bold text-sm text-[#1a1c1c]">{value}</p>
          </div>
        ))}
      </div>

      {/* Stages */}
      <div className="space-y-4">
        {COMPANY.stages.map((s) => (
          <div key={s.num} className="flex gap-3">
            <div className="flex-shrink-0 w-7 h-7 rounded-full bg-[#3525cd] text-white text-xs font-bold flex items-center justify-center">
              {s.num}
            </div>
            <div className="min-w-0">
              <p className="font-bold text-sm text-[#1a1c1c]">{s.title}</p>
              <p className="text-xs text-[#464555] mt-0.5 leading-relaxed">{s.desc}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function GeneralTipsCard() {
  return (
    <div className="bg-[#eeeeff] rounded-2xl p-6 space-y-4">
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <h2 className="font-bold text-base tracking-tight text-[#1a1c1c]">General Tips</h2>
        <span className="inline-flex items-center gap-1 bg-[#3525cd]/10 text-[#3525cd] text-[9px] font-bold uppercase tracking-widest px-2 py-1 rounded-full">
          <span className="material-symbols-outlined text-[12px]">verified</span>
          Admin curated
        </span>
      </div>
      <ul className="space-y-3">
        {COMPANY.tips.map((tip, i) => (
          <li key={i} className="flex gap-2.5 items-start">
            <span
              className="material-symbols-outlined text-[#3525cd] text-[18px] flex-shrink-0 mt-px"
              style={{ fontVariationSettings: "'FILL' 1" }}
            >
              check_circle
            </span>
            <span className="text-sm text-[#1a1c1c] leading-relaxed">{tip}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function SubmitCTACards() {
  return (
    <div className="space-y-3">
      <div className="bg-white rounded-2xl p-5 border border-[#e2dfff] space-y-2">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[#3525cd] text-xl">quiz</span>
          <p className="font-bold text-sm text-[#1a1c1c]">Interviewed here?</p>
        </div>
        <p className="text-xs text-[#464555] leading-relaxed">Share questions you were asked to help future candidates.</p>
        <button className="mt-1 w-full bg-[#3525cd] hover:bg-[#4f46e5] text-white font-bold py-2.5 rounded-xl text-xs transition-colors active:scale-[0.98]">
          Add a Question
        </button>
      </div>
      <div className="bg-white rounded-2xl p-5 border border-[#e2dfff] space-y-2">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-[#3525cd] text-xl">rate_review</span>
          <p className="font-bold text-sm text-[#1a1c1c]">Write your experience</p>
        </div>
        <p className="text-xs text-[#464555] leading-relaxed">How did your interview go? Let the community know.</p>
        <button className="mt-1 w-full bg-white hover:bg-[#f3f3f3] text-[#3525cd] font-bold py-2.5 rounded-xl text-xs transition-colors border border-[#3525cd]/30 active:scale-[0.98]">
          Write a Review
        </button>
      </div>
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────
export default function CompanyDetailPage() {
  const router = useRouter();
  const [activeTab,    setActiveTab]    = useState<QuestionTab>("All");
  const [upvoted,      setUpvoted]      = useState<Set<number>>(new Set());
  const [upvoteCounts, setUpvoteCounts] = useState<Record<number, number>>(
    () => Object.fromEntries(QUESTIONS.map((q) => [q.id, q.upvotes]))
  );

  const filteredQs = useMemo(
    () => QUESTIONS.filter(TAB_FILTER[activeTab]),
    [activeTab]
  );

  function toggleUpvote(id: number) {
    setUpvoted((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
        setUpvoteCounts((c) => ({ ...c, [id]: c[id] - 1 }));
      } else {
        next.add(id);
        setUpvoteCounts((c) => ({ ...c, [id]: c[id] + 1 }));
      }
      return next;
    });
  }

  const waText = encodeURIComponent(`Check out ${COMPANY.name}'s interview prep profile on KHI Tech Prep!`);
  const waUrl  = `https://wa.me/?text=${waText}`;

  return (
    <div className="bg-[#f9f9f9] min-h-dvh pb-32 lg:pb-12" style={{ color: "#1a1c1c", fontFamily: "Inter, sans-serif" }}>

      {/* ━━━━ Header ━━━━ */}
      <header className="sticky top-0 z-50 bg-[#f9f9f9]/90 backdrop-blur-md shadow-sm">
        <div className="flex justify-between items-center px-6 lg:px-8 py-4 max-w-7xl mx-auto">

          <div className="flex items-center gap-3">
            <button
              onClick={() => router.back()}
              className="p-1.5 rounded-full hover:bg-[#f3f3f3] transition-colors"
              aria-label="Go back"
            >
              <span className="material-symbols-outlined text-[#1a1c1c]">arrow_back</span>
            </button>
            <Link href="/" className="flex items-center gap-2">
              <span className="material-symbols-outlined text-[#3525cd] text-2xl">grid_view</span>
              <span className="hidden sm:block text-xl font-bold tracking-tighter text-[#3525cd]">KHI Tech Prep</span>
            </Link>
          </div>

          <nav className="hidden md:flex items-center gap-1 font-bold">
            <Link href="/jobs"      className="px-4 py-2 rounded-lg text-[#1a1c1c]/70 hover:bg-[#f3f3f3] transition-colors text-sm">Jobs</Link>
            <Link href="/companies" className="px-4 py-2 rounded-lg text-[#3525cd] text-sm">Companies</Link>
            <Link href="#"          className="px-4 py-2 rounded-lg text-[#1a1c1c]/70 hover:bg-[#f3f3f3] transition-colors text-sm">Saved</Link>
          </nav>

          <div className="w-8 h-8 rounded-full bg-[#e8e8e8] ring-2 ring-[#e2dfff] flex items-center justify-center cursor-pointer hover:opacity-75 transition-opacity">
            <span className="material-symbols-outlined text-[#464555] text-lg">person</span>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 lg:px-8 pt-8 pb-4">

        {/* ━━━━ Company Profile Header ━━━━ */}
        <section className="bg-white rounded-2xl p-6 shadow-[0_10px_30px_rgba(0,0,0,0.04)] mb-8 space-y-5">
          <div className="flex flex-col sm:flex-row sm:items-center gap-5">
            <div className="w-16 h-16 sm:w-20 sm:h-20 bg-[#f3f3f3] rounded-2xl flex items-center justify-center flex-shrink-0">
              <span className="material-symbols-outlined text-[#3525cd] text-4xl">{COMPANY.icon}</span>
            </div>
            <div className="flex-1 min-w-0 space-y-2">
              <div className="flex flex-wrap items-center gap-2">
                <h1 className="text-2xl lg:text-3xl font-bold tracking-tight">{COMPANY.name}</h1>
                <span className={`px-3 py-1 rounded-full text-[10px] font-bold tracking-widest uppercase ${DIFF_STYLES[COMPANY.difficulty] ?? ""}`}>
                  {COMPANY.difficulty}
                </span>
              </div>
              <div className="flex flex-wrap items-center gap-3 text-sm text-[#464555] font-medium">
                <span>{COMPANY.sector}</span>
                <span className="w-1 h-1 bg-[#c7c4d8] rounded-full" />
                <span>{COMPANY.city}</span>
                <span className="w-1 h-1 bg-[#c7c4d8] rounded-full" />
                <a
                  href={`https://${COMPANY.website}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 text-[#3525cd] hover:underline underline-offset-4"
                >
                  <span className="material-symbols-outlined text-[14px]">open_in_new</span>
                  {COMPANY.website}
                </a>
              </div>
              <div className="flex flex-wrap gap-2">
                {COMPANY.domains.map((d) => (
                  <span key={d} className="px-3 py-1 rounded-md bg-[#e2dfff] text-[#3323cc] text-[11px] font-bold">{d}</span>
                ))}
              </div>
            </div>
          </div>

          {/* Scrollable tags */}
          <div className="flex gap-2 overflow-x-auto no-scrollbar pb-1">
            {COMPANY.tags.map((t) => (
              <span
                key={t}
                className="flex-shrink-0 px-3 py-1.5 rounded-full border border-[#c7c4d8]/40 text-[11px] font-semibold italic text-[#464555] bg-[#f9f9f9] whitespace-nowrap"
              >
                {t}
              </span>
            ))}
          </div>
        </section>

        {/* ━━━━ Two-column layout ━━━━ */}
        <div className="lg:grid lg:grid-cols-3 lg:gap-8 space-y-8 lg:space-y-0">

          {/* Left Column */}
          <div className="lg:col-span-2 space-y-8">

            {/* Interview Process — mobile only */}
            <div className="lg:hidden">
              <InterviewProcessCard />
            </div>

            {/* Question Bank */}
            <section className="bg-white rounded-2xl shadow-[0_10px_30px_rgba(0,0,0,0.04)] overflow-hidden">
              <div className="px-6 pt-6 pb-0 flex items-center justify-between gap-2 flex-wrap mb-4">
                <div>
                  <h2 className="font-bold text-base tracking-tight">Question Bank</h2>
                  <p className="text-[#464555] text-xs mt-0.5">{filteredQs.length} question{filteredQs.length !== 1 ? "s" : ""}</p>
                </div>
                <button className="hidden sm:inline-flex items-center gap-1 text-xs font-bold text-[#3525cd] hover:underline underline-offset-4">
                  <span className="material-symbols-outlined text-[14px]">add</span>
                  Add Question
                </button>
              </div>

              {/* Tabs */}
              <div className="flex gap-1 overflow-x-auto no-scrollbar px-6 border-b border-[#f3f3f3]">
                {TABS.map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`flex-shrink-0 px-4 py-2.5 text-xs font-bold whitespace-nowrap border-b-2 transition-all ${
                      activeTab === tab
                        ? "border-[#3525cd] text-[#3525cd]"
                        : "border-transparent text-[#777587] hover:text-[#464555]"
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {/* Questions */}
              <div className="divide-y divide-[#f3f3f3]">
                {filteredQs.length === 0 ? (
                  <div className="text-center py-12 text-[#464555]">
                    <span className="material-symbols-outlined text-4xl text-[#c7c4d8] block mb-2">search_off</span>
                    <p className="text-sm font-semibold">No questions in this category yet</p>
                  </div>
                ) : filteredQs.map((q) => {
                  const isUp = upvoted.has(q.id);
                  return (
                    <div key={q.id} className="px-6 py-4 flex gap-4 hover:bg-[#f9f9f9] transition-colors">
                      {/* Upvote */}
                      <div className="flex flex-col items-center flex-shrink-0 pt-0.5">
                        <button
                          onClick={() => toggleUpvote(q.id)}
                          className={`p-1 rounded-lg transition-all active:scale-90 ${
                            isUp ? "text-[#3525cd]" : "text-[#c7c4d8] hover:text-[#777587]"
                          }`}
                          aria-label={isUp ? "Remove upvote" : "Upvote"}
                        >
                          <span
                            className="material-symbols-outlined text-xl"
                            style={{ fontVariationSettings: isUp ? "'FILL' 1" : "'FILL' 0" }}
                          >
                            arrow_upward
                          </span>
                        </button>
                        <span className={`text-[11px] font-bold ${isUp ? "text-[#3525cd]" : "text-[#777587]"}`}>
                          {upvoteCounts[q.id]}
                        </span>
                      </div>

                      {/* Content */}
                      <div className="flex-1 min-w-0 space-y-2">
                        <p className="text-sm font-medium text-[#1a1c1c] leading-relaxed">{q.text}</p>
                        <div className="flex flex-wrap gap-1.5">
                          {q.tags.map((t) => (
                            <span key={t} className="px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider text-[#777587] border border-[#c7c4d8]/30 rounded">
                              {t}
                            </span>
                          ))}
                          <span className="px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider text-[#3525cd] border border-[#3525cd]/20 bg-[#e2dfff]/30 rounded">
                            {q.round}
                          </span>
                          <span className="px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider text-[#777587] bg-[#f3f3f3] rounded">
                            {q.year}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>

            {/* Candidate Experiences */}
            <section className="space-y-4">
              <div className="flex items-center justify-between gap-2 flex-wrap">
                <h2 className="font-bold text-base tracking-tight">Candidate Experiences</h2>
                <button className="inline-flex items-center gap-1 text-xs font-bold text-[#3525cd] hover:underline underline-offset-4">
                  <span className="material-symbols-outlined text-[14px]">add</span>
                  Add Yours
                </button>
              </div>

              {EXPERIENCES.map((exp) => (
                <div key={exp.id} className="bg-white rounded-2xl shadow-[0_10px_30px_rgba(0,0,0,0.04)] overflow-hidden border-l-4 border-[#3525cd]/30">
                  <div className="p-6 space-y-4">
                    <div className="flex items-start justify-between gap-2 flex-wrap">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-[#e2dfff] flex items-center justify-center flex-shrink-0">
                          <span className="material-symbols-outlined text-[#3525cd] text-lg">person</span>
                        </div>
                        <div>
                          <p className="font-bold text-sm text-[#1a1c1c]">{exp.name}</p>
                          <p className="text-[11px] text-[#464555]">{exp.role} · {exp.date}</p>
                        </div>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-[10px] font-bold tracking-widest uppercase ${OUTCOME_STYLES[exp.outcome]}`}>
                        {exp.outcome}
                      </span>
                    </div>

                    <p className="text-sm text-[#464555] leading-relaxed">{exp.summary}</p>

                    <div className="bg-[#f9f9f9] rounded-xl p-4 space-y-2">
                      <p className="text-[10px] font-bold uppercase tracking-widest text-[#777587]">Their Tips</p>
                      <ul className="space-y-1.5">
                        {exp.tips.map((tip, i) => (
                          <li key={i} className="flex gap-2 items-start">
                            <span
                              className="material-symbols-outlined text-[#3525cd] text-[15px] mt-px flex-shrink-0"
                              style={{ fontVariationSettings: "'FILL' 1" }}
                            >
                              tips_and_updates
                            </span>
                            <span className="text-xs text-[#464555] leading-relaxed">{tip}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </section>

            {/* General Tips + CTAs — mobile only */}
            <div className="lg:hidden space-y-6">
              <GeneralTipsCard />
              <SubmitCTACards />
            </div>
          </div>

          {/* Right Sidebar — desktop only */}
          <div className="hidden lg:block">
            <div className="sticky top-24 space-y-6">
              <InterviewProcessCard />
              <GeneralTipsCard />
              <SubmitCTACards />
            </div>
          </div>
        </div>
      </main>

      {/* ━━━━ Mobile sticky bottom action bar ━━━━ */}
      <div className="lg:hidden fixed bottom-0 left-0 w-full z-50 bg-[#f9f9f9]/95 backdrop-blur-md border-t border-slate-200/20 shadow-[0_-10px_30px_rgba(0,0,0,0.04)] px-4 py-3 flex items-center gap-2">
        <button className="flex-1 bg-[#3525cd] hover:bg-[#4f46e5] text-white font-bold py-2.5 rounded-xl text-xs transition-colors active:scale-[0.98] flex items-center justify-center gap-1.5">
          <span className="material-symbols-outlined text-[16px]">quiz</span>
          Submit Question
        </button>
        <button className="flex-1 bg-white border border-[#3525cd]/30 text-[#3525cd] font-bold py-2.5 rounded-xl text-xs transition-colors active:scale-[0.98] flex items-center justify-center gap-1.5">
          <span className="material-symbols-outlined text-[16px]">rate_review</span>
          Your Experience
        </button>
        <a
          href={waUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-shrink-0 w-11 h-10 flex items-center justify-center bg-[#25d366] rounded-xl active:scale-[0.98] transition-transform"
          aria-label="Share on WhatsApp"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
            <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347z"/>
            <path d="M12 0C5.373 0 0 5.373 0 12c0 2.123.555 4.116 1.524 5.847L.057 23.882a.5.5 0 0 0 .606.608l6.162-1.453A11.938 11.938 0 0 0 12 24c6.627 0 12-5.373 12-12S18.627 0 12 0zm0 22c-1.878 0-3.636-.495-5.147-1.359l-.364-.214-3.773.89.928-3.668-.235-.378A9.972 9.972 0 0 1 2 12C2 6.477 6.477 2 12 2s10 4.477 10 10-4.477 10-10 10z"/>
          </svg>
        </a>
      </div>

    </div>
  );
}
