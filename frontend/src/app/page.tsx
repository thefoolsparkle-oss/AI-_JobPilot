"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

const STEPS = [
  { step: "01", title: "录入履历", desc: "结构化保存教育、实习、项目经历，标记可写和不能写的内容。", href: "/profile" },
  { step: "02", title: "选择模板", desc: "从多套专业模板中选择，AI 只填内容不改布局。", href: "/templates" },
  { step: "03", title: "解析 JD", desc: "粘贴岗位描述，系统自动抽取结构化信息和隐藏要求。", href: "/jobs/parse" },
  { step: "04", title: "匹配评分", desc: "系统判断你与岗位的匹配度、优势、风险和推荐策略。", href: "/jobs/match" },
  { step: "05", title: "生成简历", desc: "基于模板+JD+履历生成岗位专用简历，支持 DOCX 导出。", href: "/resumes" },
  { step: "06", title: "投递材料", desc: "自动生成自我介绍、申请理由、HR 私信和面试问题。", href: "/applications" },
];

export default function Home() {
  const [hasKey, setHasKey] = useState<boolean | null>(null);

  useEffect(() => {
    fetch("/api/settings")
      .then((r) => r.json())
      .then((d) => setHasKey(d.has_key))
      .catch(() => {});
  }, []);

  return (
    <div>
      <section className="bg-gradient-to-br from-blue-600 to-indigo-700 text-white py-20">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-4">JobPilot</h1>
          <p className="text-xl text-blue-100 mb-2">AI 求职 Copilot — 基于 DeepSeek 的开源求职助手</p>
          <p className="text-blue-200 max-w-2xl mx-auto">
            从真实履历出发，主动发现岗位、解析 JD、匹配经历、生成稳定简历，辅助完成投递。
          </p>
        </div>
      </section>

      {hasKey === false && (
        <div className="bg-amber-50 border-b border-amber-200">
          <div className="max-w-4xl mx-auto px-6 py-3 flex items-center justify-between">
            <span className="text-sm text-amber-800">
              未配置 API Key，LLM 功能不可用。
            </span>
            <Link href="/settings" className="text-sm text-blue-600 hover:underline font-medium">
              去设置 →
            </Link>
          </div>
        </div>
      )}

      <section className="max-w-5xl mx-auto px-6 py-16">
        <h2 className="text-2xl font-bold text-center mb-10 text-zinc-800">求职工作流</h2>
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {STEPS.map((s) => (
            <Link
              key={s.step}
              href={s.href}
              className="group bg-white rounded-xl border border-zinc-200 p-6 hover:border-blue-300 hover:shadow-md transition-all"
            >
              <span className="text-3xl font-bold text-blue-100 group-hover:text-blue-200 transition-colors">{s.step}</span>
              <h3 className="text-lg font-semibold text-zinc-800 mt-2">{s.title}</h3>
              <p className="text-sm text-zinc-500 mt-1">{s.desc}</p>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}
