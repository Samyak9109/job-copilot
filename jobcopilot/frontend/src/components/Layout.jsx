import { useEffect, useState } from 'react'
import { Menu, LogOut, X } from 'lucide-react'
import Sidebar from './Sidebar.jsx'
import { useAuth } from '../auth/AuthContext.jsx'
import client from '../api/client.js'

export default function Layout({ title, subtitle, children }) {
  const { user, logout } = useAuth()
  const [open, setOpen] = useState(false)
  const [sys, setSys] = useState(null)

  useEffect(() => {
    client.get('/dashboard/system').then((r) => setSys(r.data)).catch(() => {})
  }, [])

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* desktop sidebar */}
      <div className="hidden lg:block">
        <Sidebar />
      </div>

      {/* mobile drawer */}
      {open && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/50" onClick={() => setOpen(false)} />
          <div className="absolute left-0 top-0 h-full">
            <Sidebar onNavigate={() => setOpen(false)} />
          </div>
          <button
            className="absolute right-4 top-4 rounded-lg bg-white p-2 text-slate-700"
            onClick={() => setOpen(false)}
            aria-label="Close menu"
          >
            <X size={18} />
          </button>
        </div>
      )}

      <div className="flex flex-1 flex-col overflow-hidden">
        <header className="flex items-center justify-between gap-3 border-b border-slate-200 bg-white px-5 py-3.5">
          <div className="flex items-center gap-3">
            <button
              className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 lg:hidden"
              onClick={() => setOpen(true)}
              aria-label="Open menu"
            >
              <Menu size={20} />
            </button>
            <div>
              <h1 className="text-lg font-bold leading-tight text-ink">{title}</h1>
              {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
            </div>
          </div>

          <div className="flex items-center gap-3">
            {sys && (
              <div className="hidden items-center gap-2 sm:flex">
                <Badge label={`memory: ${sys.memory_backend}`} />
                <Badge label={`llm: ${sys.llm_provider}`} />
              </div>
            )}
            <div className="flex items-center gap-2 rounded-xl border border-slate-200 py-1 pl-1 pr-2.5">
              <div className="grid h-7 w-7 place-items-center rounded-lg bg-primary text-xs font-bold text-white">
                {(user?.name || '?').slice(0, 1).toUpperCase()}
              </div>
              <span className="hidden text-sm font-semibold text-slate-700 sm:block">{user?.name}</span>
            </div>
            <button
              onClick={logout}
              className="rounded-xl p-2 text-slate-500 hover:bg-slate-100 hover:text-rose-600"
              aria-label="Log out"
              title="Log out"
            >
              <LogOut size={18} />
            </button>
          </div>
        </header>

        <main className="flex-1 overflow-y-auto px-5 py-6">
          <div className="mx-auto max-w-6xl">{children}</div>
        </main>
      </div>
    </div>
  )
}

function Badge({ label }) {
  return (
    <span className="chip border border-slate-200 bg-slate-50 text-slate-500 font-mono lowercase tracking-tight">
      {label}
    </span>
  )
}
