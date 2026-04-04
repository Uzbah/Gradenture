"use client";

import { useState } from "react";
import Link from "next/link";

const DOMAINS = [
  { id: "backend",   label: "Backend",   icon: "dns" },
  { id: "frontend",  label: "Frontend",  icon: "web" },
  { id: "fullstack", label: "Full-Stack", icon: "layers" },
  { id: "mobile",    label: "Mobile",    icon: "smartphone" },
  { id: "devops",    label: "DevOps",    icon: "terminal" },
] as const;

const HOW_IT_WORKS = [
  { step: 1, icon: "search",       title: "Browse Companies",      desc: "Explore profiles of top software houses and startups in Karachi." },
  { step: 2, icon: "auto_stories", title: "Read Real Experiences",  desc: "Deep dive into interview rounds and questions shared by candidates." },
  { step: 3, icon: "rate_review",  title: "Submit Your Own",        desc: "Help the community by sharing your own interview journey." },
] as const;

const NAV_LINKS = [
  { href: "/companies", label: "Companies", icon: "business" },
  { href: "/jobs",      label: "Jobs",      icon: "work" },
  { href: "#",          label: "Prep",      icon: "terminal" },
] as const;

export default function HomePage() {
  const [activeDomain, setActiveDomain] = useState("backend");

  return (
    <div className="bg-[#f9f9f9] min-h-dvh antialiased pb-24 lg:pb-0" style={{ color: "#1a1c1c", fontFamily: "Inter, sans-serif" }}>

      {/* ━━━━ Header ━━━━ */}
      <header className="fixed top-0 w-full z-50 bg-[#f9f9f9]/80 backdrop-blur-md">
        <div className="flex justify-between items-center px-6 h-16 max-w-7xl mx-auto">

          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 flex-shrink-0">
            <span className="material-symbols-outlined text-[#3525cd]">architecture</span>
            <span className="font-bold tracking-tight text-xl text-[#3525cd]">KHI Tech Prep</span>
          </Link>

          {/* Desktop nav links */}
          <nav className="hidden lg:flex items-center gap-1">
            {NAV_LINKS.map(({ href, label }) => (
              <Link
                key={label}
                href={href}
                className="px-4 py-2 rounded-lg text-slate-600 hover:text-[#3525cd] hover:bg-[#4f46e5]/5 font-medium text-sm transition-all"
              >
                {label}
              </Link>
            ))}
          </nav>

          {/* Right side */}
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="hidden lg:inline-flex items-center gap-2 px-4 py-2 rounded-xl border border-[#3525cd] text-[#3525cd] text-sm font-semibold hover:bg-[#4f46e5]/5 transition-all"
            >
              Sign In
            </Link>
            <div className="w-8 h-8 rounded-full bg-[#4f46e5] flex items-center justify-center text-white text-xs font-bold cursor-pointer">
              U
            </div>
          </div>
        </div>
        <div className="bg-[#f3f3f3] h-[1px] w-full" />
      </header>

      <main className="pt-16">

        {/* ━━━━ Hero ━━━━ */}
        <section className="relative bg-[#4f46e5] text-white overflow-hidden">
          <div className="absolute inset-0 hero-pattern opacity-40" />
          {/* Decorative blobs */}
          <div className="absolute -right-32 -bottom-32 w-96 h-96 bg-[#3525cd]/30 rounded-full blur-3xl" />
          <div className="absolute -left-20 top-10 w-72 h-72 bg-white/5 rounded-full blur-3xl" />

          <div className="relative z-10 max-w-7xl mx-auto px-6 py-16 lg:py-28 lg:flex lg:items-center lg:gap-20">

            {/* Text block */}
            <div className="space-y-6 lg:max-w-xl xl:max-w-2xl">
              <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-md px-3 py-1.5 rounded-full border border-white/10">
                <span className="w-2 h-2 rounded-full bg-white animate-pulse" />
                <span className="text-[10px] font-bold uppercase tracking-widest">Built for Karachi CS Students</span>
              </div>

              <h2 className="text-4xl lg:text-6xl font-extrabold leading-[1.1] tracking-tight">
                Ace Your Tech Interview.{" "}
                <span className="text-[#c3c0ff]">Land Your First Job.</span>
              </h2>

              <p className="text-[#dad7ff] leading-relaxed font-medium text-base lg:text-lg max-w-lg">
                Community-verified interview questions, real candidate experiences, and fresher job listings — all in one place.
              </p>

              <div className="flex flex-col sm:flex-row gap-3 pt-2">
                <Link
                  href="/companies"
                  className="bg-white text-[#3525cd] font-bold py-4 px-8 rounded-xl shadow-lg active:scale-95 transition-transform text-center hover:bg-[#e2dfff]"
                >
                  Explore Companies
                </Link>
                <Link
                  href="/jobs"
                  className="bg-white/10 border border-white/20 text-white font-bold py-4 px-8 rounded-xl backdrop-blur-sm active:scale-95 transition-transform text-center hover:bg-white/20"
                >
                  Browse Jobs
                </Link>
              </div>
            </div>

            {/* Desktop decorative card grid */}
            <div className="hidden lg:flex flex-1 justify-end items-center">
              <div className="grid grid-cols-2 gap-4 opacity-80">
                {[
                  { icon: "apartment", label: "Systems Ltd", tag: "Backend" },
                  { icon: "rocket_launch", label: "Arbisoft", tag: "Full-Stack" },
                  { icon: "monitoring", label: "Netsol Tech", tag: "DevOps" },
                  { icon: "hub", label: "Folio3", tag: "Frontend" },
                ].map(({ icon, label, tag }) => (
                  <div key={label} className="bg-white/10 backdrop-blur-sm border border-white/10 rounded-2xl p-4 flex flex-col gap-2 w-40">
                    <span className="material-symbols-outlined text-white/80">{icon}</span>
                    <p className="font-bold text-sm text-white">{label}</p>
                    <span className="text-[10px] bg-white/10 text-white/80 px-2 py-0.5 rounded-full w-fit font-semibold">{tag}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ━━━━ Stats ━━━━ */}
        <section className="max-w-7xl mx-auto px-6 -mt-8 relative z-20">
          <div className="grid grid-cols-3 lg:grid-cols-3 gap-2 bg-white p-4 lg:p-6 rounded-2xl shadow-[0_20px_40px_rgba(26,28,28,0.06)] border border-[#c7c4d8]/10">
            {[
              { value: "12+",  label: "Companies",    icon: "business" },
              { value: "200+", label: "Questions",    icon: "quiz" },
              { value: "30+",  label: "Fresher Jobs", icon: "work" },
            ].map(({ value, label, icon }, i) => (
              <div key={label} className={`text-center py-2 lg:py-4 ${i === 1 ? "border-x border-slate-100" : ""}`}>
                <span className="material-symbols-outlined text-[#4f46e5] text-xl lg:text-3xl hidden lg:block mx-auto mb-1">{icon}</span>
                <p className="text-lg lg:text-3xl font-extrabold text-[#3525cd]">{value}</p>
                <p className="text-[9px] lg:text-xs uppercase tracking-tighter text-slate-500 font-bold mt-0.5">{label}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ━━━━ Domain Filter ━━━━ */}
        <section className="max-w-7xl mx-auto mt-14">
          <div className="px-6 flex justify-between items-end mb-5">
            <div>
              <p className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-1">Filter By Domain</p>
              <h3 className="text-xl lg:text-2xl font-bold tracking-tight">Explore by Specialisation</h3>
            </div>
            <span className="text-xs text-[#3525cd] font-bold cursor-pointer hover:underline">View All</span>
          </div>

          {/* Mobile: horizontal scroll / Desktop: wrap */}
          <div className="flex gap-3 overflow-x-auto lg:overflow-visible lg:flex-wrap px-6 no-scrollbar pb-2">
            {DOMAINS.map(({ id, label, icon }) => (
              <button
                key={id}
                onClick={() => setActiveDomain(id)}
                className={`flex-none flex items-center gap-2 px-5 py-3 rounded-2xl transition-all font-bold text-sm ${
                  activeDomain === id
                    ? "bg-[#a44100] text-white shadow-md scale-[1.02]"
                    : "bg-[#f3f3f3] text-slate-600 hover:bg-[#eeeeee] hover:scale-[1.01]"
                }`}
              >
                <span className="material-symbols-outlined text-sm">{icon}</span>
                {label}
              </button>
            ))}
          </div>
        </section>

        {/* ━━━━ How It Works ━━━━ */}
        <section className="max-w-7xl mx-auto mt-20 px-6">
          <div className="text-center mb-12">
            <p className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-2">Simple Process</p>
            <h3 className="text-2xl lg:text-4xl font-bold tracking-tight">How It Works</h3>
          </div>

          {/* Mobile: vertical steps / Desktop: 3-column cards */}
          <div className="lg:hidden space-y-8 relative">
            <div className="absolute left-6 top-8 bottom-8 w-[2px] bg-slate-100 -z-10" />
            {HOW_IT_WORKS.map(({ step, icon, title, desc }) => (
              <div key={step} className="flex gap-6">
                <div className="flex-none w-12 h-12 rounded-full bg-[#4f46e5] text-white flex items-center justify-center font-bold shadow-lg ring-4 ring-white text-sm">
                  {step}
                </div>
                <div className="flex flex-col pt-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="material-symbols-outlined text-[#3525cd] text-xl">{icon}</span>
                    <h4 className="font-bold text-lg">{title}</h4>
                  </div>
                  <p className="text-slate-500 text-sm leading-relaxed">{desc}</p>
                </div>
              </div>
            ))}
          </div>

          <div className="hidden lg:grid grid-cols-3 gap-6">
            {HOW_IT_WORKS.map(({ step, icon, title, desc }) => (
              <div key={step} className="relative bg-white rounded-2xl p-8 border border-[#c7c4d8]/20 shadow-sm hover:shadow-md transition-shadow group">
                <div className="absolute -top-4 left-8 w-8 h-8 rounded-full bg-[#4f46e5] text-white flex items-center justify-center font-bold text-sm shadow-md">
                  {step}
                </div>
                <span className="material-symbols-outlined text-[#4f46e5] text-4xl mb-4 block group-hover:scale-110 transition-transform">{icon}</span>
                <h4 className="font-bold text-xl mb-2">{title}</h4>
                <p className="text-slate-500 text-sm leading-relaxed">{desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* ━━━━ CTA Banner (desktop only) ━━━━ */}
        <section className="hidden lg:block max-w-7xl mx-auto mt-20 px-6">
          <div className="relative bg-[#3525cd] rounded-3xl px-12 py-14 overflow-hidden text-white flex items-center justify-between gap-8">
            <div className="absolute inset-0 hero-pattern opacity-20" />
            <div className="relative z-10">
              <h3 className="text-3xl font-extrabold mb-2">Ready to crack your next interview?</h3>
              <p className="text-[#c3c0ff] font-medium">Join thousands of Karachi CS students already using the platform.</p>
            </div>
            <div className="relative z-10 flex gap-4 flex-shrink-0">
              <Link
                href="/register"
                className="bg-white text-[#3525cd] font-bold px-6 py-3 rounded-xl hover:bg-[#e2dfff] transition-colors"
              >
                Get Started Free
              </Link>
              <Link
                href="/companies"
                className="border border-white/30 text-white font-bold px-6 py-3 rounded-xl hover:bg-white/10 transition-colors"
              >
                Browse Companies
              </Link>
            </div>
          </div>
        </section>

        {/* ━━━━ Footer ━━━━ */}
        <footer className="mt-20 bg-[#f3f3f3] border-t border-slate-200">
          <div className="max-w-7xl mx-auto px-6 py-10 lg:py-12">

            {/* Desktop: 3-column / Mobile: stacked center */}
            <div className="flex flex-col items-center text-center lg:flex-row lg:items-start lg:justify-between lg:text-left gap-8">

              {/* Brand */}
              <div className="space-y-2">
                <div className="flex items-center gap-2 justify-center lg:justify-start">
                  <span className="material-symbols-outlined text-[#3525cd]">architecture</span>
                  <span className="font-bold text-[#3525cd] text-lg">KHI Tech Prep</span>
                </div>
                <p className="text-sm text-slate-500 max-w-xs">
                  Built for Karachi CS students navigating their first tech job.
                </p>
              </div>

              {/* Links */}
              <div className="flex gap-12 lg:gap-16">
                <div className="space-y-2">
                  <p className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3">Platform</p>
                  {[{ href: "/companies", label: "Companies" }, { href: "/jobs", label: "Jobs" }, { href: "#", label: "Prep" }].map(({ href, label }) => (
                    <div key={label}>
                      <a href={href} className="text-slate-500 hover:text-[#3525cd] text-sm transition-colors block">{label}</a>
                    </div>
                  ))}
                </div>
                <div className="space-y-2">
                  <p className="text-xs font-bold uppercase tracking-widest text-slate-400 mb-3">Legal</p>
                  {["Privacy", "Terms", "Feedback"].map((label) => (
                    <div key={label}>
                      <a href="#" className="text-slate-500 hover:text-[#3525cd] text-sm transition-colors block">{label}</a>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-8 pt-6 border-t border-slate-200 text-center">
              <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold">© 2024 Karachi Tech Prep Hub</p>
            </div>
          </div>
        </footer>

      </main>

      {/* ━━━━ Bottom Nav — mobile only ━━━━ */}
      <nav className="lg:hidden fixed bottom-0 left-0 w-full z-50 bg-[#f9f9f9]/90 backdrop-blur-md border-t border-slate-200/50 shadow-[0_-4px_20px_rgba(26,28,28,0.04)] rounded-t-2xl">
        <div className="flex justify-around items-center px-4 pb-6 pt-3 max-w-md mx-auto">
          <Link href="/" className="flex flex-col items-center text-[#3525cd] bg-[#4f46e5]/10 rounded-xl px-3 py-1 active:scale-90 transition-all">
            <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>home</span>
            <span className="text-[11px] font-medium tracking-wide uppercase mt-1">Home</span>
          </Link>
          {NAV_LINKS.map(({ href, label, icon }) => (
            <Link key={label} href={href} className="flex flex-col items-center text-slate-500 hover:text-[#3525cd] active:scale-90 transition-all">
              <span className="material-symbols-outlined">{icon}</span>
              <span className="text-[11px] font-medium tracking-wide uppercase mt-1">{label}</span>
            </Link>
          ))}
        </div>
      </nav>

    </div>
  );
}
