"use client";

import Link from "next/link";
import { useAuth } from "@/lib/auth";

const NAV_ITEMS = [
  { label: "履历", href: "/profile" },
  { label: "模板", href: "/templates" },
  { label: "岗位", href: "/jobs" },
  { label: "简历", href: "/resumes" },
  { label: "投递", href: "/applications" },
  { label: "追踪", href: "/tracker" },
  { label: "助手", href: "/assistant" },
];

export default function NavBar() {
  const { user, loading, logout } = useAuth();

  return (
    <header className="bg-white border-b border-zinc-200 sticky top-0 z-50">
      <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
        <Link href="/" className="font-bold text-lg text-blue-600">
          JobPilot
        </Link>
        <nav className="flex items-center gap-6">
          {NAV_ITEMS.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-sm text-zinc-600 hover:text-blue-600 transition-colors"
            >
              {item.label}
            </Link>
          ))}
          <Link
            href="/settings"
            className="text-sm text-zinc-400 hover:text-zinc-600 transition-colors"
          >
            设置
          </Link>
          {loading ? (
            <span className="text-sm text-zinc-400">...</span>
          ) : user ? (
            <div className="flex items-center gap-3">
              <span className="text-sm text-zinc-500">{user.email}</span>
              <button
                onClick={logout}
                className="text-sm text-zinc-400 hover:text-red-500 transition-colors"
              >
                退出
              </button>
            </div>
          ) : (
            <Link
              href="/login"
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              登录
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}
