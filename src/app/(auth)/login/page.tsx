"use client";

import { useState } from "react";
import Link from "next/link";

export default function LoginPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [showError, setShowError]       = useState(true);
  const [showWarning, setShowWarning]   = useState(true);

  return (
    <div className="min-h-dvh flex" style={{ fontFamily: "Inter, sans-serif" }}>

      {/* ━━━━ Left Branding Panel — desktop only ━━━━ */}
      <aside className="hidden lg:flex flex-col justify-between w-[480px] xl:w-[520px] flex-shrink-0 bg-[#3525cd] text-white px-12 py-14 relative overflow-hidden">
        {/* Background pattern */}
        <div className="absolute inset-0 hero-pattern opacity-20" />
        {/* Decorative blobs */}
        <div className="absolute -bottom-24 -left-24 w-80 h-80 bg-white/5 rounded-full blur-3xl" />
        <div className="absolute top-20 right-0 w-64 h-64 bg-[#4f46e5]/40 rounded-full blur-3xl" />

        {/* Logo */}
        <div className="relative z-10 flex items-center gap-3">
          <div className="w-10 h-10 bg-white/10 border border-white/20 rounded-xl flex items-center justify-center">
            <span className="material-symbols-outlined text-white text-2xl">architecture</span>
          </div>
          <span className="font-extrabold text-lg tracking-tight">KHI Tech Prep</span>
        </div>

        {/* Headline */}
        <div className="relative z-10 space-y-8">
          <div className="space-y-4">
            <div className="inline-flex items-center gap-2 bg-white/10 px-3 py-1.5 rounded-full border border-white/10">
              <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
              <span className="text-[10px] font-bold uppercase tracking-widest">Karachi's #1 CS Prep Platform</span>
            </div>
            <h2 className="text-4xl xl:text-5xl font-extrabold leading-[1.1] tracking-tight">
              Your interview prep starts here.
            </h2>
            <p className="text-[#c3c0ff] text-base leading-relaxed font-medium">
              Access real questions, company experiences, and fresher job listings — all community-verified.
            </p>
          </div>

          {/* Feature highlights */}
          <div className="space-y-4">
            {[
              { icon: "apartment",    text: "12+ company interview breakdowns" },
              { icon: "quiz",         text: "200+ verified interview questions" },
              { icon: "work_history", text: "30+ active fresher job postings" },
            ].map(({ icon, text }) => (
              <div key={text} className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0">
                  <span className="material-symbols-outlined text-white/80 text-lg">{icon}</span>
                </div>
                <p className="text-[#c3c0ff] text-sm font-medium">{text}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Bottom tagline */}
        <p className="relative z-10 text-[10px] text-white/30 uppercase tracking-widest font-bold">
          © 2024 KHI Tech Prep Hub
        </p>
      </aside>

      {/* ━━━━ Right Form Panel ━━━━ */}
      <div className="flex-1 flex flex-col items-center justify-center bg-[#f3f3f3] px-4 py-12 lg:px-16 min-h-dvh lg:min-h-0">

        {/* Mobile brand (hidden on desktop) */}
        <div className="lg:hidden flex flex-col items-center mb-8">
          <div className="w-12 h-12 bg-[#3525cd] flex items-center justify-center rounded-xl mb-3 shadow-lg shadow-[#3525cd]/20">
            <span className="material-symbols-outlined text-white text-3xl">architecture</span>
          </div>
          <h2 className="font-extrabold tracking-tighter text-[#1a1c1c] text-xl uppercase">KHI Tech Prep</h2>
        </div>

        {/* Card */}
        <div className="w-full max-w-[420px] lg:max-w-[460px] bg-white rounded-2xl p-8 shadow-[0_20px_40px_rgba(26,28,28,0.06)]">

          {/* Alert states */}
          {(showError || showWarning) && (
            <div className="space-y-3 mb-6">
              {showError && (
                <div className="flex items-center justify-between bg-[#ffdad6]/40 p-3 rounded-lg border-l-4 border-[#ba1a1a]">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-[#ba1a1a] text-[20px]">error</span>
                    <p className="text-[#93000a] text-xs font-medium leading-tight">
                      Invalid email or password. Please try again.
                    </p>
                  </div>
                  <button
                    onClick={() => setShowError(false)}
                    className="text-[#93000a] opacity-60 hover:opacity-100 transition-opacity ml-2 flex-shrink-0"
                    type="button"
                    aria-label="Dismiss error"
                  >
                    <span className="material-symbols-outlined text-[18px]">close</span>
                  </button>
                </div>
              )}
              {showWarning && (
                <div className="flex items-center justify-between bg-[#ffdbcc]/30 p-3 rounded-lg border-l-4 border-[#7e3000]">
                  <div className="flex items-center gap-2">
                    <span className="material-symbols-outlined text-[#7e3000] text-[20px]">warning</span>
                    <p className="text-[#7b2f00] text-xs font-medium leading-tight">
                      Too many attempts. Please wait 15 minutes.
                    </p>
                  </div>
                  <button
                    onClick={() => setShowWarning(false)}
                    className="text-[#7b2f00] opacity-60 hover:opacity-100 transition-opacity ml-2 flex-shrink-0"
                    type="button"
                    aria-label="Dismiss warning"
                  >
                    <span className="material-symbols-outlined text-[18px]">close</span>
                  </button>
                </div>
              )}
            </div>
          )}

          {/* Heading */}
          <div className="mb-7">
            <h1 className="font-bold text-2xl text-[#1a1c1c] tracking-tight mb-1">Welcome back</h1>
            <p className="text-[#464555] text-sm">Sign in to track your prep progress.</p>
          </div>

          {/* Form */}
          <form action="#" method="POST" className="space-y-5">

            {/* Email */}
            <div className="space-y-1.5">
              <label
                htmlFor="email"
                className="block text-xs font-bold text-[#464555] tracking-wider uppercase"
              >
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                placeholder="name@company.com"
                className="w-full bg-[#f9f9f9] rounded-lg px-4 py-3 text-[#1a1c1c] placeholder:text-[#777587] text-sm ring-1 ring-[#c7c4d8]/40 focus:ring-2 focus:ring-[#3525cd] focus:outline-none transition-all duration-200"
              />
            </div>

            {/* Password */}
            <div className="space-y-1.5">
              <div className="flex justify-between items-center">
                <label
                  htmlFor="password"
                  className="block text-xs font-bold text-[#464555] tracking-wider uppercase"
                >
                  Password
                </label>
                <a href="#" className="text-xs font-semibold text-[#3525cd] hover:text-[#4f46e5] transition-colors">
                  Forgot?
                </a>
              </div>
              <div className="relative">
                <input
                  id="password"
                  name="password"
                  type={showPassword ? "text" : "password"}
                  placeholder="••••••••"
                  className="w-full bg-[#f9f9f9] rounded-lg px-4 py-3 pr-11 text-[#1a1c1c] placeholder:text-[#777587] text-sm ring-1 ring-[#c7c4d8]/40 focus:ring-2 focus:ring-[#3525cd] focus:outline-none transition-all duration-200"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword((p) => !p)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-[#777587] hover:text-[#464555] transition-colors"
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  <span className="material-symbols-outlined text-[20px]">
                    {showPassword ? "visibility_off" : "visibility"}
                  </span>
                </button>
              </div>
            </div>

            {/* Submit */}
            <button
              type="submit"
              className="w-full bg-[#4f46e5] hover:bg-[#3525cd] text-white font-bold py-3.5 rounded-xl shadow-lg shadow-[#3525cd]/10 active:scale-[0.98] transition-all duration-200 text-sm"
            >
              Sign In
            </button>

            {/* Divider */}
            <div className="relative flex items-center py-2">
              <div className="flex-grow border-t border-[#e2e2e2]" />
              <span className="mx-4 text-[10px] font-bold uppercase tracking-widest text-[#c7c4d8]">
                Or continue with
              </span>
              <div className="flex-grow border-t border-[#e2e2e2]" />
            </div>

            {/* Google OAuth */}
            <button
              type="button"
              className="w-full flex items-center justify-center gap-3 bg-white border border-[#c7c4d8]/40 hover:bg-[#f3f3f3] text-[#1a1c1c] font-semibold py-3 rounded-xl transition-colors active:scale-[0.98] text-sm"
            >
              {/* Google SVG logo — no external image dependency */}
              <svg className="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
              </svg>
              Continue with Google
            </button>
          </form>

          {/* Sign up link */}
          <div className="mt-8 text-center">
            <p className="text-[#464555] text-sm">
              Don't have an account?{" "}
              <Link href="/register" className="text-[#3525cd] font-bold hover:underline underline-offset-4">
                Create one
              </Link>
            </p>
          </div>
        </div>

        {/* Mobile footer */}
        <p className="lg:hidden mt-8 text-[10px] text-[#777587] uppercase tracking-widest font-medium opacity-60 text-center">
          © 2024 KHI Tech Prep Hub
        </p>
      </div>

    </div>
  );
}
