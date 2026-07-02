import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Brain, Sparkles, Target, RefreshCw, Trash2, FileText, Upload, Briefcase, ArrowRight,
} from 'lucide-react'
import Layout from '../components/Layout.jsx'
import { StatCard, Spinner, Chip } from '../components/ui.jsx'
import client from '../api/client.js'
import { LIFECYCLE_BADGE } from './Lifecycle.jsx'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([client.get('/dashboard/stats'), client.get('/lifecycle/logs?limit=6')])
      .then(([s, l]) => {
        setStats(s.data)
        setLogs(l.data)
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <Layout title="Dashboard" subtitle="Your career memory at a glance">
      {loading ? (
        <Spinner label="Loading your dashboard…" />
      ) : (
        <div className="space-y-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
            <StatCard icon={Brain} label="Memories remembered" value={stats.remembered_count} />
            <StatCard icon={Sparkles} label="Total generations" value={stats.generated_count} />
            <StatCard icon={RefreshCw} label="Improvements from feedback" value={stats.improved_count} />
            <StatCard icon={Trash2} label="Memories forgotten" value={stats.forgotten_count} accent="text-rose-500" />
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {/* quick actions */}
            <div className="card p-6 lg:col-span-2">
              <h2 className="text-base font-bold text-ink">Quick actions</h2>
              <p className="text-sm text-slate-500">Jump straight into the core flow.</p>
              <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
                <QuickAction to="/memory/upload" icon={Upload} title="Add memory" desc="Upload a resume or paste projects" />
                <QuickAction to="/generate" icon={Sparkles} title="Generate content" desc="Cover letter, answers & more" />
                <QuickAction to="/skill-gap" icon={Target} title="Skill gap analysis" desc="Match yourself to a JD" />
                <QuickAction to="/jobs" icon={Briefcase} title="Track applications" desc="Pipeline & linked docs" />
              </div>
            </div>

            {/* recent activity */}
            <div className="card p-6">
              <div className="flex items-center justify-between">
                <h2 className="text-base font-bold text-ink">Recent activity</h2>
                <Link to="/lifecycle" className="text-xs font-semibold text-primary-700 hover:underline">
                  View all
                </Link>
              </div>
              <div className="mt-4 space-y-3">
                {logs.length === 0 && <p className="text-sm text-slate-400">No activity yet.</p>}
                {logs.map((log) => {
                  const b = LIFECYCLE_BADGE[log.action_type] || LIFECYCLE_BADGE.GENERATED
                  return (
                    <div key={log.id} className="flex items-start gap-3">
                      <Chip tone={b.tone}>{log.action_type}</Chip>
                      <p className="flex-1 text-sm text-slate-600">{log.description}</p>
                    </div>
                  )
                })}
              </div>
            </div>
          </div>

          <div className="card flex items-center justify-between gap-4 p-5">
            <div className="flex items-center gap-3">
              <div className="grid h-10 w-10 place-items-center rounded-xl bg-primary-50 text-primary">
                <FileText size={18} />
              </div>
              <div>
                <p className="text-sm font-semibold text-ink">
                  {stats.total_memory_items} memories · {stats.total_generations} generations
                </p>
                <p className="text-xs text-slate-500">Cognee is holding your long-term career context.</p>
              </div>
            </div>
            <Link to="/memory/library" className="btn-ghost">
              Memory library <ArrowRight size={16} />
            </Link>
          </div>
        </div>
      )}
    </Layout>
  )
}

function QuickAction({ to, icon: Icon, title, desc }) {
  return (
    <Link
      to={to}
      className="group flex items-center gap-3 rounded-xl border border-slate-200 p-4 transition-colors hover:border-primary/40 hover:bg-primary-50/40"
    >
      <div className="grid h-10 w-10 place-items-center rounded-xl bg-primary-50 text-primary">
        <Icon size={18} />
      </div>
      <div className="flex-1">
        <p className="text-sm font-semibold text-ink">{title}</p>
        <p className="text-xs text-slate-500">{desc}</p>
      </div>
      <ArrowRight size={16} className="text-slate-300 transition-transform group-hover:translate-x-0.5 group-hover:text-primary" />
    </Link>
  )
}
