"use client";

export function LoadingSpinner({ text = "加载中..." }: { text?: string }) {
  return (
    <div className="max-w-4xl mx-auto px-6 py-12 flex items-center justify-center gap-3 text-zinc-500">
      <svg className="animate-spin h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
      </svg>
      <span className="text-sm">{text}</span>
    </div>
  );
}

export function ErrorBanner({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="max-w-4xl mx-auto px-6 py-4">
      <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center justify-between">
        <span className="text-sm text-red-700">{message}</span>
        {onRetry && (
          <button onClick={onRetry} className="text-sm text-red-600 hover:underline font-medium">
            重试
          </button>
        )}
      </div>
    </div>
  );
}

export function EmptyState({ message = "暂无数据" }: { message?: string }) {
  return (
    <div className="text-center py-12">
      <p className="text-sm text-zinc-400">{message}</p>
    </div>
  );
}

export function PageHeader({ title, subtitle }: { title: string; subtitle?: string }) {
  return (
    <div className="mb-6">
      <h1 className="text-2xl font-bold text-zinc-800">{title}</h1>
      {subtitle && <p className="text-zinc-500 mt-1">{subtitle}</p>}
    </div>
  );
}

export function Modal({ open, onClose, title, children }: { open: boolean; onClose: () => void; title: string; children: React.ReactNode }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-lg max-h-[85vh] overflow-y-auto">
        <h2 className="text-lg font-bold mb-4">{title}</h2>
        {children}
      </div>
    </div>
  );
}
