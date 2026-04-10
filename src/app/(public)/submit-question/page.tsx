"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

// ── Types ──────────────────────────────────────────────────────────────────────
type Domain     = "Backend" | "Frontend" | "Full-Stack" | "Mobile" | "DevOps" | "Data" | "AI/ML" | "QA";
type QuestionType = "DSA" | "OOP" | "System Design" | "SQL" | "Behavioral" | "Take-home" | "HR" | "Other";
type Difficulty = "Easy" | "Medium" | "Hard";

const DOMAINS: Domain[] = ["Backend", "Frontend", "Full-Stack", "Mobile", "DevOps", "Data", "AI/ML", "QA"];
const QUESTION_TYPES: QuestionType[] = ["DSA", "OOP", "System Design", "SQL", "Behavioral", "Take-home", "HR", "Other"];
const DIFFICULTIES: { label: Difficulty; color: string; border: string; bg: string }[] = [
  { label: "Easy",   color: "text-green-700", border: "border-green-500/30", bg: "bg-green-50"  },
  { label: "Medium", color: "text-amber-700", border: "border-amber-500/30", bg: "bg-amber-50"  },
  { label: "Hard",   color: "text-red-700",   border: "border-red-500/30",   bg: "bg-red-50"    },
];

const MAX_QUESTION = 500;
const MAX_HINT     = 300;

// ── Page ───────────────────────────────────────────────────────────────────────
export default function SubmitQuestionPage() {
  const router = useRouter();

  const [questionText,   setQuestionText]   = useState("");
  const [domain,         setDomain]         = useState<Domain>("Backend");
  const [questionType,   setQuestionType]   = useState<QuestionType>("DSA");
  const [difficulty,     setDifficulty]     = useState<Difficulty>("Medium");
  const [round,          setRound]          = useState("");
  const [year,           setYear]           = useState("");
  const [answerHint,     setAnswerHint]     = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    // TODO: wire up to API
    alert("Question submitted for review!");
  }

  return (
    <div
      className="bg-[#f9f9f9] min-h-dvh pb-40 sm:pb-28"
      style={{ color: "#1a1c1c", fontFamily: "Inter, sans-serif" }}
    >

      {/* ━━━━ Header ━━━━ */}
      <header className="sticky top-0 z-40 bg-[#f9f9f9]/90 backdrop-blur-md shadow-sm">
        <div className="flex justify-between items-center px-6 py-4 max-w-3xl mx-auto w-full">
          <div className="flex items-center gap-3">
            <button
              onClick={() => router.back()}
              className="hover:bg-[#f3f3f3] transition-colors p-2 rounded-full active:translate-y-0.5"
              aria-label="Go back"
            >
              <span className="material-symbols-outlined text-[#1a1c1c]">arrow_back</span>
            </button>
            <h1 className="font-bold text-xl sm:text-2xl tracking-tight">Submit Interview Question</h1>
          </div>

          <div className="flex items-center gap-3">
            <div className="text-right hidden sm:block">
              <p className="text-xs font-bold text-[#3525cd] tracking-tight uppercase">Karachi Chapter</p>
              <p className="text-[10px] text-[#464555] font-medium">Systems Limited Portal</p>
            </div>
            <div className="w-10 h-10 rounded-full bg-[#e2dfff] flex items-center justify-center border-2 border-white shadow-sm flex-shrink-0">
              <span className="material-symbols-outlined text-[#3525cd] text-xl">apartment</span>
            </div>
          </div>
        </div>
        <div className="h-px w-full bg-[#f3f3f3]" />
      </header>

      <main className="max-w-3xl mx-auto px-6 pt-10 space-y-12">

        {/* ━━━━ Context Header ━━━━ */}
        <section className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#3525cd]/5 text-[#3525cd] text-xs font-bold tracking-widest uppercase">
            <span className="material-symbols-outlined text-sm">apartment</span>
            Company Context
          </div>
          <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-[#1a1c1c]">For: Systems Limited</h2>
          <p className="text-[#464555] max-w-xl leading-relaxed text-sm sm:text-base">
            Help fellow CS students in Karachi by contributing real interview questions from Systems Limited.
            Your insights build the local tech community.
          </p>
        </section>

        {/* ━━━━ Form ━━━━ */}
        <form onSubmit={handleSubmit} className="space-y-10">

          {/* 1. Question Text */}
          <div className="space-y-4">
            <div className="flex justify-between items-end">
              <label className="block text-xs sm:text-sm font-bold tracking-tight text-[#1a1c1c] uppercase opacity-60">
                1. Question Text
              </label>
              <span className="text-[10px] font-medium text-[#464555] bg-[#eeeeee] px-2 py-0.5 rounded">
                {questionText.length} / {MAX_QUESTION}
              </span>
            </div>
            <div className="relative group">
              <textarea
                value={questionText}
                onChange={(e) => setQuestionText(e.target.value.slice(0, MAX_QUESTION))}
                placeholder="Type the interview question as you remember it..."
                className="w-full min-h-[180px] p-6 rounded-xl bg-white border-none focus:ring-2 focus:ring-[#3525cd]/20 focus:outline-none text-[#1a1c1c] placeholder:text-[#777587] transition-all text-base sm:text-lg leading-relaxed shadow-sm group-hover:shadow-md resize-none"
              />
            </div>
          </div>

          {/* 2 & 3. Domain + Question Type */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

            {/* Domain */}
            <div className="space-y-4">
              <label className="block text-xs sm:text-sm font-bold tracking-tight text-[#1a1c1c] uppercase opacity-60">
                2. Domain
              </label>
              <div className="relative">
                <select
                  value={domain}
                  onChange={(e) => setDomain(e.target.value as Domain)}
                  className="w-full p-4 rounded-xl bg-[#f3f3f3] border-none focus:ring-2 focus:ring-[#3525cd]/20 focus:outline-none text-[#1a1c1c] appearance-none cursor-pointer font-medium text-sm"
                >
                  {DOMAINS.map((d) => (
                    <option key={d} value={d}>{d}</option>
                  ))}
                </select>
                <span className="material-symbols-outlined absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-[#464555]">
                  expand_more
                </span>
              </div>
            </div>

            {/* Question Type */}
            <div className="space-y-4">
              <label className="block text-xs sm:text-sm font-bold tracking-tight text-[#1a1c1c] uppercase opacity-60">
                3. Question Type
              </label>
              <div className="flex flex-wrap gap-2">
                {QUESTION_TYPES.map((type) => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => setQuestionType(type)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all active:scale-95 ${
                      questionType === type
                        ? "bg-[#3525cd] text-white shadow-lg shadow-[#3525cd]/20"
                        : "bg-[#eeeeee] text-[#464555] hover:bg-[#e2e2e2]"
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* 4. Difficulty */}
          <div className="space-y-4">
            <label className="block text-xs sm:text-sm font-bold tracking-tight text-[#1a1c1c] uppercase opacity-60">
              4. Difficulty Level
            </label>
            <div className="flex gap-3 sm:gap-4">
              {DIFFICULTIES.map(({ label, color, border, bg }) => (
                <label key={label} className="flex-1 cursor-pointer">
                  <input
                    type="radio"
                    name="difficulty"
                    className="hidden peer"
                    checked={difficulty === label}
                    onChange={() => setDifficulty(label)}
                  />
                  <div
                    className={`p-4 rounded-xl bg-[#f3f3f3] border-2 transition-all text-center ${
                      difficulty === label ? `${border} ${bg}` : "border-transparent"
                    }`}
                  >
                    <span className={`block font-bold text-sm sm:text-base ${color}`}>{label}</span>
                  </div>
                </label>
              ))}
            </div>
          </div>

          {/* 5 & 6. Round + Year */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <label className="block text-xs sm:text-sm font-bold tracking-tight text-[#1a1c1c] uppercase opacity-60">
                5. Round <span className="normal-case font-normal opacity-70">(Optional)</span>
              </label>
              <input
                type="text"
                value={round}
                onChange={(e) => setRound(e.target.value)}
                placeholder="e.g. Technical Round 1"
                className="w-full p-4 rounded-xl bg-[#f3f3f3] border-none focus:ring-2 focus:ring-[#3525cd]/20 focus:outline-none text-[#1a1c1c] placeholder:text-[#777587] font-medium text-sm"
              />
            </div>
            <div className="space-y-4">
              <label className="block text-xs sm:text-sm font-bold tracking-tight text-[#1a1c1c] uppercase opacity-60">
                6. Year Asked <span className="normal-case font-normal opacity-70">(Optional)</span>
              </label>
              <input
                type="number"
                value={year}
                onChange={(e) => setYear(e.target.value)}
                placeholder="e.g. 2024"
                min={2010}
                max={2030}
                className="w-full p-4 rounded-xl bg-[#f3f3f3] border-none focus:ring-2 focus:ring-[#3525cd]/20 focus:outline-none text-[#1a1c1c] placeholder:text-[#777587] font-medium text-sm"
              />
            </div>
          </div>

          {/* 7. Answer Hint */}
          <div className="space-y-4">
            <div className="flex justify-between items-end">
              <label className="block text-xs sm:text-sm font-bold tracking-tight text-[#1a1c1c] uppercase opacity-60">
                7. Answer Hint <span className="normal-case font-normal opacity-70">(Optional)</span>
              </label>
              <span className="text-[10px] font-medium text-[#464555]">
                {answerHint.length} / {MAX_HINT}
              </span>
            </div>
            <textarea
              value={answerHint}
              onChange={(e) => setAnswerHint(e.target.value.slice(0, MAX_HINT))}
              placeholder="Any hints or notes on the expected answer..."
              className="w-full min-h-[120px] p-6 rounded-xl bg-[#f3f3f3] border-none focus:ring-2 focus:ring-[#3525cd]/20 focus:outline-none text-[#1a1c1c] placeholder:text-[#777587] transition-all text-sm resize-none"
            />
          </div>

          {/* Review Notice */}
          <div className="flex items-start gap-3 p-4 bg-[#3525cd]/5 rounded-xl border border-[#3525cd]/10">
            <span className="material-symbols-outlined text-[#3525cd] flex-shrink-0">info</span>
            <p className="text-sm text-[#3525cd]/80 font-medium leading-snug">
              Your question will be reviewed by our team before appearing on the profile.
            </p>
          </div>

        </form>
      </main>

      {/* ━━━━ Fixed Footer Action Bar ━━━━ */}
      <footer className="fixed bottom-0 left-0 w-full z-50 bg-[#f9f9f9]/90 backdrop-blur-md px-6 pb-8 pt-4 flex flex-col items-center gap-4 sm:border-t sm:border-[#f3f3f3]">
        <div className="max-w-3xl w-full flex items-center justify-between">
          <button
            type="button"
            onClick={() => router.back()}
            className="text-[#464555] font-bold text-sm tracking-widest uppercase hover:text-[#3525cd] transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            form=""
            onClick={handleSubmit}
            className="bg-[#4f46e5] hover:bg-[#3525cd] text-white rounded-xl px-8 py-4 font-bold tracking-tight shadow-xl shadow-[#3525cd]/20 active:scale-95 transition-all duration-300 ease-out flex items-center gap-2 text-sm"
          >
            Submit for Review
            <span className="material-symbols-outlined text-sm">send</span>
          </button>
        </div>
      </footer>

      {/* ━━━━ Bottom Nav — mobile only ━━━━ */}
      <nav className="sm:hidden fixed bottom-14 left-0 w-full z-40 flex justify-around items-center px-4 pb-4 pt-3 bg-[#f9f9f9]/90 backdrop-blur-md shadow-[0_-10px_30px_rgba(26,28,28,0.04)]">
        <Link
          href="/companies"
          className="flex flex-col items-center text-[#1a1c1c]/50 hover:text-[#3525cd] px-4 py-2 transition-colors"
        >
          <span className="material-symbols-outlined">school</span>
          <span className="text-[10px] font-medium tracking-wider uppercase mt-0.5">Prep</span>
        </Link>
        <Link
          href="#"
          className="flex flex-col items-center text-[#1a1c1c]/50 hover:text-[#3525cd] px-4 py-2 transition-colors"
        >
          <span className="material-symbols-outlined">terminal</span>
          <span className="text-[10px] font-medium tracking-wider uppercase mt-0.5">Practice</span>
        </Link>
        <div className="flex flex-col items-center bg-[#4f46e5] text-white rounded-xl px-4 py-2 scale-105">
          <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>add_circle</span>
          <span className="text-[10px] font-medium tracking-wider uppercase mt-0.5">Submit</span>
        </div>
        <Link
          href="#"
          className="flex flex-col items-center text-[#1a1c1c]/50 hover:text-[#3525cd] px-4 py-2 transition-colors"
        >
          <span className="material-symbols-outlined">person</span>
          <span className="text-[10px] font-medium tracking-wider uppercase mt-0.5">Profile</span>
        </Link>
      </nav>

    </div>
  );
}
