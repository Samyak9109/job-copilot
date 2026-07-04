import { useState } from 'react'
import { MessagesSquare, ExternalLink, Lightbulb } from 'lucide-react'
import Layout from '../components/Layout.jsx'
import { Field, Spinner, Chip } from '../components/ui.jsx'
import client, { errMessage } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'

const CAT_TONE = {
  technical: 'blue',
  behavioral: 'green',
  'company-fit': 'violet',
  'project-deep-dive': 'amber',
}

export default function InterviewPrep() {
  const toast = useToast()
  const [form, setForm] = useState({ company: '', role: '', job_description: '' })
  const [busy, setBusy] = useState(false)
  const [data, setData] = useState(null)

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setData(null)
    try {
      const res = await client.post('/interview/prep', form)
      setData(res.data)
    } catch (err) {
      toast.error(errMessage(err, 'Interview prep failed'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <Layout title="Interview Prep" subtitle="Real candidate-reported questions, grounded by search">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        <form onSubmit={submit} className="card space-y-4 p-6 lg:col-span-2">
          <Field label="Company" required>
            <input className="input" required placeholder="e.g. Razorpay"
              value={form.company} onChange={(e) => setForm({ ...form, company: e.target.value })} />
          </Field>
          <Field label="Role" required>
            <input className="input" required placeholder="e.g. Full-stack Engineer"
              value={form.role} onChange={(e) => setForm({ ...form, role: e.target.value })} />
          </Field>
          <Field label="Job description" hint="Optional — improves personalisation.">
            <textarea className="input min-h-[140px]"
              value={form.job_description} onChange={(e) => setForm({ ...form, job_description: e.target.value })} />
          </Field>
          <button className="btn-primary w-full" disabled={busy}>
            <MessagesSquare size={16} /> {busy ? 'Preparing…' : 'Prepare questions'}
          </button>
        </form>

        <div className="lg:col-span-3">
          {busy ? (
            <div className="card"><Spinner label="Recalling memory + searching real interviews…" /></div>
          ) : data ? (
            <div className="space-y-4">
              {data.questions.map((q, i) => (
                <div key={i} className="card p-5">
                  <div className="flex items-start justify-between gap-3">
                    <p className="font-semibold text-ink">{q.question}</p>
                    <Chip tone={CAT_TONE[q.category] || 'slate'}>{q.category}</Chip>
                  </div>
                  <p className="mt-2 flex items-start gap-1.5 text-sm text-slate-600">
                    <Lightbulb size={15} className="mt-0.5 shrink-0 text-amber-500" />
                    <span>{q.suggested_focus}</span>
                  </p>
                  <p className="mt-2 text-xs font-medium text-slate-400">
                    {q.grounding === 'commonly-reported' ? '● Commonly reported by candidates' : '○ Likely, based on role'}
                  </p>
                </div>
              ))}

              {data.sources?.length > 0 && (
                <div className="card p-5">
                  <h3 className="text-sm font-bold text-ink">Grounded in these sources</h3>
                  <ul className="mt-2 space-y-2">
                    {data.sources.map((s, i) => (
                      <li key={i}>
                        <a href={s.url} target="_blank" rel="noreferrer"
                          className="flex items-center gap-1.5 text-sm font-medium text-primary-700 hover:underline">
                          <ExternalLink size={13} /> {s.title || s.url}
                        </a>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ) : (
            <div className="card grid h-full place-items-center p-10 text-center text-slate-500">
              <div>
                <div className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-primary-50 text-primary">
                  <MessagesSquare size={22} />
                </div>
                <p className="mt-3 font-semibold text-ink">Your question set appears here</p>
                <p className="text-sm">Grounded in real candidate reports when a Tavily key is set.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
