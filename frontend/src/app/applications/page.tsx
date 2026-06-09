"use client";

import { useState, useEffect } from "react";
import { api, Job, ApplicationPackage } from "@/lib/api";
import { LoadingSpinner } from "@/components/UIComponents";

export default function ApplicationsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<number>(0);
  const [pkg, setPkg] = useState<ApplicationPackage | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    api.jobs.list().then(setJobs).catch(console.error);
  }, []);

  const handleGenerate = async () => {
    if (!selectedJob) return;
    setLoading(true);
    setError("");
    try {
      setPkg(await api.applications.generate(selectedJob));
    } catch (e: unknown) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-zinc-800 mb-2">投递材料包</h1>
      <p className="text-zinc-500 mb-6">生成自我介绍、申请理由、HR 私信、Cover Letter 和面试准备。</p>

      <div className="bg-white rounded-xl border border-zinc-200 p-6 mb-6 flex items-end gap-4">
        <div className="flex-1">
          <label className="block text-sm font-medium text-zinc-600 mb-1">选择岗位</label>
          <select value={selectedJob} onChange={e => setSelectedJob(Number(e.target.value))}
            className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm">
            <option value={0}>-- 选择岗位 --</option>
            {jobs.map(j => <option key={j.id} value={j.id}>{j.company} - {j.title}</option>)}
          </select>
        </div>
        <button onClick={handleGenerate} disabled={loading || !selectedJob}
          className="px-6 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-50">
          {loading ? "生成中..." : "生成材料包"}
        </button>
      </div>

      {error && <p className="text-red-500 text-sm mb-4">{error}</p>}

      {pkg && (
        <div className="space-y-4">
          <Card title="自我介绍" content={pkg.self_intro} />
          <Card title="申请理由" content={pkg.application_reason} />
          <Card title="HR 私信" content={pkg.hr_message} />
          <Card title="Cover Letter" content={pkg.cover_letter} />
          {pkg.risk_notes && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
              <h3 className="font-semibold text-amber-800 text-sm mb-1">风险提醒</h3>
              <p className="text-sm text-amber-700">{pkg.risk_notes}</p>
            </div>
          )}
          {pkg.form_answers?.length > 0 && (
            <div className="bg-violet-50 border border-violet-200 rounded-xl p-4">
              <h3 className="font-semibold text-violet-800 text-sm mb-2">常见开放题</h3>
              {pkg.form_answers.map((fa, i) => (
                <div key={i} className="mb-2">
                  <p className="text-xs text-violet-600 font-medium">{fa.question}</p>
                  <p className="text-sm text-violet-800">{fa.answer}</p>
                </div>
              ))}
            </div>
          )}
          {pkg.interview_questions.length > 0 && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <h3 className="font-semibold text-blue-800 text-sm mb-2">可能面试问题</h3>
              <ul className="list-disc list-inside text-sm text-blue-700 space-y-1">
                {pkg.interview_questions.map((q, i) => <li key={i}>{q}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function Card({ title, content }: { title: string; content: string }) {
  if (!content) return null;
  return (
    <div className="bg-white rounded-xl border border-zinc-200 p-4">
      <h3 className="font-semibold text-zinc-700 text-sm mb-2">{title}</h3>
      <p className="text-sm text-zinc-600 whitespace-pre-wrap leading-relaxed">{content}</p>
    </div>
  );
}
