"use client";

import { useState } from "react";

const API_BASE = "/api";

interface ParsedJD {
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

export default function JobParsePage() {
  const [jdText, setJdText] = useState("");
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [result, setResult] = useState<{ id: number; parsed_jd: ParsedJD } | null>(null);
  const [error, setError] = useState("");

  const handleFetch = async () => {
    if (!url.trim()) return;
    setFetching(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/discover/fetch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim() }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      if (data.error) throw new Error(data.error);
      setJdText(data.content);
      setError(`已抓取: ${data.title || url}`);
    } catch (e: any) {
      setError(`抓取失败: ${e.message}`);
    } finally {
      setFetching(false);
    }
  };

  const handleParse = async () => {
    if (!jdText.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch(`${API_BASE}/jobs/parse`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ jd_text: jdText, url, source: "manual" }),
      });
      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setResult(data);
    } catch (e: any) {
      setError(e.message || "解析失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-zinc-800 mb-2">JD 解析</h1>
      <p className="text-zinc-500 mb-6">粘贴岗位描述文本，系统自动提取结构化信息和隐藏要求。</p>

      <div className="bg-white rounded-xl border border-zinc-200 p-6 mb-6">
        <div className="mb-4">
          <label className="block text-sm font-medium text-zinc-600 mb-1">岗位链接（可自动抓取网页）</label>
          <div className="flex gap-2">
            <input
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              className="flex-1 border border-zinc-300 rounded-lg px-3 py-2 text-sm"
              placeholder="https://..."
            />
            <button
              onClick={handleFetch}
              disabled={fetching || !url.trim()}
              className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-50 whitespace-nowrap"
            >
              {fetching ? "抓取中..." : "抓取网页"}
            </button>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-600 mb-1">JD 文本</label>
          <textarea
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm h-40 resize-y"
            placeholder="粘贴招聘岗位描述全文..."
          />
        </div>
        <button
          onClick={handleParse}
          disabled={loading || !jdText.trim()}
          className="mt-4 px-6 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "解析中..." : "AI 解析 JD"}
        </button>
        {error && <p className="mt-3 text-sm text-red-500">{error}</p>}
      </div>

      {result && (
        <div className="bg-white rounded-xl border border-zinc-200 p-6">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-zinc-800">{result.parsed_jd.title || "未命名"}</h2>
              <p className="text-zinc-500 mt-1">
                {result.parsed_jd.company} · {result.parsed_jd.location}
                {result.parsed_jd.remote_type && ` · ${result.parsed_jd.remote_type}`}
                {result.parsed_jd.duration && ` · ${result.parsed_jd.duration}`}
              </p>
            </div>
            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">已解析</span>
          </div>

          <div className="grid gap-6 sm:grid-cols-2">
            <Section title="岗位职责" items={result.parsed_jd.responsibilities} icon="📋" />
            <Section title="硬性要求" items={result.parsed_jd.requirements} icon="✅" />
            <Section title="加分项" items={result.parsed_jd.nice_to_have} icon="⭐" />
            <Section title="硬性门槛" items={result.parsed_jd.hard_filters} icon="⚠️" type="warning" />
          </div>
          {result.parsed_jd.risk_flags.length > 0 && (
            <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <h3 className="text-sm font-semibold text-red-700 mb-2">风险标记</h3>
              <ul className="list-disc list-inside text-sm text-red-600 space-y-1">
                {result.parsed_jd.risk_flags.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function Section({ title, items, icon, type }: { title: string; items: string[]; icon: string; type?: string }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <h3 className="text-sm font-semibold text-zinc-700 mb-2">{icon} {title}</h3>
      <ul className={`list-disc list-inside text-sm space-y-1 ${type === "warning" ? "text-amber-700" : "text-zinc-600"}`}>
        {items.map((item, i) => <li key={i}>{item}</li>)}
      </ul>
    </div>
  );
}
