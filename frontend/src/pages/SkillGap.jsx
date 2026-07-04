import { useEffect, useState } from 'react'
import { Target, CheckCircle2, XCircle, FolderGit2, GraduationCap, BarChart3 } from 'lucide-react'
import Layout from '../components/Layout.jsx'
import { Field, Spinner, Chip } from '../components/ui.jsx'
import client, { errMessage } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'
import { selectedJobPatch } from '../utils/jobs.js'

export default function SkillGap() {
  const toast = useToast()
  const [jobs, setJobs] = useState([])
  const [form, setForm] = useState({ job_description: '', job_id: '' })
  const [busy, setBusy] = useState(false)
  const [result, setResult] = useState(null)
  const [agg, setAgg] = useState(null)

  function loadAggregate() {
    client.get('/analyze/skill-gap/aggregate').then((r) => setAgg(r.data)).catch(() => {})
  }
  useEffect(() => {
    client.get('/jobs').then((r) => setJobs(r.data)).catch(() => {})
    loadAggregate()
  }, [])

  async function analyze(e) {
    e.preventDefault()
    setBusy(true)
    setResult(null)
    try {
      const res = await client.post('/generate', {
        output_type: 'skill_gap_analysis',
        job_description: form.job_description,
        job_id: form.job_id ? Number(form.job_id) : null,
      })
      setResult(res.data.structured)
      loadAggregate()
    } catch (err) {
      toast.error(errMessage(err, 'Analysis failed'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <Layout title="Skill Gap Analysis" subtitle="Match your memory against a job — and spot recurring gaps">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-5">
        <form onSubmit={analyze} className="card space-y-4 p-6 lg:col-span-2">
          {jobs.length > 0 && (
            <Field label="Link to application" hint="Optional — prefills the JD.">
              <select className="input" value={form.job_id}
                onChange={(e) => {
                  setForm(selectedJobPatch(jobs, e.target.value, form.job_description))
                }}>
                <option value="">None</option>
                {jobs.map((j) => <option key={j.id} value={j.id}>{j.company} — {j.title}</option>)}
              </select>
            </Field>
          )}
          <Field label="Job description" required>
            <textarea className="input min-h-[220px]" required placeholder="Paste the job description…"
              value={form.job_description} onChange={(e) => setForm({ ...form, job_description: e.target.value })} />
          </Field>
          <button className="btn-primary w-full" disabled={busy}>
            <Target size={16} /> {busy ? 'Analyzing…' : 'Analyze skill gap'}
          </button>
        </form>

        <div className="space-y-6 lg:col-span-3">
          {busy ? (
            <div className="card"><Spinner label="Recalling skills & comparing…" /></div>
          ) : result ? (
            <ResultCards r={result} />
          ) : (
            <div className="card grid place-items-center p-10 text-center text-slate-500">
              <div>
                <div className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-primary-50 text-primary">
                  <Target size={22} />
                </div>
                <p className="mt-3 font-semibold text-ink">Analysis results appear here</p>
              </div>
            </div>
          )}

          {agg && agg.analyses > 0 && <AggregateChart agg={agg} />}
        </div>
      </div>
    </Layout>
  )
}

function ResultCards({ r }) {
  return (
    <div className="space-y-4">
      <div className="card flex items-center justify-between p-5">
        <div>
          <p className="text-sm font-medium text-slate-500">Match score</p>
          <p className="text-3xl font-extrabold text-ink">{r.score}<span className="text-lg text-slate-400">/100</span></p>
        </div>
        <div className="max-w-xs text-right">
          <Chip tone={r.score >= 70 ? 'green' : r.score >= 40 ? 'amber' : 'red'}>{r.recommendation}</Chip>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <SkillList icon={CheckCircle2} tone="text-emerald-600" title="Matched skills" items={r.matched_skills} chip="green" />
        <SkillList icon={XCircle} tone="text-rose-500" title="Missing skills" items={r.missing_skills} chip="red" />
      </div>

      <div className="card p-5">
        <h3 className="flex items-center gap-2 text-sm font-bold text-ink"><FolderGit2 size={16} className="text-primary" /> Relevant projects</h3>
        <ul className="mt-2 list-disc space-y-1 pl-5 text-sm text-slate-600">
          {r.relevant_projects.map((p, i) => <li key={i}>{p}</li>)}
        </ul>
      </div>

      <div className="card p-5">
        <h3 className="flex items-center gap-2 text-sm font-bold text-ink"><GraduationCap size={16} className="text-primary" /> Learning plan</h3>
        <p className="mt-2 text-sm text-slate-600">{r.learning_plan}</p>
        {r.resume_keywords?.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {r.resume_keywords.map((k, i) => <Chip key={i} tone="violet">{k}</Chip>)}
          </div>
        )}
      </div>
    </div>
  )
}

function SkillList({ icon: Icon, tone, title, items, chip }) {
  return (
    <div className="card p-5">
      <h3 className={`flex items-center gap-2 text-sm font-bold text-ink`}><Icon size={16} className={tone} /> {title}</h3>
      <div className="mt-3 flex flex-wrap gap-1.5">
        {items.length === 0 ? <p className="text-sm text-slate-400">None</p> : items.map((s, i) => <Chip key={i} tone={chip}>{s}</Chip>)}
      </div>
    </div>
  )
}

function AggregateChart({ agg }) {
  const max = Math.max(1, ...agg.recurring_missing.map((s) => s.count))
  return (
    <div className="card p-5">
      <h3 className="flex items-center gap-2 text-sm font-bold text-ink">
        <BarChart3 size={16} className="text-primary" /> Recurring skill gaps
        <span className="text-xs font-normal text-slate-400">across {agg.analyses} analyses · avg score {agg.average_score}</span>
      </h3>
      {agg.recurring_missing.length === 0 ? (
        <p className="mt-3 text-sm text-slate-400">No recurring gaps yet — run a few analyses.</p>
      ) : (
        <div className="mt-4 space-y-2.5">
          {agg.recurring_missing.map((s) => (
            <div key={s.skill} className="flex items-center gap-3">
              <span className="w-28 shrink-0 truncate text-right text-xs font-medium text-slate-600">{s.skill}</span>
              <div className="h-5 flex-1 overflow-hidden rounded-full bg-slate-100">
                <div className="h-full rounded-full bg-gradient-to-r from-primary to-accent"
                  style={{ width: `${(s.count / max) * 100}%` }} />
              </div>
              <span className="w-6 text-xs font-bold text-slate-500">{s.count}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
