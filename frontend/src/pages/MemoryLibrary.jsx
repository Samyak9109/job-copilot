import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Trash2, Library, Plus } from 'lucide-react'
import Layout from '../components/Layout.jsx'
import { Spinner, Chip, EmptyState } from '../components/ui.jsx'
import client, { errMessage } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'

const TYPE_TONE = {
  resume: 'violet',
  project: 'blue',
  job_description: 'amber',
  interview_answer: 'green',
  recruiter_note: 'slate',
  feedback: 'green',
  other: 'slate',
}

export default function MemoryLibrary() {
  const toast = useToast()
  const [items, setItems] = useState([])
  const [loading, setLoading] = useState(true)
  const [confirmId, setConfirmId] = useState(null)

  function load() {
    client.get('/memory/items').then((r) => setItems(r.data)).finally(() => setLoading(false))
  }
  useEffect(load, [])

  async function forget(id) {
    try {
      await client.delete(`/memory/items/${id}`)
      toast.success('Memory forgotten.')
      setItems((prev) => prev.filter((i) => i.id !== id))
    } catch (err) {
      toast.error(errMessage(err, 'Could not forget memory'))
    } finally {
      setConfirmId(null)
    }
  }

  return (
    <Layout title="Memory Library" subtitle="Everything Cognee remembers about you">
      {loading ? (
        <Spinner label="Loading memories…" />
      ) : items.length === 0 ? (
        <EmptyState
          icon={Library}
          title="No memories yet"
          hint="Add your resume, projects and job descriptions to build your career memory."
          action={<Link to="/memory/upload" className="btn-primary"><Plus size={16} /> Add memory</Link>}
        />
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {items.map((item) => (
            <div key={item.id} className="card flex flex-col p-5">
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                  <h3 className="truncate font-bold text-ink">{item.title}</h3>
                  <div className="mt-1.5 flex flex-wrap items-center gap-2">
                    <Chip tone={TYPE_TONE[item.memory_type] || 'slate'}>{item.memory_type}</Chip>
                    <span className="text-xs text-slate-400">{item.source_type}</span>
                    {item.source_filename && (
                      <span className="truncate text-xs text-slate-400">· {item.source_filename}</span>
                    )}
                  </div>
                </div>
                {confirmId === item.id ? (
                  <div className="flex shrink-0 items-center gap-1.5">
                    <button onClick={() => forget(item.id)} className="rounded-lg bg-rose-600 px-2.5 py-1.5 text-xs font-semibold text-white hover:bg-rose-700">
                      Forget
                    </button>
                    <button onClick={() => setConfirmId(null)} className="rounded-lg px-2 py-1.5 text-xs font-semibold text-slate-500 hover:bg-slate-100">
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button onClick={() => setConfirmId(item.id)} aria-label="Forget memory"
                    className="shrink-0 rounded-lg p-2 text-slate-400 hover:bg-rose-50 hover:text-rose-600">
                    <Trash2 size={16} />
                  </button>
                )}
              </div>
              <p className="mt-3 line-clamp-4 text-sm text-slate-600">{item.content_preview}</p>
            </div>
          ))}
        </div>
      )}
    </Layout>
  )
}
