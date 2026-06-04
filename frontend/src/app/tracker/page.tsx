"use client";

import { useState, useEffect } from "react";

const API_BASE = "/api";

interface Record {
  id: number; job_id: number; job_title: string; company: string;
  status: string; status_label: string; priority: number;
  platform: string; hr_contact: string; notes: string;
  rejection_reason: string; interview_log: string;
  applied_at: string | null; follow_up_at: string | null;
  created_at: string; updated_at: string;
}

interface Analytics {
  total: number; applied: number; interviewing: number;
  offered: number; rejected: number;
  response_rate: number; interview_rate: number;
  status_counts: { [key: string]: number };
  rejection_reasons: { job: string; reason: string }[];
  recommendations: string[];
}

const STATUS_OPTIONS = [
  { value: "discovered", label: "已发现", color: "bg-zinc-100 text-zinc-700" },
  { value: "saved", label: "已收藏", color: "bg-blue-100 text-blue-700" },
  { value: "applied", label: "已投递", color: "bg-amber-100 text-amber-700" },
  { value: "interviewing", label: "面试中", color: "bg-purple-100 text-purple-700" },
  { value: "offered", label: "已 Offer", color: "bg-green-100 text-green-700" },
  { value: "rejected", label: "已拒绝", color: "bg-red-100 text-red-700" },
  { value: "archived", label: "已归档", color: "bg-zinc-200 text-zinc-500" },
];

export default function TrackerPage() {
  const [records, setRecords] = useState<Record[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState<number | null>(null);
  const [form, setForm] = useState({ status: "applied", priority: 3, platform: "", hr_contact: "", notes: "", rejection_reason: "", interview_log: "" });

  const loadRecords = async () => {
    try {
      const [recRes, anaRes] = await Promise.all([
        fetch(`${API_BASE}/tracker/records`),
        fetch(`${API_BASE}/tracker/analytics`),
      ]);
      setRecords(await recRes.json());
      setAnalytics(await anaRes.json());
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadRecords(); }, []);

  const handleUpdate = async (jobId: number) => {
    await fetch(`${API_BASE}/tracker/records/${jobId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(form),
    });
    setEditing(null);
    loadRecords();
  };

  if (loading) return <div className="max-w-5xl mx-auto px-6 py-12 text-zinc-500">加载中...</div>;

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-zinc-800 mb-2">投递追踪</h1>
      <p className="text-zinc-500 mb-6">看板式管理投递状态：发现 → 收藏 → 投递 → 面试 → Offer。</p>

      <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {STATUS_OPTIONS.map((col) => {
          const items = records.filter((r) => r.status === col.value);
          return (
            <div key={col.value} className="bg-zinc-50 rounded-xl p-3">
              <div className="flex items-center justify-between mb-3">
                <span className={`text-xs font-medium px-2 py-0.5 rounded ${col.color}`}>{col.label}</span>
                <span className="text-xs text-zinc-400">{items.length}</span>
              </div>
              <div className="space-y-2">
                {items.map((r) => (
                  <div key={r.id} className="bg-white rounded-lg border border-zinc-200 p-3 text-sm">
                    <div className="font-medium text-zinc-700 truncate">{r.company}</div>
                    <div className="text-xs text-zinc-500 truncate">{r.job_title}</div>
                    {r.platform && <div className="text-xs text-zinc-400 mt-1">平台: {r.platform}</div>}
                    <button
                      onClick={() => { setEditing(r.job_id); setForm({ status: r.status, priority: r.priority, platform: r.platform, hr_contact: r.hr_contact, notes: r.notes, rejection_reason: r.rejection_reason || "", interview_log: r.interview_log || "" }); }}
                      className="text-xs text-blue-500 hover:underline mt-1"
                    >
                      更新状态
                    </button>
                  </div>
                ))}
                {items.length === 0 && (
                  <p className="text-xs text-zinc-300 text-center py-4">空</p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {analytics && analytics.total > 0 && (
        <div className="mt-10">
          <h2 className="font-semibold text-zinc-800 mb-4">数据分析与建议</h2>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            <StatCard label="总投递" value={analytics.total} />
            <StatCard label="回复率" value={analytics.response_rate + "%"} />
            <StatCard label="面试率" value={analytics.interview_rate + "%"} />
            <StatCard label="Offer" value={analytics.offered} />
          </div>
          {analytics.recommendations.length > 0 && (
            <div className="mt-4 bg-blue-50 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-blue-800 mb-2">策略建议</h3>
              <ul className="list-disc list-inside text-sm text-blue-700 space-y-1">
                {analytics.recommendations.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          )}
          {analytics.rejection_reasons.length > 0 && (
            <div className="mt-4 bg-red-50 rounded-xl p-4">
              <h3 className="text-sm font-semibold text-red-800 mb-2">拒绝原因总结</h3>
              {analytics.rejection_reasons.map((r, i) => (
                <p key={i} className="text-sm text-red-700">{r.job}: {r.reason}</p>
              ))}
            </div>
          )}
        </div>
      )}

      {editing !== null && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md">
            <h2 className="font-semibold text-zinc-800 mb-4">更新状态</h2>
            <div className="grid gap-3">
              <div>
                <label className="block text-xs font-medium text-zinc-500 mb-1">状态</label>
                <select value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}
                  className="w-full border border-zinc-200 rounded px-2 py-1 text-sm">
                  {STATUS_OPTIONS.map((s) => <option key={s.value} value={s.value}>{s.label}</option>)}
                </select>
              </div>
              <div>
                <label className="block text-xs font-medium text-zinc-500 mb-1">投递平台</label>
                <input value={form.platform} onChange={(e) => setForm({ ...form, platform: e.target.value })}
                  className="w-full border border-zinc-200 rounded px-2 py-1 text-sm" placeholder="如: Boss直聘" />
              </div>
              <div>
                <label className="block text-xs font-medium text-zinc-500 mb-1">HR 联系方式</label>
                <input value={form.hr_contact} onChange={(e) => setForm({ ...form, hr_contact: e.target.value })}
                  className="w-full border border-zinc-200 rounded px-2 py-1 text-sm" />
              </div>
              <div className="flex gap-3">
                <div className="flex-1">
                  <label className="block text-xs font-medium text-zinc-500 mb-1">优先级 (1-5)</label>
                  <select value={form.priority} onChange={(e) => setForm({ ...form, priority: Number(e.target.value) })}
                    className="w-full border border-zinc-200 rounded px-2 py-1 text-sm">
                    {[1,2,3,4,5].map(n => <option key={n} value={n}>{n}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-xs font-medium text-zinc-500 mb-1">面试记录</label>
                <textarea value={form.interview_log} onChange={(e) => setForm({ ...form, interview_log: e.target.value })}
                  className="w-full border border-zinc-200 rounded px-2 py-1 text-sm" rows={2} placeholder="面试时间、问题、表现..." />
              </div>
              <div>
                <label className="block text-xs font-medium text-zinc-500 mb-1">拒绝原因</label>
                <input value={form.rejection_reason} onChange={(e) => setForm({ ...form, rejection_reason: e.target.value })}
                  className="w-full border border-zinc-200 rounded px-2 py-1 text-sm" placeholder="如：经验不匹配、已招满..." />
              </div>
              <div>
                <label className="block text-xs font-medium text-zinc-500 mb-1">备注</label>
                <textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })}
                  className="w-full border border-zinc-200 rounded px-2 py-1 text-sm" rows={2} />
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-4">
              <button onClick={() => setEditing(null)} className="px-4 py-2 text-sm text-zinc-600 rounded-lg border">取消</button>
              <button onClick={() => handleUpdate(editing!)} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">保存</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-white rounded-xl border border-zinc-200 p-4 text-center">
      <div className="text-2xl font-bold text-zinc-800">{value}</div>
      <div className="text-xs text-zinc-500 mt-1">{label}</div>
    </div>
  );
}
