"use client";

import { useState, useEffect, useCallback } from "react";

const API_BASE = "/api";

interface Profile {
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

interface Education {
  id?: number;
  school: string;
  degree: string;
  major: string;
  start_date: string;
  end_date: string;
  gpa: string;
  description: string;
}

interface ExperienceFact {
  id?: number;
  content: string;
  sort_order: number;
}

interface Experience {
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
  facts: ExperienceFact[];
}

interface Skill {
  id?: number;
  name: string;
  level: string;
  category: string;
}

interface JobPreference {
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

const emptyEducation = (): Education => ({
  school: "", degree: "", major: "", start_date: "", end_date: "", gpa: "", description: "",
});

const emptyExperience = (): Experience => ({
  experience_type: "internship", name: "", organization: "", title: "",
  start_date: "", end_date: "", location: "", tech_stack: [], allowed_claims: [],
  forbidden_claims: [], facts: [],
});

const emptySkill = (): Skill => ({ name: "", level: "intermediate", category: "programming" });

const emptyPreferences = (): JobPreference => ({
  target_roles: [], target_industries: [], preferred_locations: [],
  remote_preference: "any", min_duration_weeks: null, max_duration_weeks: null,
  available_from: "", excluded_roles: [], extra_context: "",
});

async function apiFetch(path: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<Profile | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"basic" | "education" | "experience" | "skills" | "preferences">("basic");

  const loadProfile = useCallback(async () => {
    try {
      const data = await apiFetch("/profiles");
      setProfile(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadProfile(); }, [loadProfile]);

  if (loading) return <div className="max-w-3xl mx-auto px-6 py-12 text-zinc-500">加载中...</div>;

  const tabs = [
    { key: "basic", label: "基本信息" },
    { key: "education", label: "教育" },
    { key: "experience", label: "经历" },
    { key: "skills", label: "技能" },
    { key: "preferences", label: "求职偏好" },
  ] as const;

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-zinc-800 mb-6">履历库</h1>

      <div className="flex gap-1 border-b border-zinc-200 mb-8">
        {tabs.map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
              activeTab === t.key
                ? "border-blue-600 text-blue-600"
                : "border-transparent text-zinc-500 hover:text-zinc-700"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === "basic" && profile && <BasicInfoForm profile={profile} onUpdate={loadProfile} />}
      {activeTab === "education" && profile && <EducationSection profile={profile} onUpdate={loadProfile} />}
      {activeTab === "experience" && profile && <ExperienceSection profile={profile} onUpdate={loadProfile} />}
      {activeTab === "skills" && profile && <SkillsSection profile={profile} onUpdate={loadProfile} />}
      {activeTab === "preferences" && profile && <PreferencesSection profile={profile} onUpdate={loadProfile} />}
    </div>
  );
}

function BasicInfoForm({ profile, onUpdate }: { profile: Profile; onUpdate: () => void }) {
  const [form, setForm] = useState({
    name: profile.name, email: profile.email, phone: profile.phone,
    location: profile.location, linkedin: profile.linkedin,
    github: profile.github, portfolio: profile.portfolio,
  });
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    await apiFetch("/profiles", { method: "PUT", body: JSON.stringify(form) });
    setSaving(false);
    onUpdate();
  };

  return (
    <div className="bg-white rounded-xl border border-zinc-200 p-6">
      <div className="grid gap-4 sm:grid-cols-2">
        {Object.entries(form).map(([key, value]) => (
          <div key={key}>
            <label className="block text-sm font-medium text-zinc-600 mb-1 capitalize">{key}</label>
            <input
              type="text"
              value={value}
              onChange={(e) => setForm({ ...form, [key]: e.target.value })}
              className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        ))}
      </div>
      <button
        onClick={handleSave}
        disabled={saving}
        className="mt-6 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        {saving ? "保存中..." : "保存"}
      </button>
    </div>
  );
}

function EducationSection({ profile, onUpdate }: { profile: Profile; onUpdate: () => void }) {
  const [items, setItems] = useState<Education[]>(profile.education || []);
  const [editingId, setEditingId] = useState<number | "new" | null>(null);
  const [form, setForm] = useState<Education>(emptyEducation());

  const startEdit = (edu?: Education) => {
    setForm(edu ? { ...edu } : emptyEducation());
    setEditingId(edu?.id ?? "new");
  };

  const handleSave = async () => {
    if (editingId === "new") {
      await apiFetch("/profiles/education", { method: "POST", body: JSON.stringify(form) });
    } else if (typeof editingId === "number") {
      await apiFetch(`/profiles/education/${editingId}`, { method: "PUT", body: JSON.stringify(form) });
    }
    setEditingId(null);
    const p = await apiFetch("/profiles");
    setItems(p.education);
    onUpdate();
  };

  const handleDelete = async (id: number) => {
    await apiFetch(`/profiles/education/${id}`, { method: "DELETE" });
    const p = await apiFetch("/profiles");
    setItems(p.education);
    onUpdate();
  };

  return (
    <div>
      <button onClick={() => startEdit()} className="mb-4 text-sm text-blue-600 hover:underline">+ 添加教育经历</button>
      {items.map((edu) => (
        <div key={edu.id} className="bg-white rounded-xl border border-zinc-200 p-4 mb-3">
          <div className="flex justify-between items-start">
            <div>
              <h3 className="font-semibold text-zinc-800">{edu.school}</h3>
              <p className="text-sm text-zinc-500">{edu.degree} · {edu.major} · {edu.start_date} ~ {edu.end_date}</p>
            </div>
            <div className="flex gap-2">
              <button onClick={() => startEdit(edu)} className="text-xs text-blue-600 hover:underline">编辑</button>
              <button onClick={() => edu.id && handleDelete(edu.id)} className="text-xs text-red-500 hover:underline">删除</button>
            </div>
          </div>
        </div>
      ))}

      {editingId !== null && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-lg max-h-[80vh] overflow-y-auto">
            <h2 className="text-lg font-bold mb-4">{editingId === "new" ? "添加" : "编辑"}教育经历</h2>
            <div className="grid gap-3">
              {(["school", "degree", "major", "start_date", "end_date", "gpa"] as const).map((f) => (
                <div key={f}>
                  <label className="block text-xs font-medium text-zinc-500 capitalize">{f.replace("_", " ")}</label>
                  <input value={form[f]} onChange={(e) => setForm({ ...form, [f]: e.target.value })}
                    className="w-full border border-zinc-200 rounded px-2 py-1 text-sm" />
                </div>
              ))}
              <div>
                <label className="block text-xs font-medium text-zinc-500">描述</label>
                <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })}
                  className="w-full border border-zinc-200 rounded px-2 py-1 text-sm" rows={3} />
              </div>
            </div>
            <div className="flex justify-end gap-2 mt-4">
              <button onClick={() => setEditingId(null)} className="px-4 py-2 text-sm text-zinc-600 rounded-lg border">取消</button>
              <button onClick={handleSave} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">保存</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ExperienceSection({ profile, onUpdate }: { profile: Profile; onUpdate: () => void }) {
  const [items, setItems] = useState<Experience[]>(profile.experiences || []);
  const [editingId, setEditingId] = useState<number | "new" | null>(null);
  const [form, setForm] = useState<Experience>(emptyExperience());
  const [parseText, setParseText] = useState("");
  const [parsing, setParsing] = useState(false);

  const startEdit = (exp?: Experience) => {
    setForm(exp ? { ...exp } : emptyExperience());
    setEditingId(exp?.id ?? "new");
  };

  const handleSave = async () => {
    const payload = { ...form, tech_stack: form.tech_stack.filter(Boolean), allowed_claims: form.allowed_claims.filter(Boolean), forbidden_claims: form.forbidden_claims.filter(Boolean) };
    if (editingId === "new") {
      await apiFetch("/profiles/experiences", { method: "POST", body: JSON.stringify(payload) });
    } else if (typeof editingId === "number") {
      await apiFetch(`/profiles/experiences/${editingId}`, { method: "PUT", body: JSON.stringify(payload) });
    }
    setEditingId(null);
    const p = await apiFetch("/profiles");
    setItems(p.experiences);
    onUpdate();
  };

  const handleDelete = async (id: number) => {
    await apiFetch(`/profiles/experiences/${id}`, { method: "DELETE" });
    const p = await apiFetch("/profiles");
    setItems(p.experiences);
    onUpdate();
  };

  const handleParse = async () => {
    setParsing(true);
    try {
      const result = await apiFetch("/profiles/experiences/parse", {
        method: "POST", body: JSON.stringify({ text: parseText, experience_type: "project" }),
      });
      setForm({
        ...emptyExperience(),
        experience_type: "project",
        name: result.name || "",
        organization: result.organization || "",
        title: result.title || "",
        start_date: result.start_date || "",
        end_date: result.end_date || "",
        location: result.location || "",
        tech_stack: result.tech_stack || [],
        allowed_claims: result.allowed_claims || [],
        forbidden_claims: result.forbidden_claims || [],
        facts: (result.facts || []).map((f: string, i: number) => ({ content: f, sort_order: i })),
      });
      setEditingId("new");
    } catch (e) {
      console.error(e);
    } finally {
      setParsing(false);
    }
  };

  const typeLabel = (t: string) => ({ internship: "实习", project: "项目", research: "科研" }[t] || t);

  return (
    <div>
      <div className="flex gap-3 mb-4">
        <button onClick={() => startEdit()} className="text-sm text-blue-600 hover:underline">+ 手动添加</button>
        <span className="text-zinc-300">|</span>
        <span className="text-sm text-zinc-500">或用 AI 解析文本：</span>
      </div>
      <div className="flex gap-2 mb-4">
        <textarea
          value={parseText}
          onChange={(e) => setParseText(e.target.value)}
          placeholder="粘贴一段经历描述，AI 自动解析..."
          className="flex-1 border border-zinc-300 rounded-lg px-3 py-2 text-sm h-20 resize-none"
        />
        <button onClick={handleParse} disabled={parsing || !parseText.trim()}
          className="px-4 py-2 bg-indigo-600 text-white text-sm rounded-lg hover:bg-indigo-700 disabled:opacity-50 self-end">
          {parsing ? "解析中..." : "AI 解析"}
        </button>
      </div>

      {items.map((exp) => (
        <div key={exp.id} className="bg-white rounded-xl border border-zinc-200 p-4 mb-3">
          <div className="flex justify-between items-start">
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xs bg-zinc-100 px-2 py-0.5 rounded">{typeLabel(exp.experience_type)}</span>
                <h3 className="font-semibold text-zinc-800">{exp.name || exp.title}</h3>
              </div>
              <p className="text-sm text-zinc-500">{exp.organization} · {exp.start_date} ~ {exp.end_date}</p>
              {exp.facts && exp.facts.length > 0 && (
                <ul className="mt-2 list-disc list-inside text-sm text-zinc-600">
                  {exp.facts.filter(f => f.content).slice(0, 3).map((f, i) => <li key={i}>{f.content}</li>)}
                </ul>
              )}
            </div>
            <div className="flex gap-2">
              <button onClick={() => startEdit(exp)} className="text-xs text-blue-600 hover:underline">编辑</button>
              <button onClick={() => exp.id && handleDelete(exp.id)} className="text-xs text-red-500 hover:underline">删除</button>
            </div>
          </div>
        </div>
      ))}

      {editingId !== null && (
        <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-2xl max-h-[85vh] overflow-y-auto">
            <h2 className="text-lg font-bold mb-4">{editingId === "new" ? "添加" : "编辑"}经历</h2>
            <div className="grid gap-3 sm:grid-cols-2">
              <div>
                <label className="block text-xs font-medium text-zinc-500">类型</label>
                <select value={form.experience_type} onChange={(e) => setForm({ ...form, experience_type: e.target.value })}
                  className="w-full border border-zinc-200 rounded px-2 py-1 text-sm">
                  <option value="internship">实习</option>
                  <option value="project">项目</option>
                  <option value="research">科研</option>
                </select>
              </div>
              {(["name", "organization", "title", "start_date", "end_date", "location"] as const).map((f) => (
                <div key={f}>
                  <label className="block text-xs font-medium text-zinc-500 capitalize">{f.replace("_", " ")}</label>
                  <input value={(form as any)[f]} onChange={(e) => setForm({ ...form, [f]: e.target.value })}
                    className="w-full border border-zinc-200 rounded px-2 py-1 text-sm" />
                </div>
              ))}
            </div>

            <div className="mt-4">
              <label className="block text-xs font-medium text-zinc-500">技术栈（逗号分隔）</label>
              <input value={form.tech_stack.join(", ")} onChange={(e) => setForm({ ...form, tech_stack: e.target.value.split(",").map(s => s.trim()) })}
                className="w-full border border-zinc-200 rounded px-2 py-1 text-sm" />
            </div>

            <div className="mt-4">
              <label className="block text-xs font-medium text-zinc-500">事实列表 (facts)</label>
              {(form.facts || []).map((f, i) => (
                <div key={i} className="flex gap-2 mt-1">
                  <input value={f.content} onChange={(e) => {
                    const nf = [...form.facts]; nf[i] = { ...nf[i], content: e.target.value }; setForm({ ...form, facts: nf });
                  }} className="flex-1 border border-zinc-200 rounded px-2 py-1 text-sm" />
                  <button onClick={() => setForm({ ...form, facts: form.facts.filter((_, j) => j !== i) })} className="text-red-400 text-xs">删除</button>
                </div>
              ))}
              <button onClick={() => setForm({ ...form, facts: [...form.facts, { content: "", sort_order: form.facts.length }] })}
                className="text-sm text-blue-600 mt-1">+ 添加事实</button>
            </div>

            <div className="mt-4 grid sm:grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-medium text-zinc-500">允许声称 (allowed_claims) 逗号分隔</label>
                <input value={form.allowed_claims.join(", ")} onChange={(e) => setForm({ ...form, allowed_claims: e.target.value.split(",").map(s => s.trim()) })}
                  className="w-full border border-zinc-200 rounded px-2 py-1 text-sm" />
              </div>
              <div>
                <label className="block text-xs font-medium text-zinc-500">禁止声称 (forbidden_claims) 逗号分隔</label>
                <input value={form.forbidden_claims.join(", ")} onChange={(e) => setForm({ ...form, forbidden_claims: e.target.value.split(",").map(s => s.trim()) })}
                  className="w-full border border-zinc-200 rounded px-2 py-1 text-sm" />
              </div>
            </div>

            <div className="flex justify-end gap-2 mt-6">
              <button onClick={() => setEditingId(null)} className="px-4 py-2 text-sm text-zinc-600 rounded-lg border">取消</button>
              <button onClick={handleSave} className="px-4 py-2 text-sm bg-blue-600 text-white rounded-lg">保存</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function SkillsSection({ profile, onUpdate }: { profile: Profile; onUpdate: () => void }) {
  const [items, setItems] = useState<Skill[]>(profile.skills || []);
  const [form, setForm] = useState<Skill>(emptySkill());

  const handleAdd = async () => {
    if (!form.name.trim()) return;
    await apiFetch("/profiles/skills", { method: "POST", body: JSON.stringify(form) });
    setForm(emptySkill());
    const p = await apiFetch("/profiles");
    setItems(p.skills);
    onUpdate();
  };

  const handleDelete = async (id: number) => {
    await apiFetch(`/profiles/skills/${id}`, { method: "DELETE" });
    const p = await apiFetch("/profiles");
    setItems(p.skills);
    onUpdate();
  };

  return (
    <div className="bg-white rounded-xl border border-zinc-200 p-6">
      <div className="flex gap-3 mb-4 items-end">
        <div>
          <label className="block text-xs font-medium text-zinc-500">技能名</label>
          <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })}
            className="border border-zinc-200 rounded px-2 py-1 text-sm w-32" />
        </div>
        <div>
          <label className="block text-xs font-medium text-zinc-500">等级</label>
          <select value={form.level} onChange={(e) => setForm({ ...form, level: e.target.value })}
            className="border border-zinc-200 rounded px-2 py-1 text-sm">
            <option value="beginner">入门</option>
            <option value="intermediate">熟练</option>
            <option value="advanced">精通</option>
            <option value="expert">专家</option>
          </select>
        </div>
        <div>
          <label className="block text-xs font-medium text-zinc-500">类别</label>
          <select value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })}
            className="border border-zinc-200 rounded px-2 py-1 text-sm">
            <option value="programming">编程语言</option>
            <option value="tool">工具</option>
            <option value="language">语言</option>
            <option value="soft_skill">软技能</option>
          </select>
        </div>
        <button onClick={handleAdd} className="px-4 py-1 bg-blue-600 text-white text-sm rounded-lg">添加</button>
      </div>
      <div className="flex flex-wrap gap-2">
        {items.map((s) => (
          <span key={s.id} className="inline-flex items-center gap-1 bg-zinc-100 text-zinc-700 px-3 py-1 rounded-full text-sm">
            {s.name} <span className="text-zinc-400 text-xs">({s.level})</span>
            <button onClick={() => s.id && handleDelete(s.id)} className="text-red-400 ml-1">&times;</button>
          </span>
        ))}
        {items.length === 0 && <p className="text-sm text-zinc-400">暂无技能，请添加</p>}
      </div>
    </div>
  );
}

function PreferencesSection({ profile, onUpdate }: { profile: Profile; onUpdate: () => void }) {
  const pref = profile.preferences?.[0] || emptyPreferences();
  const [form, setForm] = useState<JobPreference>(pref);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    const payload = {
      ...form,
      target_roles: form.target_roles.filter(Boolean),
      target_industries: form.target_industries.filter(Boolean),
      preferred_locations: form.preferred_locations.filter(Boolean),
      excluded_roles: form.excluded_roles.filter(Boolean),
    };
    await apiFetch("/profiles/preferences", { method: "PUT", body: JSON.stringify(payload) });
    setSaving(false);
    onUpdate();
  };

  return (
    <div className="bg-white rounded-xl border border-zinc-200 p-6">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-zinc-600">目标岗位（逗号分隔）</label>
          <input value={form.target_roles.join(", ")}
            onChange={(e) => setForm({ ...form, target_roles: e.target.value.split(",").map(s => s.trim()) })}
            className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm" placeholder="AI产品实习生, 后端开发实习生" />
        </div>
        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-zinc-600">偏好地点（逗号分隔）</label>
          <input value={form.preferred_locations.join(", ")}
            onChange={(e) => setForm({ ...form, preferred_locations: e.target.value.split(",").map(s => s.trim()) })}
            className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm" placeholder="远程, 上海, 北京" />
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-600">远程偏好</label>
          <select value={form.remote_preference} onChange={(e) => setForm({ ...form, remote_preference: e.target.value })}
            className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm">
            <option value="any">不限</option>
            <option value="remote">远程</option>
            <option value="hybrid">混合</option>
            <option value="onsite">线下</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-600">可开始时间</label>
          <input value={form.available_from} onChange={(e) => setForm({ ...form, available_from: e.target.value })}
            className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm" placeholder="2026-07" />
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-600">最短实习周数</label>
          <input type="number" value={form.min_duration_weeks || ""} onChange={(e) => setForm({ ...form, min_duration_weeks: e.target.value ? Number(e.target.value) : null })}
            className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm" />
        </div>
        <div>
          <label className="block text-sm font-medium text-zinc-600">最长实习周数</label>
          <input type="number" value={form.max_duration_weeks || ""} onChange={(e) => setForm({ ...form, max_duration_weeks: e.target.value ? Number(e.target.value) : null })}
            className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm" />
        </div>
        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-zinc-600">排除岗位（逗号分隔）</label>
          <input value={form.excluded_roles.join(", ")}
            onChange={(e) => setForm({ ...form, excluded_roles: e.target.value.split(",").map(s => s.trim()) })}
            className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm" placeholder="销售, 电话销售" />
        </div>
        <div className="sm:col-span-2">
          <label className="block text-sm font-medium text-zinc-600">其他补充</label>
          <textarea value={form.extra_context} onChange={(e) => setForm({ ...form, extra_context: e.target.value })}
            className="w-full border border-zinc-300 rounded-lg px-3 py-2 text-sm" rows={3} />
        </div>
      </div>
      <button onClick={handleSave} disabled={saving}
        className="mt-6 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50">
        {saving ? "保存中..." : "保存偏好"}
      </button>
    </div>
  );
}
