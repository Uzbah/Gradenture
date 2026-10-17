const BASE = import.meta.env.VITE_API_BASE_URL || "/api/v1";

export function getToken(): string | null {
  return localStorage.getItem("token");
}

// Clearing the access token (logout, dead session) clears the refresh token too.
export function setToken(token: string | null, refreshToken?: string) {
  if (token) localStorage.setItem("token", token);
  else localStorage.removeItem("token");
  if (refreshToken) localStorage.setItem("refresh_token", refreshToken);
  else if (!token) localStorage.removeItem("refresh_token");
}

// One refresh at a time: parallel 401s all wait on the same call, because
// Supabase rotates the refresh token and a second use of the old one fails.
let refreshing: Promise<boolean> | null = null;

function refreshSession(): Promise<boolean> {
  const refreshToken = localStorage.getItem("refresh_token");
  if (!refreshToken) return Promise.resolve(false);
  refreshing ??= fetch(`${BASE}/auth/refresh`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh_token: refreshToken }),
  })
    .then(async (res) => {
      if (!res.ok) return false;
      const json = await res.json();
      setToken(json.access_token, json.refresh_token);
      return true;
    })
    .catch(() => false)
    .finally(() => { refreshing = null; });
  return refreshing;
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function extractError(body: any): string {
  if (body?.error) return body.error;
  if (body?.errors) {
    return Object.entries(body.errors as Record<string, string[]>)
      .map(([field, msgs]) => `${field}: ${msgs.join(", ")}`)
      .join("; ");
  }
  return "Request failed";
}

export async function api<T = any>(
  path: string,
  opts: { method?: string; body?: any; token?: string } = {}
): Promise<T> {
  const headers: Record<string, string> = {};

  let body: BodyInit | undefined;
  if (opts.body instanceof FormData) {
    body = opts.body;
  } else if (opts.body !== undefined) {
    headers["Content-Type"] = "application/json";
    body = JSON.stringify(opts.body);
  }

  const send = () => {
    const token = opts.token ?? getToken();
    if (token) headers.Authorization = `Bearer ${token}`;
    return fetch(`${BASE}${path}`, { method: opts.method ?? "GET", headers, body });
  };

  let res = await send();
  // Access tokens last ~1h: on a 401, refresh once and retry. Skipped when the
  // caller passed its own token (password-recovery link).
  if (res.status === 401 && !opts.token && getToken() && (await refreshSession())) {
    res = await send();
  }
  const json = await res.json().catch(() => ({}));
  if (!res.ok) {
    if (res.status === 401 && getToken()) {
      setToken(null);
      window.location.href = "/login";
    }
    throw new ApiError(res.status, extractError(json));
  }
  return json as T;
}

// For user-supplied links rendered as <a href>. The API now only accepts
// http(s), but rows saved before that may hold javascript: URLs, which
// React 18 still renders (and runs on click).
export function safeUrl(url?: string | null): string | undefined {
  return url && /^https?:\/\//i.test(url) ? url : undefined;
}

// --- shared types matching the backend ---
export interface Domain { id: string; name: string; slug: string }
export interface Company {
  id: string; name: string; slug: string; website?: string; industry?: string;
  logo_url?: string; status?: "pending" | "approved";
}
export interface User {
  id: string; email: string; role: "user" | "admin" | "super_admin";
  domain_id?: string; skill_level?: string; goal?: string; university?: string;
  onboarding_complete: boolean; suspended_at?: string | null;
}
export interface Flag {
  id: string; content_type: "question" | "review"; content_id: string;
  reason: string; status: string; created_at: string;
  content?: (Question & Review) | null;
}
export interface Question {
  id: string; domain_id: string; company_id: string; role_title: string;
  question_text: string; question_type: string; difficulty: string;
  asked_date: string; notes?: string; upvotes: number; status: string;
  created_at: string; submitted_by?: string; admin_note?: string;
}
export interface BankQuestion {
  id: string; domain_id: string; company_id?: string | null; role_title: string;
  question_text: string; question_type: string; difficulty?: string | null;
}
export interface Review {
  id: string; company_id: string; domain_id?: string; role_title: string;
  review_text: string; interview_date: string; difficulty?: string;
  outcome?: string; status: string; created_at: string; submitted_by?: string;
  admin_note?: string;
}
export interface MySubmissions {
  questions: (Question & { notes?: string | null })[];
  reviews: Review[];
}
export interface Application {
  id: string; company_name: string; role_title: string;
  status: "applied" | "interview" | "offer" | "rejected" | "closed";
  applied_date?: string; deadline?: string; job_url?: string; notes?: string;
}
export interface CompanyManager {
  user_id: string; created_at: string; users?: { email: string } | null;
}
export interface CompanyEdit {
  id: string; company_id: string; requested_by: string;
  changes: Record<string, string>; status: string; created_at: string;
  companies?: { name: string } | null;
}
