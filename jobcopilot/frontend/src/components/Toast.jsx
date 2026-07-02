import { createContext, useCallback, useContext, useState } from 'react'
import { CheckCircle2, XCircle, Info, X } from 'lucide-react'

const ToastCtx = createContext(null)
export const useToast = () => useContext(ToastCtx)

const ICONS = {
  success: CheckCircle2,
  error: XCircle,
  info: Info,
}
const TONES = {
  success: 'border-emerald-200 bg-emerald-50 text-emerald-800',
  error: 'border-rose-200 bg-rose-50 text-rose-800',
  info: 'border-slate-200 bg-white text-slate-800',
}

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const dismiss = useCallback((id) => setToasts((t) => t.filter((x) => x.id !== id)), [])

  const push = useCallback(
    (message, type = 'info') => {
      const id = Math.random().toString(36).slice(2)
      setToasts((t) => [...t, { id, message, type }])
      setTimeout(() => dismiss(id), 4000)
    },
    [dismiss],
  )

  const toast = {
    success: (m) => push(m, 'success'),
    error: (m) => push(m, 'error'),
    info: (m) => push(m, 'info'),
  }

  return (
    <ToastCtx.Provider value={toast}>
      {children}
      <div
        className="fixed bottom-5 right-5 z-[1000] flex w-full max-w-sm flex-col gap-2"
        role="region"
        aria-live="polite"
      >
        {toasts.map((t) => {
          const Icon = ICONS[t.type]
          return (
            <div
              key={t.id}
              className={`flex items-start gap-3 rounded-xl border px-4 py-3 shadow-card ${TONES[t.type]}`}
            >
              <Icon size={18} className="mt-0.5 shrink-0" />
              <p className="text-sm font-medium leading-snug flex-1">{t.message}</p>
              <button onClick={() => dismiss(t.id)} aria-label="Dismiss" className="cursor-pointer opacity-60 hover:opacity-100">
                <X size={16} />
              </button>
            </div>
          )
        })}
      </div>
    </ToastCtx.Provider>
  )
}
