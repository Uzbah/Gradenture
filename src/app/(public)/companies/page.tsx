"use client";

import { useState, useMemo } from "react";
import Link from "next/link";

// ── Types ──────────────────────────────────────────────────────────────────────
type Domain     = "All Domains" | "Backend" | "Frontend" | "Full-Stack" | "Mobile" | "DevOps" | "AI/ML";
type Difficulty = "All" | "Easy" | "Medium" | "Hard";

interface Company {
  id:          string;
  name:        string;
  sector:      string;
  city:        string;
  difficulty:  Exclude<Difficulty, "All">;
  domains:     string[];
  tags:        string[];
  questions:   number;
  experiences: number;
  icon:        string; // material symbol
}

// ── Static data ────────────────────────────────────────────────────────────────
const COMPANIES: Company[] = [
  {
    id: "cloudscale",
    name: "CloudScale Solutions", sector: "SaaS",            city: "Karachi, PK",
    difficulty: "Medium",
    domains: ["Backend", "Cloud", "Docker"],
    tags: ["Asks DSA", "Take-home project"],
    questions: 24, experiences: 8,
    icon: "cloud",
  },
  {
    id: "datapulse",
    name: "DataPulse Labs",       sector: "Data Analytics",  city: "Karachi, PK",
    difficulty: "Hard",
    domains: ["Data Engineering", "Python"],
    tags: ["Asks SQL", "Math Heavy"],
    questions: 18, experiences: 5,
    icon: "analytics",
  },
  {
    id: "swiftpay",
    name: "SwiftPay",             sector: "Fintech",          city: "Karachi, PK",
    difficulty: "Easy",
    domains: ["Frontend", "Mobile", "React Native"],
    tags: ["Behavioral Focus", "Speed Code"],
    questions: 32, experiences: 12,
    icon: "payments",
  },
  {
    id: "retailflow",
    name: "RetailFlow",           sector: "E-Commerce",       city: "Karachi, PK",
    difficulty: "Medium",
    domains: ["Full-Stack", "Node.js"],
    tags: ["Asks DSA", "System Design"],
    questions: 12, experiences: 3,
    icon: "local_shipping",
  },
  {
    id: "neurofront",
    name: "NeuroFront AI",        sector: "AI/ML",            city: "Karachi, PK",
    difficulty: "Hard",
    domains: ["AI/ML", "Python", "Backend"],
    tags: ["Research Questions", "Math Heavy"],
    questions: 20, experiences: 6,
    icon: "psychology",
  },
  {
    id: "securelayer",
    name: "SecureLayer",          sector: "Cybersecurity",    city: "Karachi, PK",
    difficulty: "Medium",
    domains: ["DevOps", "Backend"],
    tags: ["System Design", "Scenario-based"],
    questions: 15, experiences: 4,
    icon: "security",
  },
];

const DOMAINS:      Domain[]     = ["All Domains", "Backend", "Frontend", "Full-Stack", "Mobile", "DevOps", "AI/ML"];
const DIFFICULTIES: Difficulty[] = ["All", "Easy", "Medium", "Hard"];

// ── Difficulty badge ───────────────────────────────────────────────────────────
const DIFF_STYLES: Record<string, string> = {
  Easy:   "bg-green-50 text-green-700",
  Medium: "bg-amber-50 text-amber-700",
  Hard:   "bg-red-50 text-red-700",
};

function DifficultyBadge({ label }: { label: string }) {
  return (
    <span className={`px-3 py-1 rounded-full text-[10px] font-bold tracking-widest uppercase ${DIFF_STYLES[label] ?? "bg-slate-100 text-slate-600"}`}>
      {label}
    </span>
  );
}

// ── Company Card ───────────────────────────────────────────────────────────────
function CompanyCard({ c }: { c: Company }) {
  return (
    <div className="bg-white p-6 rounded-2xl shadow-[0_10px_30px_rgba(0,0,0,0.03)] hover:shadow-[0_20px_40px_rgba(26,28,28,0.07)] hover:-translate-y-0.5 transition-all flex flex-col gap-4 border border-transparent hover:border-[#3525cd]/5">

      {/* Header row */}
      <div className="flex justify-between items-start gap-2">
        <div className="flex gap-3 min-w-0">
          <div className="w-12 h-12 bg-[#f3f3f3] rounded-xl flex items-center justify-center flex-shrink-0">
            <span className="material-symbols-outlined text-[#3525cd] text-2xl">{c.icon}</span>
          </div>
          <div className="min-w-0">
            <h3 className="font-bold text-lg lg:text-xl tracking-tight truncate">{c.name}</h3>
            <span className="text-xs text-[#464555] font-medium">{c.sector} · {c.city}</span>
          </div>
        </div>
        <DifficultyBadge label={c.difficulty} />
      </div>

      {/* Domain chips */}
      <div className="flex flex-wrap gap-2">
        {c.domains.map((d) => (
          <span key={d} className="px-3 py-1 rounded-md bg-[#e2dfff] text-[#3323cc] text-[11px] font-bold">{d}</span>
        ))}
      </div>

      {/* Stats */}
      <div className="flex gap-5 text-[#464555]">
        <div className="flex items-center gap-1.5">
          <span className="material-symbols-outlined text-sm">book</span>
          <span className="text-sm font-medium">{c.questions} Questions</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="material-symbols-outlined text-sm">person</span>
          <span className="text-sm font-medium">{c.experiences} Experiences</span>
        </div>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-1.5">
        {c.tags.map((t) => (
          <span key={t} className="px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider text-[#777587] border border-[#c7c4d8]/30 rounded">
            {t}
          </span>
        ))}
      </div>

      {/* CTA */}
      <div className="pt-1">
        <Link
          href={`/companies/${c.id}`}
          className="text-[#3525cd] font-bold text-sm inline-flex items-center gap-1 group hover:underline underline-offset-4"
        >
          View Prep Profile
          <span className="material-symbols-outlined text-base group-hover:translate-x-1 transition-transform">arrow_forward</span>
        </Link>
      </div>
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────
export default function CompaniesPage() {
  const [activeDomain,     setActiveDomain]     = useState<Domain>("All Domains");
  const [activeDifficulty, setActiveDifficulty] = useState<Difficulty>("All");
  const [search,           setSearch]           = useState("");
  const [mobileMenuOpen,   setMobileMenuOpen]   = useState(false);

  const filtered = useMemo(() => COMPANIES.filter((c) => {
    const matchDomain = activeDomain === "All Domains" ||
      c.domains.some((d) => d.toLowerCase().includes(activeDomain.toLowerCase()));
    const matchDiff   = activeDifficulty === "All" || c.difficulty === activeDifficulty;
    const matchSearch = !search ||
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.sector.toLowerCase().includes(search.toLowerCase());
    return matchDomain && matchDiff && matchSearch;
  }), [activeDomain, activeDifficulty, search]);

  return (
    <div className="bg-[#f9f9f9] min-h-dvh pb-28 lg:pb-12" style={{ color: "#1a1c1c", fontFamily: "Inter, sans-serif" }}>

      {/* ━━━━ Header ━━━━ */}
      <header className="sticky top-0 z-50 bg-[#f9f9f9]/90 backdrop-blur-md shadow-sm">
        <div className="flex justify-between items-center px-6 lg:px-8 py-4 max-w-7xl mx-auto">

          {/* Logo */}
          <Link href="/" className="flex items-center gap-2.5">
            <span className="material-symbols-outlined text-[#3525cd] text-2xl">grid_view</span>
            <span className="text-xl font-bold tracking-tighter text-[#3525cd]">KHI Tech Prep</span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-1 font-bold">
            <Link href="/jobs"      className="px-4 py-2 rounded-lg text-[#1a1c1c]/70 hover:bg-[#f3f3f3] transition-colors text-sm">Jobs</Link>
            <Link href="/companies" className="px-4 py-2 rounded-lg text-[#3525cd] text-sm">Companies</Link>
            <Link href="#"          className="px-4 py-2 rounded-lg text-[#1a1c1c]/70 hover:bg-[#f3f3f3] transition-colors text-sm">Saved</Link>
          </nav>

          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-[#e8e8e8] ring-2 ring-[#e2dfff] flex items-center justify-center overflow-hidden cursor-pointer hover:opacity-75 transition-opacity">
              <span className="material-symbols-outlined text-[#464555] text-lg">person</span>
            </div>
            {/* Mobile hamburger */}
            <button
              className="md:hidden p-1.5 rounded-full hover:bg-[#f3f3f3] transition-colors"
              onClick={() => setMobileMenuOpen((v) => !v)}
              aria-label="Toggle menu"
            >
              <span className="material-symbols-outlined">{mobileMenuOpen ? "close" : "menu"}</span>
            </button>
          </div>
        </div>

        {/* Mobile dropdown */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-[#f3f3f3] px-6 py-4 flex flex-col gap-3 shadow-md">
            <Link href="/jobs"      onClick={() => setMobileMenuOpen(false)} className="text-[#1a1c1c]/70 py-2 font-medium">Jobs</Link>
            <Link href="/companies" onClick={() => setMobileMenuOpen(false)} className="text-[#3525cd] font-bold py-2">Companies</Link>
            <Link href="#"          onClick={() => setMobileMenuOpen(false)} className="text-[#1a1c1c]/70 py-2 font-medium">Saved</Link>
          </div>
        )}
      </header>

      <main className="max-w-7xl mx-auto px-6 lg:px-8 pt-8 space-y-8 pb-4">

        {/* ━━━━ Hero ━━━━ */}
        <section className="space-y-6">
          <div className="flex flex-col lg:flex-row lg:items-end lg:justify-between gap-6">
            <div className="space-y-1">
              <h2 className="text-3xl lg:text-4xl font-bold tracking-tight">Interview Prep by Company</h2>
              <p className="text-[#464555] font-medium">
                {filtered.length} compan{filtered.length !== 1 ? "ies" : "y"} with prep profiles.
              </p>
            </div>

            {/* Search */}
            <div className="relative w-full lg:w-80">
              <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                <span className="material-symbols-outlined text-[#777587]">search</span>
              </div>
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search company name"
                className="w-full pl-12 pr-4 py-3.5 bg-white rounded-xl ring-1 ring-[#c7c4d8]/30 focus:ring-2 focus:ring-[#3525cd] focus:outline-none shadow-sm transition-all text-sm"
              />
            </div>
          </div>

          {/* Domain filters */}
          <div className="flex flex-col gap-3">
            <span className="text-[10px] font-bold uppercase tracking-[0.15em] text-[#777587]">Domains</span>
            <div className="flex gap-2 overflow-x-auto no-scrollbar pb-1 lg:flex-wrap lg:overflow-visible">
              {DOMAINS.map((d) => (
                <button
                  key={d}
                  onClick={() => setActiveDomain(d)}
                  className={`px-5 py-2 rounded-full font-semibold text-sm whitespace-nowrap transition-all active:scale-95 ${
                    activeDomain === d
                      ? "bg-[#3525cd] text-white shadow-md"
                      : "bg-[#f3f3f3] text-[#464555] hover:bg-[#e8e8e8]"
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {/* Difficulty filters */}
          <div className="flex flex-col gap-3">
            <span className="text-[10px] font-bold uppercase tracking-[0.15em] text-[#777587]">Interview Difficulty</span>
            <div className="flex flex-wrap gap-2">
              {DIFFICULTIES.map((d) => (
                <button
                  key={d}
                  onClick={() => setActiveDifficulty(d)}
                  className={`px-4 py-1.5 rounded-lg font-bold text-xs transition-all ${
                    activeDifficulty === d
                      ? "bg-[#e2e2e2] text-[#1a1c1c]"
                      : "bg-[#f3f3f3] text-[#464555] hover:bg-[#e8e8e8]"
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* ━━━━ Company Card Grid ━━━━ */}
        {filtered.length === 0 ? (
          <div className="text-center py-24 text-[#464555]">
            <span className="material-symbols-outlined text-5xl text-[#c7c4d8] block mb-4">search_off</span>
            <p className="font-semibold text-lg">No companies match your filters</p>
            <p className="text-sm mt-1">Try adjusting the domain, difficulty, or search query.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 lg:gap-8 pb-8">
            {filtered.map((c) => <CompanyCard key={c.id} c={c} />)}
          </div>
        )}

      </main>

      {/* ━━━━ Bottom Nav — mobile only ━━━━ */}
      <nav className="md:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-4 pb-6 pt-3 bg-[#f9f9f9]/90 backdrop-blur-md rounded-t-2xl shadow-[0_-10px_30px_rgba(0,0,0,0.04)] border-t border-slate-200/20">
        <Link href="/jobs"      className="flex flex-col items-center text-slate-400 hover:text-[#3525cd] p-2 active:scale-95 transition-all">
          <span className="material-symbols-outlined">work</span>
          <span className="text-[10px] font-bold uppercase tracking-widest mt-1">Jobs</span>
        </Link>
        <Link href="/companies" className="flex flex-col items-center bg-[#4f46e5] text-white rounded-2xl p-2 px-4 shadow-lg active:scale-95 transition-all">
          <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>apartment</span>
          <span className="text-[10px] font-bold uppercase tracking-widest mt-1">Prep</span>
        </Link>
        <Link href="#"          className="flex flex-col items-center text-slate-400 hover:text-[#3525cd] p-2 active:scale-95 transition-all">
          <span className="material-symbols-outlined">bookmark</span>
          <span className="text-[10px] font-bold uppercase tracking-widest mt-1">Saved</span>
        </Link>
        <Link href="#"          className="flex flex-col items-center text-slate-400 hover:text-[#3525cd] p-2 active:scale-95 transition-all">
          <span className="material-symbols-outlined">person</span>
          <span className="text-[10px] font-bold uppercase tracking-widest mt-1">Profile</span>
        </Link>
      </nav>

    </div>
  );
}
