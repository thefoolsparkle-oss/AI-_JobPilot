"use client";

import { useState, useEffect } from "react";

const API_BASE = "/api";

interface Job {
  id: number;
  title: string;
  company: string;
  location: string;
  parsed_jd: any;
}

interface Match {
  id: number;
  job_id: number;
  score: number;
  recommendation: string;
  summary: string;
  match_reasons: string[];
  risks: string[];
  resume_strategy: string[];
}

export default function JobMatchPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [match, setMatch] = useState<Match | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/jobs`)
      .then((r) => r.json())
      .then((data) => setJobs(data.filter((j: Job) => j.parsed_jd)))
      .catch(console.error);
  }, []);

  const handleMatch = async (job: Job) => {
    setSelectedJob(job);
    setLoading(true);
    setError("");
    setMatch(null);
    try {
      const res = await fetch(`${API_BASE}/jobs/${job.id}/match`, { method: "POST" });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setMatch(data);
    } catch (e: any) {
      setError(e.message || "匹配分析失败");
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (s: number) => {
    if (s >= 80) return "text-green-600";
    if (s >= 60) return "text-blue-600";
    if (s >= 40) return "text-amber-600";
    return "text-red-500";
  };

  const getRecLabel = (r: string) =>
    ({ apply: "建议投递", review: "需评估", skip: "不推荐" }[r] || r);

  const getRecColor = (r: string) =>
    ({ apply: "bg-green-100 text-green-700", review: "bg-amber-100 text-amber-700", skip: "bg-red-100 text-red-700" }[r] || "");

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-zinc-800 mb-2">岗位匹配</h1>
      <p className="text-zinc-500 mb-6">系统对比你的履历与岗位要求，给出匹配评分和投递建议。</p>

      {jobs.length === 0 ? (
        <div className="p-8 border border-dashed border-zinc-300 rounded-xl text-center text-zinc-400">
          暂无已解析的岗位。请先在「JD 解析」中添加岗位。
        </div>
      ) : (
        <div className="grid gap-3 mb-8">
          {jobs.map((job) => (
            <div
              key={job.id}
              className={`bg-white rounded-xl border p-4 flex justify-between items-center cursor-pointer transition-all ${
                selectedJob?.id === job.id ? "border-blue-500 ring-2 ring-blue-100" : "border-zinc-200 hover:border-zinc-300"
              }`}
              onClick={() => handleMatch(job)}
            >
              <div>
                <h3 className="font-semibold text-zinc-800">{job.title}</h3>
                <p className="text-sm text-zinc-500">{job.company} · {job.location}</p>
              </div>
              <button className="px-4 py-1.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700">
                匹配分析
              </button>
            </div>
          ))}
        </div>
      )}

      {loading && <div className="text-center text-zinc-500 py-8">AI 分析中，请稍候...</div>}
      {error && <p className="text-red-500 text-sm">{error}</p>}

      {match && (
        <div className="bg-white rounded-xl border border-zinc-200 p-6">
          <div className="flex items-center gap-4 mb-6">
            <div className={`text-4xl font-bold ${getScoreColor(match.score)}`}>{match.score}</div>
            <div>
              <div className="text-lg font-semibold text-zinc-800">匹配度评分</div>
              <span className={`text-xs px-2 py-0.5 rounded ${getRecColor(match.recommendation)}`}>
                {getRecLabel(match.recommendation)}
              </span>
            </div>
          </div>
          <p className="text-zinc-600 mb-6">{match.summary}</p>

          <div className="grid gap-4 sm:grid-cols-2">
            <div className="bg-green-50 rounded-lg p-4">
              <h3 className="font-semibold text-green-800 text-sm mb-2">匹配优势</h3>
              <ul className="list-disc list-inside text-sm text-green-700 space-y-1">
                {match.match_reasons.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
            <div className="bg-red-50 rounded-lg p-4">
              <h3 className="font-semibold text-red-800 text-sm mb-2">潜在风险</h3>
              <ul className="list-disc list-inside text-sm text-red-700 space-y-1">
                {match.risks.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          </div>
          {match.resume_strategy.length > 0 && (
            <div className="mt-4 bg-blue-50 rounded-lg p-4">
              <h3 className="font-semibold text-blue-800 text-sm mb-2">简历策略建议</h3>
              <ul className="list-disc list-inside text-sm text-blue-700 space-y-1">
                {match.resume_strategy.map((s, i) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
