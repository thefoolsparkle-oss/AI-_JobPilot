"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

const API_BASE = "/api";

interface Job { id: number; title: string; company: string; location: string; url: string; }
interface SearchResult { title: string; url: string; snippet: string; }

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [query, setQuery] = useState("");
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searching, setSearching] = useState(false);
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState("");

  const loadJobs = async () => {
    try { const r = await fetch(`${API_BASE}/jobs`); setJobs(await r.json()); } catch (e) { console.error(e); }
  };

  useEffect(() => { loadJobs(); }, []);

  const handleSearch = async () => {
    if (!query.trim()) return;
    setSearching(true);
    setStatus("搜索中...");
    try {
      const r = await fetch(`${API_BASE}/discover/search`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, max_results: 10 }),
      });
      const data = await r.json();
      setSearchResults(data.results || []);
      setStatus(`找到 ${data.results?.length || 0} 个结果`);
    } catch (e: any) {
      setStatus(`搜索失败: ${e.message}`);
    } finally { setSearching(false); }
  };

  const handleSaveAndParse = async () => {
    if (!query.trim()) return;
    setSaving(true);
    setStatus("保存并解析中...");
    try {
      await fetch(`${API_BASE}/discover/save-and-parse`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, max_results: 5 }),
      });
      setStatus("已保存并开始解析，刷新查看结果");
      await loadJobs();
    } catch (e: any) {
      setStatus(`失败: ${e.message}`);
    } finally { setSaving(false); }
  };

  const handleAutoDiscover = async () => {
    setSearching(true);
    setStatus("自动发现中...");
    try {
      await fetch(`${API_BASE}/discover/search-all`, { method: "POST" });
      setStatus("搜索策略已执行");
    } catch (e: any) {
      setStatus(`失败: ${e.message}`);
    } finally { setSearching(false); }
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-zinc-800 mb-2">岗位发现</h1>
      <p className="text-zinc-500 mb-6">主动搜索岗位，自动保存、解析 JD、匹配评分。</p>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="bg-white rounded-xl border border-zinc-200 p-6">
          <h2 className="font-semibold text-zinc-700 mb-4">搜索岗位</h2>
          <div className="flex gap-2 mb-4">
            <input value={query} onChange={e => setQuery(e.target.value)}
              className="flex-1 border border-zinc-300 rounded-lg px-3 py-2 text-sm"
              placeholder="如: AI产品实习生 远程 2026" />
          </div>
          <div className="flex gap-2 mb-4">
            <button onClick={handleSearch} disabled={searching || !query.trim()}
              className="px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50">
              搜索
            </button>
            <button onClick={handleSaveAndParse} disabled={saving || !query.trim()}
              className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-50">
              保存并解析
            </button>
            <button onClick={handleAutoDiscover} disabled={searching}
              className="px-4 py-2 bg-green-600 text-white text-sm rounded-lg hover:bg-green-700 disabled:opacity-50">
              自动发现
            </button>
          </div>
          {status && <p className="text-sm text-zinc-500 mb-3">{status}</p>}
          {searchResults.length > 0 && (
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {searchResults.map((r, i) => (
                <div key={i} className="p-3 bg-zinc-50 rounded-lg text-sm">
                  <a href={r.url} target="_blank" className="font-medium text-blue-600 hover:underline">{r.title}</a>
                  <p className="text-zinc-500 text-xs mt-1 truncate">{r.snippet}</p>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl border border-zinc-200 p-6">
          <h2 className="font-semibold text-zinc-700 mb-4">已保存岗位 ({jobs.length})</h2>
          <div className="flex gap-2 mb-4">
            <Link href="/jobs/parse" className="text-xs text-blue-600 hover:underline">JD 解析</Link>
            <Link href="/jobs/match" className="text-xs text-blue-600 hover:underline">匹配评分</Link>
          </div>
          {jobs.length === 0 ? (
            <p className="text-sm text-zinc-400">暂无岗位，请先搜索并保存</p>
          ) : (
            <div className="space-y-2 max-h-80 overflow-y-auto">
              {jobs.map(j => (
                <div key={j.id} className="p-3 bg-zinc-50 rounded-lg text-sm">
                  <span className="font-medium text-zinc-700">{j.company}</span>
                  <span className="text-zinc-500 ml-2">{j.title}</span>
                  {j.location && <span className="text-zinc-400 text-xs ml-2">{j.location}</span>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
