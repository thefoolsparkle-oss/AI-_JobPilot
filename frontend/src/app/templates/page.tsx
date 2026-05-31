"use client";

import { useState, useEffect } from "react";

const API_BASE = "/api";

interface Template {
  id: number;
  name: string;
  description: string;
  style: string;
  template_file: string;
}

const STYLE_LABELS: Record<string, string> = {
  cn_tech: "技术实习",
  cn_ai_product: "AI产品",
  cn_operation: "产品运营",
};

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Template | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/templates`)
      .then((r) => r.json())
      .then((data) => {
        setTemplates(data);
        if (data.length > 0) setSelected(data[0]);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="max-w-4xl mx-auto px-6 py-12 text-zinc-500">加载中...</div>;

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">
      <h1 className="text-2xl font-bold text-zinc-800 mb-2">模板系统</h1>
      <p className="text-zinc-500 mb-8">选择简历模板。模板决定栏目顺序和视觉风格，AI 只负责填充内容。</p>

      <div className="grid gap-4 sm:grid-cols-3 mb-8">
        {templates.map((t) => (
          <button
            key={t.id}
            onClick={() => setSelected(t)}
            className={`text-left rounded-xl border p-5 transition-all ${
              selected?.id === t.id
                ? "border-blue-500 ring-2 ring-blue-200 bg-blue-50"
                : "border-zinc-200 bg-white hover:border-zinc-300"
            }`}
          >
            <span className="text-xs font-medium text-blue-600 bg-blue-100 px-2 py-0.5 rounded">
              {STYLE_LABELS[t.style] || t.style}
            </span>
            <h3 className="font-semibold text-zinc-800 mt-2">{t.name}</h3>
            <p className="text-sm text-zinc-500 mt-1">{t.description}</p>
          </button>
        ))}
      </div>

      {selected && (
        <div className="bg-white rounded-xl border border-zinc-200 p-6">
          <h2 className="font-semibold text-zinc-800 mb-4">模板预览 — {selected.name}</h2>
          <div className="border border-zinc-300 rounded-lg bg-zinc-50 p-8 min-h-[500px]">
            <div className="text-center mb-6">
              <div className="text-xl font-bold text-zinc-800">姓名</div>
              <div className="text-xs text-zinc-400 mt-1">电话 | 邮箱 | 城市</div>
              <div className="text-xs text-zinc-400">GitHub | LinkedIn</div>
            </div>

            {selected.style === "cn_tech" && <TechPreview />}
            {selected.style === "cn_ai_product" && <AIProductPreview />}
            {selected.style === "cn_operation" && <OperationPreview />}
          </div>
          <p className="text-xs text-zinc-400 mt-3">以上为模板结构预览。实际简历将由 AI 根据岗位 JD 填充内容，使用 python-docx 渲染为 DOCX/PDF。</p>
        </div>
      )}
    </div>
  );
}

function SectionPreview({ title, lines }: { title: string; lines: string[] }) {
  return (
    <div className="mb-4 text-left">
      <div className="text-sm font-bold text-blue-700 border-b border-blue-200 pb-1 mb-2">{title}</div>
      {lines.map((line, i) => (
        <p key={i} className="text-xs text-zinc-400 leading-relaxed ml-2">{line}</p>
      ))}
    </div>
  );
}

function TechPreview() {
  return (
    <div className="max-w-md mx-auto text-left">
      <SectionPreview title="教育背景" lines={["学校 · 学位 · 专业 · GPA", "时间范围"]} />
      <SectionPreview title="实习经历" lines={["公司 | 职位 | 时间", "- 工作内容与成果 bullet point", "- 技术栈与量化指标"]} />
      <SectionPreview title="项目经历" lines={["项目名称 | 技术栈 | 时间", "- 项目功能与角色", "- 技术亮点与规模"]} />
      <SectionPreview title="技能" lines={["编程语言: Python, Go, TypeScript", "工具: Docker, Git, Linux", "语言: 英语 (流利)"]} />
    </div>
  );
}

function AIProductPreview() {
  return (
    <div className="max-w-md mx-auto text-left">
      <SectionPreview title="求职意向" lines={["AI 产品实习生 · 远程/上海 · 2026年7月起"]} />
      <SectionPreview title="专业优势" lines={["具备 AI 工具使用与产品原型设计经验，熟悉 LLM 应用和 Agent 架构..."]} />
      <SectionPreview title="项目经历" lines={["项目名称 | 角色 | 技术栈", "- 产品方案与功能设计", "- 用户研究与数据分析"]} />
      <SectionPreview title="实习经历" lines={["公司 | 职位 | 时间", "- 需求调研与 PRD 撰写"]} />
      <SectionPreview title="教育背景" lines={["学校 · 学位 · 专业"]} />
      <SectionPreview title="技能" lines={["产品工具: Figma, Axure, Notion", "数据: Python, SQL, Excel", "语言: 英语 (流利)"]} />
    </div>
  );
}

function OperationPreview() {
  return (
    <div className="max-w-md mx-auto text-left">
      <SectionPreview title="求职意向" lines={["产品运营实习生 · 上海 · 2026年7月起"]} />
      <SectionPreview title="实习经历" lines={["公司 | 运营实习生 | 时间", "- 内容运营与用户增长", "- 数据分析与报告"]} />
      <SectionPreview title="项目经历" lines={["项目名称 | 角色", "- 社群运营与活动策划"]} />
      <SectionPreview title="教育背景" lines={["学校 · 学位 · 专业"]} />
      <SectionPreview title="技能与工具" lines={["运营工具: 公众号后台, 秀米, Canva", "数据: Excel, SQL, Google Analytics", "语言: 英语 (流利)"]} />
    </div>
  );
}
