"use client";

import { useState, useEffect } from "react";

const API_BASE = "/api";

interface Job { id: number; title: string; company: string; }
interface Template { id: number; name: string; style: string; }
interface Resume { id: number; name: string; docx_path: string; pdf_path: string; created_at: string; }

export default function ResumesPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedJob, setSelectedJob] = useState<number>(0);
  const [selectedTemplate, setSelectedTemplate] = useState<number>(0);
  const [generating, setGenerating] = useState(false);
  const [status, setStatus] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/jobs`).then(r => r.json()).then(setJobs).catch(console.error);
    fetch(`${API_BASE}/templates`).then(r => r.json()).then(data => { setTemplates(data); if (data[0]) setSelectedTemplate(data[0].id); }).catch(console.error);
    fetch(`${API_BASE}/resumes`).then(r => r.json()).then(setResumes).catch(console.error);
  }, []);

  const handleGenerate = async () => {
    if (!selectedJob || !selectedTemplate) return;
    setGenerating(true);
    setStatus("AI 正在生成简历内容...");
    try {
      const res = await fetch(`${API_BASE}/resumes/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_id: selectedJob, template_id: selectedTemplate }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setStatus(`简历已生成: ${data.docx_path}`);
      const updated = await fetch(`${API_BASE}/resumes`).then(r => r.json());
      setResumes(updated);
    } catch (e: any) {
      setStatus(`错误: ${e.message}`);
    } finally {
      setGenerating(false);
    }
  };

  const [exportingPdf, setExportingPdf] = useState<number | null>(null);

  const handleExportPdf = async (resumeId: number) => {
    setExportingPdf(resumeId);
    try {
      const res = await fetch(`${API_BASE}/resumes/${resumeId}/export-pdf`, { method: "POST" });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      window.open(`${API_BASE}/resumes/${resumeId}/download-pdf`, "_blank");
      const updated = await fetch(`${API_BASE}/resumes`).then(r => r.json());
      setResumes(updated);
      setStatus(`PDF 已导出`);
    } catch (e: any) {
      setStatus(`PDF 导出失败: ${e.message}`);
    } finally {
      setExportingPdf(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-zinc-800 mb-2">简历生成</h1>
      <p className="text-zinc-500 mb-6">选择岗位和模板，AI 基于你的履历生成岗位专用简历。</p>

      <div className="bg-white rounded-xl border border-zinc-200 p-6 mb-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-zinc-600 mb-1">选择岗位</label>
            <select value={selectedJob} onChange={e => setSelectedJob(Number(e.target.value))}
              className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm">
              <option value={0}>-- 选择已解析的岗位 --</option>
              {jobs.map(j => <option key={j.id} value={j.id}>{j.company} - {j.title}</option>)}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-zinc-600 mb-1">选择模板</label>
            <select value={selectedTemplate} onChange={e => setSelectedTemplate(Number(e.target.value))}
              className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm">
              {templates.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
          </div>
        </div>
        <button onClick={handleGenerate} disabled={generating || !selectedJob || !selectedTemplate}
          className="mt-4 px-6 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {generating ? "生成中..." : "生成简历"}
        </button>
        {status && <p className="mt-3 text-sm text-zinc-600">{status}</p>}
      </div>

      <div>
        <h2 className="font-semibold text-zinc-800 mb-3">已生成的简历版本</h2>
        {resumes.length === 0 ? (
          <p className="text-sm text-zinc-400">暂无简历版本</p>
        ) : (
          <div className="space-y-2">
            {resumes.map(r => (
              <div key={r.id} className="bg-white rounded-lg border border-zinc-200 p-3 text-sm flex justify-between items-center">
                <div>
                  <span className="font-medium text-zinc-700">{r.name}</span>
                  <span className="text-zinc-400 text-xs ml-3">{new Date(r.created_at).toLocaleString()}</span>
                </div>
                <div className="flex gap-2">
                  {r.pdf_path ? (
                    <a href={`${API_BASE}/resumes/${r.id}/download-pdf`} className="text-xs text-green-600 hover:underline">PDF</a>
                  ) : (
                    <button onClick={() => handleExportPdf(r.id)} disabled={exportingPdf === r.id}
                      className="text-xs text-blue-600 hover:underline disabled:opacity-50">
                      {exportingPdf === r.id ? "导出中..." : "导出PDF"}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
