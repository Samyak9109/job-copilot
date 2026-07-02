import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, Briefcase, X } from 'lucide-react'
import Layout from '../components/Layout.jsx'
import { Field, Spinner, Chip, EmptyState } from '../components/ui.jsx'
import client, { errMessage } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'

export const STATUS_META = {
  applied: { label: 'Applied', tone: 'blue' },
  interview: { label: 'Interview', tone: 'amber' },
  offer: { label: 'Offer', tone: 'green' },
  rejected: { label: 'Rejected', tone: 'red' },
}
const COLUMNS = ['applied', 'interview', 'offer', 'rejected']

export default function Jobs() {
  const toast = useToast()
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)

  function load() {
    client.get('/jobs').then((r) => setJobs(r.data)).finally(() => setLoading(false))
  }
  useEffect(load, [])

  async function create(payload) {
    try {
      await client.post('/jobs', payload)
      toast.success('Application added.')
      setShowForm(false)
      load()
    } catch (err) {
      toast.error(errMessage(err, 'Could not add application'))
    }
  }

  return (
    <Layout title="Applications" subtitle="Track every job through the pipeline">
      <div className="mb-5 flex items-center justify-between">
        <p className="text-sm text-slate-500">{jobs.length} application{jobs.length === 1 ? '' : 's'}</p>
        <button className="btn-primary" onClick={() => setShowForm(true)}><Plus size={16} /> New application</button>
      </div>

      {loading ? (
        <Spinner label="Loading applications…" />
      ) : jobs.length === 0 ? (
        <EmptyState icon={Briefcase} title="No applications yet"
          hint="Add a job to track its status and attach generated documents."
          action={<button className="btn-primary" onClick={() => setShowForm(true)}><Plus size={16} /> New application</button>} />
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
          {COLUMNS.map((col) => {
            const items = jobs.filter((j) => j.status === col)
            return (
              <div key={col} className="rounded-2xl bg-slate-100/70 p-3">
                <div className="mb-3 flex items-center justify-between px-1">
                  <Chip tone={STATUS_META[col].tone}>{STATUS_META[col].label}</Chip>
                  <span className="text-xs font-semibold text-slate-400">{items.length}</span>
                </div>
                <div className="space-y-2.5">
                  {items.map((job) => (
                    <Link key={job.id} to={`/jobs/${job.id}`} className="block rounded-xl bg-white p-3.5 shadow-card transition-shadow hover:shadow-md">
                      <p className="truncate font-semibold text-ink">{job.title}</p>
                      <p className="truncate text-sm text-slate-500">{job.company}</p>
                      <p className="mt-1 text-[11px] text-slate-400">
                        {new Date(job.applied_date).toLocaleDateString()}
                      </p>
                    </Link>
                  ))}
                  {items.length === 0 && <p className="px-1 py-2 text-xs text-slate-400">Empty</p>}
                </div>
              </div>
            )
          })}
        </div>
      )}

      {showForm && <NewJobModal onClose={() => setShowForm(false)} onCreate={create} />}
    </Layout>
  )
}

function NewJobModal({ onClose, onCreate }) {
  const [form, setForm] = useState({ company: '', title: '', jd_text: '', status: 'applied' })
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="card relative z-10 w-full max-w-lg p-6">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-bold text-ink">New application</h2>
          <button onClick={onClose} className="rounded-lg p-1.5 text-slate-400 hover:bg-slate-100" aria-label="Close"><X size={18} /></button>
        </div>
        <form onSubmit={(e) => { e.preventDefault(); onCreate({ ...form }) }} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Field label="Company" required>
              <input className="input" required value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} />
            </Field>
            <Field label="Title" required>
              <input className="input" required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            </Field>
          </div>
          <Field label="Status">
            <select className="input" value={form.status} onChange={(e) => setForm({ ...form, status: e.target.value })}>
              {COLUMNS.map((c) => <option key={c} value={c}>{STATUS_META[c].label}</option>)}
            </select>
          </Field>
          <Field label="Job description" hint="Reused across generation & skill-gap.">
            <textarea className="input min-h-[120px]" value={form.jd_text} onChange={(e) => setForm({ ...form, jd_text: e.target.value })} />
          </Field>
          <div className="flex justify-end gap-2">
            <button type="button" onClick={onClose} className="btn-ghost">Cancel</button>
            <button className="btn-primary">Add application</button>
          </div>
        </form>
      </div>
    </div>
  )
}
