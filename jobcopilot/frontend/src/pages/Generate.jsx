import { useEffect, useState } from 'react'
import { Sparkles, Copy, Check, ThumbsUp } from 'lucide-react'
import Layout from '../components/Layout.jsx'
import { Field, Spinner } from '../components/ui.jsx'
import client, { errMessage } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'

const OUTPUT_TYPES = [
  ['cover_letter', 'Cover Letter'],
  ['interview_answer', 'Interview Answer'],
  ['resume_summary', 'Resume Summary'],
  ['recruiter_message', 'Recruiter Message'],
]

const FEEDBACK = [
  ['good', 'Good'],
  ['too_generic', 'Too generic'],
  ['too_long', 'Too long'],
  ['too_short', 'Too short'],
  ['missing_project_details', 'Missing projects'],
  ['selected', 'Selected ✓'],
  ['rejected', 'Rejected'],
]

export default function Generate() {
  const toast = useToast()
  const [jobs, setJobs] = useState([])
  const [form, setForm] = useState({ output_type: 'cover_letter', job_description: '', extra_instructions: '', job_id: '' })
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [copied, setCopied] = useState(false)
  const [feedbackSent, setFeedbackSent] = useState(false)

  useEffect(() => {
    client.get('/jobs').then((r) => setJobs(r.data)).catch(() => {})
  }, [])

  function pickJob(id) {
    const job = jobs.find((j) => String(j.id) === id)
    setForm((f) => ({ ...f, job_id: id, job_description: job?.jd_text || f.job_description }))
  }

  async function generate(e) {
    e.preventDefault()
    setBusy(true)
    setResult(null)
    setFeedbackSent(false)
    try {
      const payload = {
        output_type: form.output_type,
        job_description: form.job_description,
        extra_instructions: form.extra_instructions,
        job_id: form.job_id ? Number(form.job_id) : null,
      }
      const res = await client.post('/generate', payload)
      setResult(res.data)
    } catch (err) {
      toast.error(errMessage(err, 'Generation failed'))
    } finally {
      setBusy(false)
    }
  }

  async function copy() {
    await navigator.clipboard.writeText(result.output_text || '')
    setCopied(true)
    setTimeout(() => setCopied(false), 1800)
  }

  async function sendFeedback(rating) {
    try {
      await client.post('/feedback', { generation_id: result.generation_id, rating, feedback_text: '' })
      setFeedbackSent(true)
      toast.success('Thanks — Cognee improved your memory from that feedback.')
    } catch (err) {
      toast.error(errMessage(err, 'Could not send feedback'))
    }
  }

  return (
    <Layout title="Generate" subtitle="Recall your memory → LangChain → polished output">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        <form onSubmit={generate} className="card space-y-5 p-6 lg:col-span-2">
          <Field label="Output type" required>
            <select className="input" value={form.output_type}
              onChange={(e) => setForm({ ...form, output_type: e.target.value })}>
              {OUTPUT_TYPES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </Field>

          {jobs.length > 0 && (
            <Field label="Link to application" hint="Optional — prefills the JD and attaches the result.">
              <select className="input" value={form.job_id} onChange={(e) => pickJob(e.target.value)}>
                <option value="">None</option>
                {jobs.map((j) => <option key={j.id} value={j.id}>{j.company} — {j.title}</option>)}
              </select>
            </Field>
          )}

          <Field label="Job description" hint="Paste the role you're targeting.">
            <textarea className="input min-h-[150px]" placeholder="Paste the job description here…"
              value={form.job_description} onChange={(e) => setForm({ ...form, job_description: e.target.value })} />
          </Field>

          <Field label="Extra instructions" hint="e.g. keep it under 200 words, emphasise leadership.">
            <input className="input" value={form.extra_instructions}
              onChange={(e) => setForm({ ...form, extra_instructions: e.target.value })} />
          </Field>

          <button className="btn-primary w-full" disabled={busy}>
            <Sparkles size={16} /> {busy ? 'Generating…' : 'Generate'}
          </button>
        </form>

        <div className="lg:col-span-3">
          {busy ? (
            <div className="card"><Spinner label="Recalling memory & generating…" /></div>
          ) : result ? (
            <div className="card p-6">
              <div className="flex items-center justify-between">
                <h2 className="text-base font-bold text-ink">Result</h2>
                <button onClick={copy} className="btn-ghost !py-1.5 !px-3 text-xs">
                  {copied ? <Check size={14} /> : <Copy size={14} />} {copied ? 'Copied' : 'Copy'}
                </button>
              </div>

              <div className="mt-4 whitespace-pre-wrap rounded-xl bg-slate-50 p-4 text-sm leading-relaxed text-slate-800">
                {result.output_text}
              </div>

              <details className="mt-3 text-xs text-slate-500">
                <summary className="cursor-pointer font-semibold">Recalled memory used</summary>
                <p className="mt-2 whitespace-pre-wrap rounded-lg bg-slate-50 p-3">{result.recalled_context_preview}</p>
              </details>

              <div className="mt-5 border-t border-slate-100 pt-4">
                <p className="mb-2 flex items-center gap-1.5 text-sm font-semibold text-ink">
                  <ThumbsUp size={15} /> How was this? Feedback improves your memory.
                </p>
                {feedbackSent ? (
                  <p className="text-sm font-medium text-emerald-600">Feedback recorded — memory improved.</p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {FEEDBACK.map(([v, l]) => (
                      <button key={v} onClick={() => sendFeedback(v)} className="btn-soft !py-1.5 !px-3 text-xs">
                        {l}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="card grid h-full place-items-center p-10 text-center">
              <div>
                <div className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-primary-50 text-primary">
                  <Sparkles size={22} />
                </div>
                <p className="mt-3 font-semibold text-ink">Your generated content appears here</p>
                <p className="text-sm text-slate-500">Pick an output type and hit generate.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}
