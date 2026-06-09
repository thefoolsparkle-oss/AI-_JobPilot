interface RequestOptions extends RequestInit {
  params?: Record<string, string>;
}

const TOKEN_KEY = "jobpilot_token";

function getAuthHeaders(): Record<string, string> {
  if (typeof window === "undefined") return {};
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return {};
  return { Authorization: `Bearer ${token}` };
}

async function request<T>(endpoint: string, options?: RequestOptions): Promise<T> {
  const url = `/api${endpoint}`;
  const authHeaders = getAuthHeaders();
  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...authHeaders,
      ...options?.headers,
    },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export interface Profile {
  id?: number;
  name: string;
  email: string;
  phone: string;
  location: string;
  linkedin: string;
  github: string;
  portfolio: string;
  education: Education[];
  experiences: Experience[];
  skills: Skill[];
  preferences: JobPreference[];
}

export interface Education {
  id?: number;
  school: string;
  degree: string;
  major: string;
  start_date: string;
  end_date: string;
  gpa: string;
  description: string;
}

export interface ExperienceFact {
  id?: number;
  content: string;
  claim_level: string;
  risk_level: string;
  interview_explanation: string;
  sort_order: number;
}

export interface Experience {
  id?: number;
  experience_type: string;
  name: string;
  organization: string;
  title: string;
  start_date: string;
  end_date: string;
  location: string;
  tech_stack: string[];
  allowed_claims: string[];
  forbidden_claims: string[];
  evidence: string[];
  transferable_skills: string[];
  facts: ExperienceFact[];
}

export interface Skill {
  id?: number;
  name: string;
  level: string;
  category: string;
}

export interface JobPreference {
  id?: number;
  target_roles: string[];
  target_industries: string[];
  preferred_locations: string[];
  remote_preference: string;
  min_duration_weeks: number | null;
  max_duration_weeks: number | null;
  available_from: string;
  excluded_roles: string[];
  extra_context: string;
}

export interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  remote_type: string;
  url: string;
  source: string;
  parsed_jd: ParsedJD | null;
  discovered_at: string;
}

export interface ParsedJD {
  title: string;
  company: string;
  location: string;
  remote_type: string;
  duration: string;
  responsibilities: string[];
  requirements: string[];
  nice_to_have: string[];
  hard_filters: string[];
  risk_flags: string[];
}

export interface JobMatch {
  id: number;
  job_id: number;
  score: number;
  decision: string;
  decision_reasons: string;
  hard_filter_passed: boolean;
  hard_filter_details: string[];
  user_confirm_required: string[];
  application_strategy: string;
  match_reasons: string[];
  risks: string[];
  resume_strategy: string[];
}

export interface ResumeVersion {
  id: number;
  template_id: number;
  name: string;
  docx_path: string;
  pdf_path: string;
  created_at: string;
  data?: Record<string, unknown>;
}

export interface ApplicationPackage {
  id: number;
  job_id: number;
  self_intro: string;
  application_reason: string;
  hr_message: string;
  cover_letter: string;
  form_answers: { question: string; answer: string }[];
  risk_notes: string;
  interview_questions: string[];
}

export interface TrackerRecord {
  id: number;
  job_id: number;
  job_title: string;
  company: string;
  status: string;
  status_label: string;
  priority: number;
  platform: string;
  hr_contact: string;
  notes: string;
  rejection_reason: string;
  interview_log: string;
  applied_at: string | null;
  follow_up_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface TrackerAnalytics {
  total: number;
  applied: number;
  interviewing: number;
  offered: number;
  rejected: number;
  response_rate: number;
  interview_rate: number;
  status_counts: Record<string, number>;
  rejection_reasons: { job: string; reason: string }[];
  recommendations: string[];
}

export interface SearchResult {
  title: string;
  url: string;
  snippet: string;
}

export interface FormAssistResult {
  meaning: string;
  suggestion: string;
  natural_answer: string;
  risk_warning: string;
  needs_user_check: boolean;
}

export interface SettingsInfo {
  has_key: boolean;
  masked_key: string;
  models: {
    fast_model: string;
    reasoning_model: string;
    base_url: string;
  };
}

export interface Template {
  id: number;
  name: string;
  description: string;
  style: string;
  template_file: string;
}

export const api = {
  health: () => request<{ status: string; version: string }>("/health"),

  profile: {
    get: () => request<Profile>("/profiles"),
    update: (data: Partial<Profile>) => request<Profile>("/profiles", { method: "PUT", body: JSON.stringify(data) }),
    addEducation: (data: Partial<Education>) => request<Education>("/profiles/education", { method: "POST", body: JSON.stringify(data) }),
    updateEducation: (id: number, data: Partial<Education>) => request<Education>(`/profiles/education/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    deleteEducation: (id: number) => request<{ ok: boolean }>(`/profiles/education/${id}`, { method: "DELETE" }),
    addExperience: (data: Partial<Experience>) => request<Experience>("/profiles/experiences", { method: "POST", body: JSON.stringify(data) }),
    updateExperience: (id: number, data: Partial<Experience>) => request<Experience>(`/profiles/experiences/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    deleteExperience: (id: number) => request<{ ok: boolean }>(`/profiles/experiences/${id}`, { method: "DELETE" }),
    parseExperience: (text: string, experienceType: string) => request<Record<string, unknown>>("/profiles/experiences/parse", { method: "POST", body: JSON.stringify({ text, experience_type: experienceType }) }),
    addSkill: (data: Partial<Skill>) => request<Skill>("/profiles/skills", { method: "POST", body: JSON.stringify(data) }),
    deleteSkill: (id: number) => request<{ ok: boolean }>(`/profiles/skills/${id}`, { method: "DELETE" }),
    getPreferences: () => request<JobPreference>("/profiles/preferences"),
    updatePreferences: (data: Partial<JobPreference>) => request<JobPreference>("/profiles/preferences", { method: "PUT", body: JSON.stringify(data) }),
  },

  jobs: {
    parse: (jdText: string, url?: string, source?: string) => request<Job>("/jobs/parse", { method: "POST", body: JSON.stringify({ jd_text: jdText, url, source }) }),
    list: () => request<Job[]>("/jobs"),
    get: (id: number) => request<Job>(`/jobs/${id}`),
    delete: (id: number) => request<{ ok: boolean }>(`/jobs/${id}`, { method: "DELETE" }),
    match: (jobId: number) => request<JobMatch>(`/jobs/${jobId}/match`, { method: "POST" }),
    getMatch: (jobId: number) => request<JobMatch>(`/jobs/${jobId}/match`),
    batchMatch: (jobIds: number[]) => request<{ results: { job_id: number; score: number; decision: string }[] }>("/jobs/batch-match", { method: "POST", body: JSON.stringify({ job_ids: jobIds }) }),
  },

  resumes: {
    list: () => request<ResumeVersion[]>("/resumes"),
    generate: (jobId: number, templateId: number) => request<ResumeVersion>("/resumes/generate", { method: "POST", body: JSON.stringify({ job_id: jobId, template_id: templateId }) }),
    exportPdf: (resumeId: number) => request<{ pdf_path: string; filename: string }>(`/resumes/${resumeId}/export-pdf`, { method: "POST" }),
    review: (resumeId: number, jobId: number) => request<Record<string, unknown>>(`/resumes/${resumeId}/review?job_id=${jobId}`, { method: "POST" }),
  },

  templates: {
    list: () => request<Template[]>("/templates"),
  },

  applications: {
    generate: (jobId: number) => request<ApplicationPackage>("/applications/generate", { method: "POST", body: JSON.stringify({ job_id: jobId }) }),
    get: (jobId: number) => request<ApplicationPackage>(`/applications/${jobId}`),
  },

  discover: {
    searchStrategy: () => request<Record<string, unknown>>("/discover/search-strategy", { method: "POST" }),
    search: (query: string, maxResults?: number) => request<{ query: string; results: SearchResult[] }>("/discover/search", { method: "POST", body: JSON.stringify({ query, max_results: maxResults ?? 10 }) }),
    searchAll: () => request<{ queries: string[]; results: SearchResult[] }>("/discover/search-all", { method: "POST" }),
    saveAndParse: (query: string, maxResults?: number) => request<{ query: string; saved: number; jobs: Record<string, unknown>[] }>("/discover/save-and-parse", { method: "POST", body: JSON.stringify({ query, max_results: maxResults ?? 5 }) }),
    fetchUrl: (url: string) => request<Record<string, unknown>>("/discover/fetch", { method: "POST", body: JSON.stringify({ url }) }),
  },

  assistant: {
    form: (formText: string, jobId?: number, resumeId?: number, imagePath?: string) => request<FormAssistResult>("/assistant/form", { method: "POST", body: JSON.stringify({ form_text: formText, job_id: jobId, resume_id: resumeId, image_path: imagePath }) }),
    ocr: (imagePath: string) => request<{ text: string; image_path: string }>("/assistant/ocr", { method: "POST", body: JSON.stringify({ image_path: imagePath }) }),
  },

  tracker: {
    records: () => request<TrackerRecord[]>("/tracker/records"),
    analytics: () => request<TrackerAnalytics>("/tracker/analytics"),
    upsert: (jobId: number, data: Record<string, unknown>) => request<TrackerRecord>(`/tracker/records/${jobId}`, { method: "POST", body: JSON.stringify(data) }),
    delete: (jobId: number) => request<{ ok: boolean }>(`/tracker/records/${jobId}`, { method: "DELETE" }),
  },

  settings: {
    get: () => request<SettingsInfo>("/settings"),
    setKey: (apiKey: string) => request<{ ok: boolean; masked_key: string }>("/settings/key", { method: "PUT", body: JSON.stringify({ api_key: apiKey }) }),
    setModel: (data: { base_url: string; fast_model: string; reasoning_model: string }) => request<{ ok: boolean }>("/settings/models", { method: "PUT", body: JSON.stringify(data) }),
  },
};
