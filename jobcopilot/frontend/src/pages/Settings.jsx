import { useEffect, useState } from 'react'
import { User, Database, Cpu, LogOut } from 'lucide-react'
import Layout from '../components/Layout.jsx'
import { useAuth } from '../auth/AuthContext.jsx'
import client from '../api/client.js'

export default function Settings() {
  const { user, logout } = useAuth()
  const [sys, setSys] = useState(null)

  useEffect(() => {
    client.get('/dashboard/system').then((r) => setSys(r.data)).catch(() => {})
  }, [])

  return (
    <Layout title="Settings" subtitle="Account & system">
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="card p-6">
          <h2 className="flex items-center gap-2 text-base font-bold text-ink"><User size={18} className="text-primary" /> Account</h2>
          <dl className="mt-4 space-y-3 text-sm">
            <Row label="Name" value={user?.name} />
            <Row label="Email" value={user?.email} />
            <Row label="Member since" value={user?.created_at ? new Date(user.created_at).toLocaleDateString() : '—'} />
          </dl>
          <button onClick={logout} className="btn-ghost mt-5 text-rose-600 hover:bg-rose-50">
            <LogOut size={16} /> Log out
          </button>
        </div>

        <div className="card p-6">
          <h2 className="text-base font-bold text-ink">System</h2>
          <p className="text-xs text-slate-500">Which engines are powering your session.</p>
          <div className="mt-4 space-y-3">
            <SysRow icon={Database} label="Memory backend" value={sys?.memory_backend || '…'}
              hint="Cognee (real SDK) or the local semantic store fallback." />
            <SysRow icon={Cpu} label="LLM provider" value={sys?.llm_provider || '…'}
              hint="Gemini / OpenRouter, or the offline deterministic generator." />
          </div>
        </div>
      </div>
    </Layout>
  )
}

function Row({ label, value }) {
  return (
    <div className="flex justify-between border-b border-slate-100 pb-2">
      <dt className="text-slate-500">{label}</dt>
      <dd className="font-semibold text-ink">{value}</dd>
    </div>
  )
}

function SysRow({ icon: Icon, label, value, hint }) {
  return (
    <div className="flex items-start gap-3 rounded-xl bg-slate-50 p-3">
      <div className="grid h-9 w-9 place-items-center rounded-lg bg-white text-primary"><Icon size={16} /></div>
      <div>
        <p className="text-sm font-semibold text-ink">{label}: <span className="font-mono text-primary-700">{value}</span></p>
        <p className="text-xs text-slate-500">{hint}</p>
      </div>
    </div>
  )
}
