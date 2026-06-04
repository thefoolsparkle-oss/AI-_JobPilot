"use client";

import { useState } from "react";

const API_BASE = "/api";

interface AssistResult {
  meaning: string;
  suggestion: string;
  natural_answer: string;
  risk_warning: string;
  needs_user_check: boolean;
}
interface Job { id: number; title: string; company: string; }
interface ResumeV { id: number; name: string; }

export default function AssistantPage() {
  const [formText, setFormText] = useState("");
  const [jobId, setJobId] = useState<number>(0);
  const [resumeId, setResumeId] = useState<number>(0);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [resumes, setResumes] = useState<ResumeV[]>([]);
  const [result, setResult] = useState<AssistResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loaded, setLoaded] = useState(false);
  const [ocrLoading, setOcrLoading] = useState(false);

  if (!loaded) {
    fetch(`${API_BASE}/jobs`).then(r => r.json()).then(setJobs).catch(console.error);
    fetch(`${API_BASE}/resumes`).then(r => r.json()).then(setResumes).catch(console.error).finally(() => setLoaded(true));
  }

  const handleAssist = async () => {
    if (!formText.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const body: any = { form_text: formText };
      if (jobId) body.job_id = jobId;
      if (resumeId) body.resume_id = resumeId;
      const res = await fetch(`${API_BASE}/assistant/form`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(await res.text());
      setResult(await res.json());
    } catch (e: any) {
      setError(e.message || "请求失败");
    } finally {
      setLoading(false);
    }
  };

  const handleOCRUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setOcrLoading(true);
    setError("");
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API_BASE}/assistant/ocr-upload`, { method: "POST", body: formData });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      if (data.text && data.text !== "未识别到文字") {
        setFormText(data.text);
        setError(`OCR 识别完成: ${data.text.length} 字符`);
      } else {
        setError(`OCR 结果: ${data.text || "无文字"}`);
      }
    } catch (e: any) {
      setError(`OCR 失败: ${e.message}`);
    } finally {
      setOcrLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-zinc-800 mb-2">申请表辅助</h1>
      <p className="text-zinc-500 mb-6">卡在申请表单、开放题、HR 消息？粘贴内容，AI 帮你分析怎么填。</p>

      <div className="bg-white rounded-xl border border-zinc-200 p-6 mb-6">
        <div className="mb-4">
          <label className="block text-sm font-medium text-zinc-600 mb-1">关联岗位（可选）</label>
          <select value={jobId} onChange={e => setJobId(Number(e.target.value))}
            className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm">
            <option value={0}>-- 不关联 --</option>
            {jobs.map(j => <option key={j.id} value={j.id}>{j.company} - {j.title}</option>)}
          </select>
        </div>
        <div className="mb-4">
          <label className="block text-sm font-medium text-zinc-600 mb-1">关联简历版本（可选，回答会更一致）</label>
          <select value={resumeId} onChange={e => setResumeId(Number(e.target.value))}
            className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm">
            <option value={0}>-- 不关联 --</option>
            {resumes.map(r => <option key={r.id} value={r.id}>{r.name}</option>)}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-600 mb-1">表单内容 / 问题 / HR 消息</label>
          <textarea
            value={formText}
            onChange={e => setFormText(e.target.value)}
            className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm h-32 resize-y"
            placeholder="粘贴申请表字段、开放题、HR 私信、错误提示等..."
          />
        </div>
        <div className="flex items-center gap-3 mt-3">
          <label className="text-sm text-zinc-500">或上传截图识别:</label>
          <label className="cursor-pointer px-3 py-1.5 border border-zinc-300 rounded-lg text-sm text-zinc-600 hover:bg-zinc-50">
            {ocrLoading ? "识别中..." : "选择图片"}
            <input type="file" accept="image/*" onChange={handleOCRUpload} className="hidden" disabled={ocrLoading} />
          </label>
          <span className="text-xs text-zinc-400">支持 jpg/png，文字自动填入上方</span>
        </div>
        <button onClick={handleAssist} disabled={loading || !formText.trim()}
          className="mt-4 px-6 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50">
          {loading ? "分析中..." : "AI 分析"}
        </button>
        {error && <p className="mt-3 text-sm text-red-500">{error}</p>}
      </div>

      {result && (
        <div className="space-y-4">
          <div className="bg-white rounded-xl border border-zinc-200 p-4">
            <h3 className="text-sm font-semibold text-zinc-500 mb-1">这是什么意思</h3>
            <p className="text-zinc-700">{result.meaning}</p>
          </div>
          <div className="bg-white rounded-xl border border-zinc-200 p-4">
            <h3 className="text-sm font-semibold text-zinc-500 mb-1">建议填写</h3>
            <p className="text-zinc-700">{result.suggestion}</p>
          </div>
          {result.natural_answer && (
            <div className="bg-green-50 rounded-xl border border-green-200 p-4">
              <h3 className="text-sm font-semibold text-green-700 mb-1">可用的自然表述</h3>
              <p className="text-green-800 whitespace-pre-wrap">{result.natural_answer}</p>
            </div>
          )}
          {result.risk_warning && (
            <div className="bg-amber-50 rounded-xl border border-amber-200 p-4">
              <h3 className="text-sm font-semibold text-amber-700 mb-1">风险提醒</h3>
              <p className="text-amber-800">{result.risk_warning}</p>
            </div>
          )}
          {result.needs_user_check && (
            <div className="bg-blue-50 rounded-xl border border-blue-200 p-3 text-sm text-blue-700">
              以上内容请自行确认后再使用。
            </div>
          )}
        </div>
      )}
    </div>
  );
}
