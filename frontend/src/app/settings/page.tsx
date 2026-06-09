"use client";

import { useState, useEffect } from "react";
import { api, SettingsInfo } from "@/lib/api";
import { LoadingSpinner } from "@/components/UIComponents";

const PRESETS = [
  { label: "DeepSeek", base_url: "https://api.deepseek.com", fast: "deepseek-chat", reasoning: "deepseek-reasoner" },
  { label: "OpenAI", base_url: "https://api.openai.com/v1", fast: "gpt-4o", reasoning: "gpt-4o" },
  { label: "Kimi (月之暗面)", base_url: "https://api.moonshot.cn/v1", fast: "moonshot-v1-8k", reasoning: "moonshot-v1-128k" },
  { label: "Qwen (通义千问)", base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1", fast: "qwen-plus", reasoning: "qwen-max" },
];

export default function SettingsPage() {
  const [settings, setSettings] = useState<SettingsInfo | null>(null);
  const [keyInput, setKeyInput] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [modelForm, setModelForm] = useState({ base_url: "", fast_model: "", reasoning_model: "" });

  const loadSettings = async () => {
    try {
      const d = await api.settings.get();
      setSettings(d);
      setModelForm({ base_url: d.models.base_url, fast_model: d.models.fast_model, reasoning_model: d.models.reasoning_model });
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => { loadSettings(); }, []);

  const handleSave = async () => {
    if (!keyInput.trim()) return;
    setSaving(true);
    setMessage("");
    try {
      await api.settings.setKey(keyInput);
      setMessage("API Key 已保存");
      setKeyInput("");
      loadSettings();
    } catch (e: unknown) {
      setMessage(`保存失败: ${(e as Error).message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleModelSave = async () => {
    setSaving(true);
    setMessage("");
    try {
      await api.settings.setModel(modelForm);
      setMessage("模型配置已保存，重启后生效");
      loadSettings();
    } catch (e: unknown) {
      setMessage(`保存失败: ${(e as Error).message}`);
    } finally {
      setSaving(false);
    }
  };

  const applyPreset = (p: typeof PRESETS[0]) => {
    setModelForm({ base_url: p.base_url, fast_model: p.fast, reasoning_model: p.reasoning });
  };

  if (!settings) return <LoadingSpinner />;

  return (
    <div className="max-w-2xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-zinc-800 mb-6">设置</h1>

      <div className="bg-white rounded-xl border border-zinc-200 p-6 mb-6">
        <h2 className="font-semibold text-zinc-700 mb-4">LLM 模型信息</h2>
        <div className="grid gap-3 text-sm">
          <div className="flex justify-between py-2 border-b border-zinc-100">
            <span className="text-zinc-500">接口地址</span>
            <span className="text-zinc-700 font-mono text-xs">{settings.models.base_url}</span>
          </div>
          <div className="flex justify-between py-2 border-b border-zinc-100">
            <span className="text-zinc-500">普通任务模型</span>
            <span className="text-zinc-700 font-mono">{settings.models.fast_model}</span>
          </div>
          <div className="flex justify-between py-2">
            <span className="text-zinc-500">深度推理模型</span>
            <span className="text-zinc-700 font-mono">{settings.models.reasoning_model}</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-zinc-200 p-6 mb-6">
        <h2 className="font-semibold text-zinc-700 mb-4">模型配置</h2>
        <p className="text-sm text-zinc-500 mb-3">快速预设</p>
        <div className="flex flex-wrap gap-2 mb-4">
          {PRESETS.map((p) => (
            <button key={p.label} onClick={() => applyPreset(p)}
              className="text-xs px-3 py-1.5 rounded-lg border border-zinc-200 hover:border-blue-400 hover:bg-blue-50 transition-colors">
              {p.label}
            </button>
          ))}
        </div>
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="sm:col-span-2">
            <label className="block text-xs font-medium text-zinc-500">接口地址</label>
            <input value={modelForm.base_url} onChange={(e) => setModelForm({ ...modelForm, base_url: e.target.value })}
              className="w-full border border-zinc-200 rounded px-2 py-1 text-sm font-mono" />
          </div>
          <div>
            <label className="block text-xs font-medium text-zinc-500">普通模型</label>
            <input value={modelForm.fast_model} onChange={(e) => setModelForm({ ...modelForm, fast_model: e.target.value })}
              className="w-full border border-zinc-200 rounded px-2 py-1 text-sm font-mono" />
          </div>
          <div>
            <label className="block text-xs font-medium text-zinc-500">推理模型</label>
            <input value={modelForm.reasoning_model} onChange={(e) => setModelForm({ ...modelForm, reasoning_model: e.target.value })}
              className="w-full border border-zinc-200 rounded px-2 py-1 text-sm font-mono" />
          </div>
        </div>
        <button onClick={handleModelSave} disabled={saving}
          className="mt-4 px-4 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50">
          保存模型配置
        </button>
      </div>

      <div className="bg-white rounded-xl border border-zinc-200 p-6">
        <h2 className="font-semibold text-zinc-700 mb-2">API Key</h2>
        <p className="text-sm text-zinc-500 mb-4">
          在 <a href="https://platform.deepseek.com" target="_blank" className="text-blue-600 hover:underline">platform.deepseek.com</a> 申请 API Key
        </p>

        {settings.has_key && (
          <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg flex items-center gap-2">
            <span className="w-2 h-2 bg-green-500 rounded-full" />
            <span className="text-sm text-green-700">已配置</span>
            <span className="text-sm text-green-600 ml-2 font-mono">{settings.masked_key}</span>
          </div>
        )}
        {!settings.has_key && (
          <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg flex items-center gap-2">
            <span className="w-2 h-2 bg-amber-500 rounded-full" />
            <span className="text-sm text-amber-700">未配置 API Key，LLM 功能不可用</span>
          </div>
        )}

        <label className="block text-sm font-medium text-zinc-600 mb-1">
          {settings.has_key ? "更换 API Key" : "填写 API Key"}
        </label>
        <div className="flex gap-3">
          <input
            type="password"
            value={keyInput}
            onChange={(e) => setKeyInput(e.target.value)}
            placeholder="sk-..."
            className="flex-1 border border-zinc-300 rounded-lg px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-blue-500"
            autoComplete="off"
          />
          <button
            onClick={handleSave}
            disabled={saving || !keyInput.trim()}
            className="px-5 py-2 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 disabled:opacity-50 whitespace-nowrap"
          >
            {saving ? "保存中..." : "保存"}
          </button>
        </div>
        {message && (
          <p className={`mt-3 text-sm ${message.includes("失败") ? "text-red-500" : "text-green-600"}`}>
            {message}
          </p>
        )}
        <p className="mt-4 text-xs text-zinc-400">Key 使用 Fernet 加密存储在本地，不会明文显示。</p>
      </div>
    </div>
  );
}
