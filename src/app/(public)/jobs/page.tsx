"use client";

import { useState } from "react";
import Link from "next/link";

// ── Types ──────────────────────────────────────────────────────────────────────
type Domain   = "All" | "Backend" | "Frontend" | "Full-Stack" | "Mobile" | "DevOps" | "Data" | "AI/ML" | "QA";
type JobType  = "All" | "Internship" | "Full-Time";
type WorkMode = "All" | "Remote" | "Onsite" | "Hybrid";

interface Job {
  id:           number;
  company:      string;
  city:         string;
  role:         string;
  domain:       Exclude<Domain, "All">;
  type:         Exclude<JobType, "All">;
  workMode:     Exclude<WorkMode, "All">;
  deadline:     string;
  deadlineIcon: string;
  icon:         string | null;   // material symbol name, or null if has logo
}

// ── Static data ────────────────────────────────────────────────────────────────
const DOMAINS:    Domain[]   = ["All", "Backend", "Frontend", "Full-Stack", "Mobile", "DevOps", "Data", "AI/ML", "QA"];
const JOB_TYPES:  JobType[]  = ["All", "Internship", "Full-Time"];
const WORK_MODES: WorkMode[] = ["All", "Remote", "Onsite"];

const JOBS: Job[] = [
  { id: 1, company: "CloudScale Solutions", city: "Karachi", role: "Junior Backend Engineer",    domain: "Backend",    type: "Full-Time",  workMode: "Remote",  deadline: "Apply by May 15",  deadlineIcon: "calendar_today", icon: "corporate_fare" },
  { id: 2, company: "DataPulse Labs",        city: "Karachi", role: "Software Intern",            domain: "Full-Stack", type: "Internship", workMode: "Onsite",  deadline: "Rolling deadline", deadlineIcon: "schedule",       icon: "hub"            },
  { id: 3, company: "NeuroFront AI",         city: "Karachi", role: "Frontend Developer (React)", domain: "Frontend",   type: "Full-Time",  workMode: "Hybrid",  deadline: "Apply by May 10",  deadlineIcon: "calendar_today", icon: "token"          },
  { id: 4, company: "SecureLayer",           city: "Karachi", role: "DevOps Internship",          domain: "DevOps",     type: "Internship", workMode: "Remote",  deadline: "Rolling deadline", deadlineIcon: "schedule",       icon: "security"       },
  { id: 5, company: "Arbisoft",              city: "Lahore",  role: "React Native Engineer",      domain: "Mobile",     type: "Full-Time",  workMode: "Onsite",  deadline: "Apply by May 20",  deadlineIcon: "calendar_today", icon: "phone_android"  },
  { id: 6, company: "Systems Ltd",           city: "Karachi", role: "Data Science Intern",        domain: "Data",       type: "Internship", workMode: "Hybrid",  deadline: "Rolling deadline", deadlineIcon: "schedule",       icon: "analytics"      },
];

// ── Badge helpers ──────────────────────────────────────────────────────────────
function DomainBadge({ label }: { label: string }) {
  return (
    <span className="px-3 py-1 rounded-md bg-[#3525cd]/10 text-[#3525cd] text-xs font-bold">{label}</span>
  );
}
function TypeBadge({ label }: { label: string }) {
  const isInternship = label === "Internship";
  return (
    <span className={`px-3 py-1 rounded-md text-xs font-bold ${isInternship ? "bg-[#ffdbcc] text-[#7b2f00]" : "bg-[#ffdbcc] text-[#7b2f00]"}`}>
      {label}
    </span>
  );
}
function WorkModeBadge({ label }: { label: string }) {
  const styles: Record<string, string> = {
    Remote:  "bg-[#b6b4ff]/30 text-[#58579b]",
    Onsite:  "bg-[#e8e8e8] text-[#464555]",
    Hybrid:  "bg-[#b6b4ff]/30 text-[#58579b]",
  };
  return (
    <span className={`px-3 py-1 rounded-md text-xs font-bold ${styles[label] ?? "bg-[#eeeeee] text-[#464555]"}`}>{label}</span>
  );
}

// ── Main component ─────────────────────────────────────────────────────────────
export default function JobsPage() {
  const [activeDomain,   setActiveDomain]   = useState<Domain>("All");
  const [activeType,     setActiveType]     = useState<JobType>("All");
  const [activeWorkMode, setActiveWorkMode] = useState<WorkMode>("All");
  const [search,         setSearch]         = useState("");
  const [saved,          setSaved]          = useState<Set<number>>(new Set([2])); // card 2 pre-saved
  const [currentPage,    setCurrentPage]    = useState(1);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleSave = (id: number) =>
    setSaved((prev) => { const next = new Set(prev); next.has(id) ? next.delete(id) : next.add(id); return next; });

  const filtered = JOBS.filter((j) => {
    const matchDomain   = activeDomain   === "All" || j.domain   === activeDomain;
    const matchType     = activeType     === "All" || j.type     === activeType;
    const matchWorkMode = activeWorkMode === "All" || j.workMode === activeWorkMode;
    const matchSearch   = !search || j.role.toLowerCase().includes(search.toLowerCase()) || j.company.toLowerCase().includes(search.toLowerCase());
    return matchDomain && matchType && matchWorkMode && matchSearch;
  });

  return (
    <div className="bg-[#f9f9f9] min-h-dvh antialiased pb-28 lg:pb-10" style={{ color: "#1a1c1c", fontFamily: "Inter, sans-serif" }}>

      {/* ━━━━ Header ━━━━ */}
      <header className="bg-[#f9f9f9]/90 backdrop-blur-md sticky top-0 z-40">
        <div className="flex justify-between items-center px-6 lg:px-8 py-4 lg:py-5 max-w-7xl mx-auto">

          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 flex-shrink-0">
            <span className="material-symbols-outlined text-[#3525cd] text-3xl">architecture</span>
            <span className="text-xl lg:text-2xl font-bold tracking-tighter text-[#3525cd]">GradHire</span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden md:flex items-center gap-6 font-bold tracking-tight">
            <Link href="/jobs"     className="text-[#3525cd] font-bold">Jobs</Link>
            <Link href="#"         className="text-[#1a1c1c]/70 hover:bg-[#f3f3f3] transition-colors px-3 py-1 rounded-lg">Applied</Link>
            <Link href="#"         className="text-[#1a1c1c]/70 hover:bg-[#f3f3f3] transition-colors px-3 py-1 rounded-lg">Saved</Link>
            <div className="w-9 h-9 rounded-full bg-[#e8e8e8] flex items-center justify-center border-2 border-[#3525cd]/10 overflow-hidden ml-2">
              <span className="material-symbols-outlined text-[#464555] text-lg">person</span>
            </div>
          </nav>

          {/* Mobile hamburger */}
          <button
            className="md:hidden p-2 rounded-full hover:bg-[#f3f3f3] transition-colors"
            onClick={() => setMobileMenuOpen((v) => !v)}
            aria-label="Toggle menu"
          >
            <span className="material-symbols-outlined">{mobileMenuOpen ? "close" : "menu"}</span>
          </button>
        </div>

        {/* Mobile dropdown menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-white border-t border-[#f3f3f3] px-6 py-4 flex flex-col gap-3 shadow-md">
            <Link href="/jobs" onClick={() => setMobileMenuOpen(false)} className="font-bold text-[#3525cd] py-2">Jobs</Link>
            <Link href="#"     onClick={() => setMobileMenuOpen(false)} className="text-[#1a1c1c]/70 py-2">Applied</Link>
            <Link href="#"     onClick={() => setMobileMenuOpen(false)} className="text-[#1a1c1c]/70 py-2">Saved</Link>
          </div>
        )}

        <div className="bg-[#f3f3f3] h-px w-full" />
      </header>

      <main className="max-w-7xl mx-auto px-6 lg:px-8 py-10">

        {/* ━━━━ Hero ━━━━ */}
        <section className="mb-10 lg:mb-12">
          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6">
            <div>
              <span className="text-xs uppercase tracking-widest text-[#3525cd] font-bold mb-2 block">
                Available Opportunities
              </span>
              <h1 className="text-3xl lg:text-5xl font-bold tracking-tight leading-tight">
                Software Jobs &amp; Internships
              </h1>
              <p className="text-[#464555] mt-2 text-base lg:text-lg">
                Showing {filtered.length} active listing{filtered.length !== 1 ? "s" : ""}
              </p>
            </div>

            {/* Search */}
            <div className="w-full lg:w-96 relative">
              <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
                <span className="material-symbols-outlined text-[#777587]">search</span>
              </div>
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search by title or company"
                className="w-full pl-12 pr-4 py-3.5 bg-white rounded-xl ring-1 ring-[#c7c4d8]/30 focus:ring-2 focus:ring-[#3525cd] focus:outline-none shadow-sm transition-all text-sm"
              />
            </div>
          </div>
        </section>

        {/* ━━━━ Filter Bar ━━━━ */}
        <section className="space-y-5 mb-10">

          {/* Domain pills */}
          <div className="flex flex-col gap-2">
            <span className="text-xs font-bold uppercase tracking-widest text-[#464555]/70">Domains</span>
            <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1">
              {DOMAINS.map((d) => (
                <button
                  key={d}
                  onClick={() => setActiveDomain(d)}
                  className={`px-5 py-2 rounded-full font-medium whitespace-nowrap text-sm transition-all ${
                    activeDomain === d
                      ? "bg-[#3525cd] text-white shadow-md shadow-[#3525cd]/20"
                      : "bg-[#f3f3f3] hover:bg-[#e8e8e8] text-[#1a1c1c]"
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          {/* Meta filters */}
          <div className="flex flex-wrap gap-6 lg:gap-10">
            {/* Job Type */}
            <div className="flex flex-col gap-2">
              <span className="text-xs font-bold uppercase tracking-widest text-[#464555]/70">Job Type</span>
              <div className="flex items-center gap-2">
                {JOB_TYPES.map((t) => (
                  <button
                    key={t}
                    onClick={() => setActiveType(t)}
                    className={`px-4 py-1.5 rounded-lg border text-sm font-medium transition-all ${
                      activeType === t
                        ? "border-[#3525cd] bg-white text-[#1a1c1c]"
                        : "border-[#c7c4d8]/30 hover:border-[#3525cd] text-[#1a1c1c]"
                    }`}
                  >
                    {t}
                  </button>
                ))}
              </div>
            </div>

            {/* Location */}
            <div className="flex flex-col gap-2">
              <span className="text-xs font-bold uppercase tracking-widest text-[#464555]/70">Location</span>
              <div className="flex items-center gap-2">
                {WORK_MODES.map((m) => (
                  <button
                    key={m}
                    onClick={() => setActiveWorkMode(m)}
                    className={`px-4 py-1.5 rounded-lg border text-sm font-medium transition-all ${
                      activeWorkMode === m
                        ? "border-[#3525cd] bg-white text-[#1a1c1c]"
                        : "border-[#c7c4d8]/30 hover:border-[#3525cd] text-[#1a1c1c]"
                    }`}
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ━━━━ Job Card Grid ━━━━ */}
        {filtered.length === 0 ? (
          <div className="text-center py-24 text-[#464555]">
            <span className="material-symbols-outlined text-5xl text-[#c7c4d8] block mb-4">search_off</span>
            <p className="font-semibold text-lg">No jobs match your filters</p>
            <p className="text-sm mt-1">Try adjusting the domain, type, or search query.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 lg:gap-8">
            {filtered.map((job) => (
              <article
                key={job.id}
                className="group relative flex flex-col bg-white rounded-xl p-6 border border-[#c7c4d8]/10 transition-all duration-300 hover:shadow-[0_20px_40px_rgba(26,28,28,0.08)] hover:-translate-y-1"
              >
                {/* Save button */}
                <button
                  onClick={() => toggleSave(job.id)}
                  className="absolute top-5 right-5 transition-colors"
                  aria-label={saved.has(job.id) ? "Unsave job" : "Save job"}
                >
                  <span
                    className={`material-symbols-outlined transition-colors ${saved.has(job.id) ? "text-[#ba1a1a]" : "text-[#777587] hover:text-[#ba1a1a]"}`}
                    style={saved.has(job.id) ? { fontVariationSettings: "'FILL' 1" } : undefined}
                  >
                    favorite
                  </span>
                </button>

                {/* Company row */}
                <div className="flex items-center gap-3 mb-5">
                  <div className="w-11 h-11 rounded-full bg-[#eeeeee] flex items-center justify-center flex-shrink-0">
                    <span className="material-symbols-outlined text-[#464555] text-xl">{job.icon ?? "business"}</span>
                  </div>
                  <div>
                    <p className="font-bold text-[#1a1c1c] text-sm leading-tight">{job.company}</p>
                    <p className="text-xs text-[#464555]">{job.city}</p>
                  </div>
                </div>

                {/* Role */}
                <h3 className="text-lg font-bold text-[#1a1c1c] group-hover:text-[#3525cd] transition-colors mb-4 leading-tight pr-6">
                  {job.role}
                </h3>

                {/* Badges */}
                <div className="flex flex-wrap gap-2 mb-5">
                  <DomainBadge   label={job.domain}   />
                  <TypeBadge     label={job.type}     />
                  <WorkModeBadge label={job.workMode} />
                </div>

                {/* Footer */}
                <div className="mt-auto pt-4 border-t border-[#eeeeee] flex items-center justify-between">
                  <div className="flex items-center gap-1.5 text-[#464555] text-xs">
                    <span className="material-symbols-outlined text-sm">{job.deadlineIcon}</span>
                    <span>{job.deadline}</span>
                  </div>
                  <Link href={`/jobs/${job.id}`} className="text-[#3525cd] font-bold text-sm hover:underline underline-offset-4">
                    View Details
                  </Link>
                </div>
              </article>
            ))}
          </div>
        )}

        {/* ━━━━ Pagination ━━━━ */}
        <div className="mt-14 flex justify-center items-center gap-2">
          <button
            onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
            className="flex items-center justify-center w-10 h-10 rounded-lg hover:bg-[#e8e8e8] transition-colors"
            aria-label="Previous page"
          >
            <span className="material-symbols-outlined">chevron_left</span>
          </button>
          {[1, 2, 3].map((p) => (
            <button
              key={p}
              onClick={() => setCurrentPage(p)}
              className={`w-10 h-10 rounded-lg font-bold text-sm transition-colors ${
                currentPage === p
                  ? "bg-[#3525cd] text-white shadow-sm"
                  : "hover:bg-[#e8e8e8] text-[#1a1c1c] font-medium"
              }`}
            >
              {p}
            </button>
          ))}
          <button
            onClick={() => setCurrentPage((p) => Math.min(3, p + 1))}
            className="flex items-center justify-center w-10 h-10 rounded-lg hover:bg-[#e8e8e8] transition-colors"
            aria-label="Next page"
          >
            <span className="material-symbols-outlined">chevron_right</span>
          </button>
        </div>

      </main>

      {/* ━━━━ Bottom Nav — mobile only ━━━━ */}
      <nav className="md:hidden fixed bottom-0 left-0 w-full z-50 flex justify-around items-center px-6 pb-8 pt-4 bg-[#f9f9f9]/90 backdrop-blur-md border-t border-[#f3f3f3] shadow-[0_-10px_30px_rgba(26,28,28,0.04)] rounded-t-3xl">
        <Link href="/jobs" className="flex flex-col items-center bg-[#4f46e5] text-white rounded-2xl p-3 scale-110">
          <span className="material-symbols-outlined">work</span>
          <span className="text-[11px] font-bold uppercase tracking-widest mt-1">Jobs</span>
        </Link>
        <Link href="#" className="flex flex-col items-center text-[#1a1c1c]/60 hover:text-[#3525cd] p-2 transition-all">
          <span className="material-symbols-outlined">assignment_turned_in</span>
          <span className="text-[11px] font-bold uppercase tracking-widest mt-1">Applied</span>
        </Link>
        <Link href="#" className="flex flex-col items-center text-[#1a1c1c]/60 hover:text-[#3525cd] p-2 transition-all">
          <span className="material-symbols-outlined">bookmark</span>
          <span className="text-[11px] font-bold uppercase tracking-widest mt-1">Saved</span>
        </Link>
        <Link href="#" className="flex flex-col items-center text-[#1a1c1c]/60 hover:text-[#3525cd] p-2 transition-all">
          <span className="material-symbols-outlined">person</span>
          <span className="text-[11px] font-bold uppercase tracking-widest mt-1">Profile</span>
        </Link>
      </nav>

    </div>
  );
}
