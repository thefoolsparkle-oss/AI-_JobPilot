import Link from "next/link";

export default function JobsPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-12">
      <h1 className="text-2xl font-bold text-zinc-800">岗位管理</h1>
      <p className="text-zinc-500 mt-2">解析 JD、匹配评分、管理岗位。</p>
      <div className="mt-8 p-8 border border-dashed border-zinc-300 rounded-xl text-center text-zinc-400">
        岗位功能将在 Step 4-5 中实现
      </div>
      <div className="flex gap-4 mt-4">
        <Link href="/jobs/parse" className="text-blue-600 hover:underline text-sm">JD 解析</Link>
        <Link href="/jobs/match" className="text-blue-600 hover:underline text-sm">匹配评分</Link>
      </div>
    </div>
  );
}
