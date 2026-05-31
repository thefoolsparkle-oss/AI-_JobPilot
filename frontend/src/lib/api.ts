const API_BASE = "http://localhost:8000/api";

async function request<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
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

export const api = {
  health: () => request<{ status: string }>("/health"),

  profile: {
    get: () => request<any>("/profiles"),
    create: (data: any) => request<any>("/profiles", { method: "POST", body: JSON.stringify(data) }),
    update: (id: number, data: any) => request<any>(`/profiles/${id}`, { method: "PUT", body: JSON.stringify(data) }),
  },

  jobs: {
    parse: (jdText: string) => request<any>("/jobs/parse", { method: "POST", body: JSON.stringify({ jd_text: jdText }) }),
    match: (jobId: number) => request<any>(`/jobs/${jobId}/match`, { method: "POST" }),
    list: () => request<any[]>("/jobs"),
  },

  resumes: {
    generate: (data: any) => request<any>("/resumes/generate", { method: "POST", body: JSON.stringify(data) }),
    list: () => request<any[]>("/resumes"),
  },

  applications: {
    generate: (jobId: number) => request<any>(`/applications/generate`, { method: "POST", body: JSON.stringify({ job_id: jobId }) }),
  },
};
