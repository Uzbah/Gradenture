"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

// ── Static job data (replace with API call when backend is ready) ──────────────
const JOB = {
  id:          "1",
  company:     "CloudScale Solutions",
  city:        "Karachi",
  role:        "Junior Backend Engineer",
  domain:      "Backend",
  type:        "Internship",
  workMode:    "Remote",
  posted:      "3 days ago",
  deadline:    "May 20, 2026",
  salary:      "PKR 40,000–60,000",
  email:       "careers@cloudscale.com",
  companyIcon: "corporate_fare",
  about: [
    "CloudScale Solutions is seeking an ambitious Junior Backend Engineer to join our core engineering team. You will play a vital role in building and optimizing high-scale systems that power digital transformation for our global clients.",
    <>In this role, you will work primarily with <strong>Python</strong> and <strong>Django</strong>, contributing to server-side logic and architectural decisions under the mentorship of senior architects.</>,
  ],
  requirements: [
    "Proficiency in Python and Django framework",
    "Understanding of relational databases like PostgreSQL",
    "Version control with Git",
    "Basic familiarity with AWS cloud services",
    "Strong problem-solving and analytical skills",
  ],
};

// ── Badge helpers ──────────────────────────────────────────────────────────────
function Badge({ label, variant }: { label: string; variant: "domain" | "type" | "mode" }) {
  const styles = {
    domain: "bg-[#3525cd]/10 text-[#3525cd]",
    type:   "bg-[#ffdbcc] text-[#7b2f00]",
    mode:   "bg-teal-100 text-teal-800",
  };
  return (
    <span className={`px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${styles[variant]}`}>
      {label}
    </span>
  );
}

// ── WhatsApp icon ──────────────────────────────────────────────────────────────
function WhatsAppIcon() {
  return (
    <svg className="w-5 h-5 fill-current flex-shrink-0" viewBox="0 0 24 24">
      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z" />
    </svg>
  );
}

// ── Action buttons (shared between header card + sidebar) ─────────────────────
function ApplyActions() {
  const shareText = `Check out this job: ${JOB.role} at ${JOB.company} — via KHI Tech Prep`;
  const waUrl = `https://wa.me/?text=${encodeURIComponent(shareText)}`;
  return (
    <div className="space-y-3">
      <button className="w-full py-4 bg-[#3525cd] hover:bg-[#2a1eb5] text-white font-bold rounded-xl active:scale-95 transition-all duration-200 text-sm">
        Apply Now
      </button>
      <a
        href={waUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="w-full py-4 bg-[#25D366] hover:bg-[#1fba59] text-white font-bold rounded-xl flex items-center justify-center gap-2 active:scale-95 transition-all duration-200 text-sm"
      >
        <WhatsAppIcon />
        Share on WhatsApp
      </a>
    </div>
  );
}

// ── Page ───────────────────────────────────────────────────────────────────────
export default function JobDetailPage() {
  const router  = useRouter();
  const [saved, setSaved] = useState(true); // pre-saved to show filled heart

  return (
    <div className="bg-[#f9f9f9] min-h-dvh pb-28 lg:pb-12" style={{ color: "#1a1c1c", fontFamily: "Inter, sans-serif" }}>

      {/* ━━━━ Header ━━━━ */}
      <header className="sticky top-0 z-50 bg-[#f9f9f9]/90 backdrop-blur-md">
        <div className="flex justify-between items-center px-6 lg:px-8 py-4 max-w-7xl mx-auto">
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.back()}
              className="p-1.5 rounded-full hover:bg-[#eeeeee] transition-colors"
              aria-label="Go back"
            >
              <span className="material-symbols-outlined text-[#464555]">arrow_back</span>
            </button>
            <Link href="/" className="font-bold tracking-tighter text-xl text-[#3525cd]">KHI Tech Prep</Link>
          </div>
          <div className="w-8 h-8 rounded-full bg-[#e8e8e8] flex items-center justify-center overflow-hidden">
            <span className="material-symbols-outlined text-[#464555] text-lg">person</span>
          </div>
        </div>
        <div className="bg-[#f3f3f3] h-px w-full" />
      </header>

      <main className="max-w-7xl mx-auto px-4 lg:px-8 pt-8 pb-4">

        {/* ━━━━ Desktop: 2-col grid / Mobile: single col ━━━━ */}
        <div className="lg:grid lg:grid-cols-3 lg:gap-10 lg:items-start">

          {/* ── Left column ────────────────────────────────────────── */}
          <div className="lg:col-span-2 space-y-5">

            {/* Job Header Card */}
            <section className="bg-white rounded-2xl p-6 lg:p-8 relative border border-[#c7c4d8]/10 shadow-sm">
              {/* Save toggle */}
              <button
                onClick={() => setSaved((v) => !v)}
                className="absolute top-6 right-6 transition-colors"
                aria-label={saved ? "Unsave job" : "Save job"}
              >
                <span
                  className={`material-symbols-outlined text-2xl transition-colors ${saved ? "text-[#ba1a1a]" : "text-[#777587] hover:text-[#ba1a1a]"}`}
                  style={saved ? { fontVariationSettings: "'FILL' 1" } : undefined}
                >
                  favorite
                </span>
              </button>

              {/* Company + Title */}
              <div className="flex items-center gap-4 mb-6 pr-8">
                <div className="w-16 h-16 rounded-2xl bg-[#eeeeee] flex items-center justify-center flex-shrink-0">
                  <span className="material-symbols-outlined text-[#464555] text-3xl">{JOB.companyIcon}</span>
                </div>
                <div>
                  <p className="text-[#464555] font-medium text-sm">{JOB.company}</p>
                  <h2 className="text-2xl lg:text-3xl font-bold tracking-tight">{JOB.role}</h2>
                </div>
              </div>

              {/* Badges */}
              <div className="flex flex-wrap gap-2 mb-6">
                <Badge label={JOB.domain}   variant="domain" />
                <Badge label={JOB.type}     variant="type"   />
                <Badge label={JOB.workMode} variant="mode"   />
              </div>

              {/* Meta */}
              <div className="space-y-2.5 mb-8">
                <div className="flex items-center gap-2 text-[#464555] text-sm">
                  <span className="material-symbols-outlined text-sm">location_on</span>
                  <span>{JOB.city}</span>
                </div>
                <div className="flex items-center gap-2 text-[#464555] text-sm">
                  <span className="material-symbols-outlined text-sm">schedule</span>
                  <span>Posted {JOB.posted}</span>
                </div>
                <div className="flex items-center gap-2 text-[#ba1a1a] text-sm font-medium">
                  <span className="material-symbols-outlined text-sm">event</span>
                  <span>Apply by {JOB.deadline}</span>
                </div>
              </div>

              {/* Action buttons — mobile only (desktop shows in sidebar) */}
              <div className="lg:hidden">
                <ApplyActions />
              </div>
            </section>

            {/* About the Role */}
            <section className="bg-white rounded-2xl p-6 lg:p-8 border border-[#c7c4d8]/10 shadow-sm">
              <h3 className="text-lg lg:text-xl font-bold mb-4">About the Role</h3>
              <div className="text-[#464555] leading-relaxed text-sm space-y-4">
                {JOB.about.map((para, i) => (
                  <p key={i}>{para}</p>
                ))}
              </div>
            </section>

            {/* Requirements */}
            <section className="bg-white rounded-2xl p-6 lg:p-8 border border-[#c7c4d8]/10 shadow-sm">
              <h3 className="text-lg lg:text-xl font-bold mb-4">Requirements</h3>
              <ul className="space-y-3">
                {JOB.requirements.map((req) => (
                  <li key={req} className="flex items-start gap-3 text-sm text-[#464555]">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#3525cd] mt-1.5 flex-shrink-0" />
                    <span>{req}</span>
                  </li>
                ))}
              </ul>
            </section>

            {/* Interview Prep Banner */}
            <section className="border-2 border-[#3525cd]/20 bg-[#3525cd]/5 rounded-2xl p-5 lg:p-6">
              <div className="flex items-start gap-4">
                <span className="material-symbols-outlined text-[#3525cd] text-3xl flex-shrink-0 mt-0.5">lightbulb</span>
                <div className="space-y-3">
                  <p className="text-sm font-medium leading-snug">
                    Preparing for an interview at {JOB.company}? We have real questions and experiences from candidates.
                  </p>
                  <button className="text-[#3525cd] font-bold text-sm flex items-center gap-1 hover:underline underline-offset-4">
                    View Interview Prep Profile →
                  </button>
                </div>
              </div>
            </section>

          </div>{/* end left col */}

          {/* ── Right column — sticky sidebar (desktop only) ────────── */}
          <aside className="hidden lg:flex flex-col gap-5 sticky top-24">

            {/* Apply actions */}
            <div className="bg-white rounded-2xl p-6 border border-[#c7c4d8]/10 shadow-sm">
              <h3 className="font-bold text-base mb-4">Ready to apply?</h3>
              <ApplyActions />
            </div>

            {/* Salary */}
            <div className="bg-white rounded-2xl p-6 border border-[#c7c4d8]/10 shadow-sm flex items-center justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-widest text-[#464555]/70 mb-1">Salary</p>
                <p className="text-[#3525cd] font-bold text-lg">{JOB.salary}</p>
                <p className="text-xs text-[#464555]">per month</p>
              </div>
              <span className="material-symbols-outlined text-[#3525cd] text-3xl">payments</span>
            </div>

            {/* How to Apply */}
            <div className="bg-white rounded-2xl p-6 border border-[#c7c4d8]/10 shadow-sm space-y-4">
              <h3 className="font-bold text-base">How to Apply</h3>
              <p className="text-sm text-[#464555]">
                Send your CV and portfolio directly to our recruitment team or use the quick apply button above.
              </p>
              <div className="p-3 bg-[#f3f3f3] rounded-xl flex items-center gap-3">
                <span className="material-symbols-outlined text-[#3525cd]">mail</span>
                <span className="text-sm font-medium">{JOB.email}</span>
              </div>
            </div>

          </aside>

        </div>{/* end grid */}

        {/* Salary + How to Apply — mobile only, below content ─────── */}
        <div className="lg:hidden space-y-5 mt-5">

          {/* Salary */}
          <section className="bg-white rounded-2xl p-5 border border-[#c7c4d8]/10 shadow-sm flex items-center justify-between">
            <h3 className="text-base font-bold">Salary</h3>
            <p className="text-[#3525cd] font-bold text-base">
              {JOB.salary}<span className="text-xs font-normal text-[#464555]">/mo</span>
            </p>
          </section>

          {/* How to Apply */}
          <section className="bg-white rounded-2xl p-5 border border-[#c7c4d8]/10 shadow-sm space-y-4">
            <h3 className="text-base font-bold">How to Apply</h3>
            <p className="text-sm text-[#464555]">
              Send your CV and portfolio to our recruitment team or use the quick apply button above.
            </p>
            <div className="p-3 bg-[#f3f3f3] rounded-xl flex items-center gap-3">
              <span className="material-symbols-outlined text-[#3525cd]">mail</span>
              <span className="text-sm font-medium">{JOB.email}</span>
            </div>
            <button className="w-full py-3 bg-[#3525cd] hover:bg-[#2a1eb5] text-white font-bold rounded-xl active:scale-95 transition-all text-sm">
              Apply Now
            </button>
          </section>

        </div>

      </main>

      {/* ━━━━ Bottom Nav — mobile only ━━━━ */}
      <nav className="lg:hidden fixed bottom-0 left-0 w-full z-50 bg-[#f9f9f9]/90 backdrop-blur-md border-t border-slate-200/20 shadow-[0_-4px_20px_rgba(26,28,28,0.06)] flex justify-around items-center px-4 pb-6 pt-3">
        <Link href="/jobs" className="flex flex-col items-center text-[#3525cd] bg-[#4f46e5]/10 rounded-xl px-3 py-1 transition-all">
          <span className="material-symbols-outlined">work</span>
          <span className="text-[11px] font-medium tracking-wide uppercase mt-1">Jobs</span>
        </Link>
        <Link href="#" className="flex flex-col items-center text-slate-500 hover:text-[#3525cd] transition-all">
          <span className="material-symbols-outlined">menu_book</span>
          <span className="text-[11px] font-medium tracking-wide uppercase mt-1">Prep</span>
        </Link>
        <Link href="#" className="flex flex-col items-center text-slate-500 hover:text-[#3525cd] transition-all">
          <span className="material-symbols-outlined">bookmark</span>
          <span className="text-[11px] font-medium tracking-wide uppercase mt-1">Saved</span>
        </Link>
        <Link href="#" className="flex flex-col items-center text-slate-500 hover:text-[#3525cd] transition-all">
          <span className="material-symbols-outlined">person</span>
          <span className="text-[11px] font-medium tracking-wide uppercase mt-1">Profile</span>
        </Link>
      </nav>

    </div>
  );
}
