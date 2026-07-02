import { useEffect, useState } from 'react'
import { Brain, Search, RefreshCw, Trash2, Sparkles, History } from 'lucide-react'
import Layout from '../components/Layout.jsx'
import { Spinner, Chip, EmptyState } from '../components/ui.jsx'
import client from '../api/client.js'

export const LIFECYCLE_BADGE = {
  REMEMBERED: { tone: 'violet', icon: Brain },
  RECALLED: { tone: 'blue', icon: Search },
  IMPROVED: { tone: 'green', icon: RefreshCw },
  FORGOTTEN: { tone: 'red', icon: Trash2 },
  GENERATED: { tone: 'amber', icon: Sparkles },
}

function fmtTime(iso) {
  const d = new Date(iso)
  return d.toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

export default function Lifecycle() {
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    client.get('/lifecycle/logs?limit=200').then((r) => setLogs(r.data)).finally(() => setLoading(false))
  }, [])

  return (
    <Layout title="Memory Lifecycle" subtitle="Every remember · recall · improve · forget event">
      {loading ? (
        <Spinner label="Loading lifecycle…" />
      ) : logs.length === 0 ? (
        <EmptyState icon={History} title="No memory activity yet" hint="Upload a memory or generate content to see the timeline fill up." />
      ) : (
        <div className="card p-6">
          <div className="mb-5 flex flex-wrap gap-2">
            {Object.keys(LIFECYCLE_BADGE).map((k) => (
              <Chip key={k} tone={LIFECYCLE_BADGE[k].tone}>{k}</Chip>
            ))}
          </div>
          <ol className="relative space-y-5 border-l border-slate-200 pl-6">
            {logs.map((log) => {
              const b = LIFECYCLE_BADGE[log.action_type] || LIFECYCLE_BADGE.GENERATED
              const Icon = b.icon
              return (
                <li key={log.id} className="relative">
                  <span className="absolute -left-[31px] grid h-6 w-6 place-items-center rounded-full border border-slate-200 bg-white text-primary">
                    <Icon size={13} />
                  </span>
                  <div className="flex flex-wrap items-center gap-2">
                    <Chip tone={b.tone}>{log.action_type}</Chip>
                    <span className="text-xs text-slate-400">{fmtTime(log.created_at)}</span>
                  </div>
                  <p className="mt-1 text-sm text-slate-700">{log.description}</p>
                </li>
              )
            })}
          </ol>
        </div>
      )}
    </Layout>
  )
}
