// Small shared UI atoms used across pages.
import { Loader2 } from 'lucide-react'

export function StatCard({ icon: Icon, label, value, accent = 'text-primary' }) {
  return (
    <div className="card flex items-center gap-4 p-5">
      <div className={`grid h-11 w-11 place-items-center rounded-xl bg-primary-50 ${accent}`}>
        <Icon size={20} />
      </div>
      <div>
        <p className="text-2xl font-extrabold leading-none text-ink">{value}</p>
        <p className="mt-1 text-xs font-medium text-slate-500">{label}</p>
      </div>
    </div>
  )
}

export function Spinner({ label = 'Working…' }) {
  return (
    <div className="flex items-center justify-center gap-2 py-10 text-slate-400">
      <Loader2 size={18} className="animate-spin" />
      <span className="text-sm font-medium">{label}</span>
    </div>
  )
}

export function EmptyState({ icon: Icon, title, hint, action }) {
  return (
    <div className="card flex flex-col items-center gap-3 px-6 py-14 text-center">
      {Icon && (
        <div className="grid h-12 w-12 place-items-center rounded-2xl bg-slate-100 text-slate-400">
          <Icon size={22} />
        </div>
      )}
      <div>
        <p className="font-semibold text-ink">{title}</p>
        {hint && <p className="mt-1 text-sm text-slate-500">{hint}</p>}
      </div>
      {action}
    </div>
  )
}

const CHIP_TONES = {
  green: 'bg-emerald-50 text-emerald-700',
  red: 'bg-rose-50 text-rose-700',
  amber: 'bg-amber-50 text-amber-700',
  violet: 'bg-primary-50 text-primary-700',
  slate: 'bg-slate-100 text-slate-600',
  blue: 'bg-blue-50 text-blue-700',
}

export function Chip({ tone = 'slate', children }) {
  return <span className={`chip ${CHIP_TONES[tone] || CHIP_TONES.slate}`}>{children}</span>
}

export function Field({ label, children, hint, required }) {
  return (
    <div>
      <label className="label">
        {label} {required && <span className="text-rose-500">*</span>}
      </label>
      {children}
      {hint && <p className="mt-1 text-xs text-slate-400">{hint}</p>}
    </div>
  )
}
