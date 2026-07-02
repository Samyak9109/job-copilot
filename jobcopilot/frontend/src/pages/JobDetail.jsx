import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { ArrowLeft, Trash2, FileText } from 'lucide-react'
import Layout from '../components/Layout.jsx'
import { Spinner, Chip } from '../components/ui.jsx'
import client, { errMessage } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'
import { STATUS_META } from './Jobs.jsx'

const COLUMNS = ['applied', 'interview', 'offer', 'rejected']
const OUTPUT_LABEL = {
  cover_letter: 'Cover letter',
  interview_answer: 'Interview answer',
  resume_summary: 'Resume summary',
  recruiter_message: 'Recruiter message',
  skill_gap_analysis: 'Skill gap',
}

export default function JobDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const toast = useToast()
  const [job, setJob] = useState(null)
  const [loading, setLoading] = useState(true)

  function load() {
    client.get(`/jobs/${id}`).then((r) => setJob(r.data)).catch(() => navigate('/jobs')).finally(() => setLoading(false))
  }
  useEffect(load, [id])

  async function setStatus(status) {
    try {
      const r = await client.put(`/jobs/${id}`, { status })
      setJob((j) => ({ ...j, ...r.data }))
      toast.success(`Moved to ${STATUS_META[status].label}.`)
    } catch (err) {
      toast.error(errMessage(err))
    }
  }

  async function remove() {
    try {
      await client.delete(`/jobs/${id}`)
      toast.success('Application deleted.')
      navigate('/jobs')
    } catch (err) {
      toast.error(errMessage(err))
    }
  }

  if (loading) return <Layout title="Application"><Spinner /></Layout>
  if (!job) return null

  return (
    <Layout title={job.title} subtitle={job.company}>
      <Link to="/jobs" className="mb-4 inline-flex items-center gap-1.5 text-sm font-semibold text-slate-500 hover:text-ink">
        <ArrowLeft size={16} /> Back to applications
      </Link>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="space-y-6 lg:col-span-2">
          <div className="card p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-base font-bold text-ink">Pipeline status</h2>
              <button onClick={remove} className="inline-flex items-center gap-1.5 rounded-lg px-2 py-1.5 text-xs font-semibold text-rose-600 hover:bg-rose-50">
                <Trash2 size={14} /> Delete
              </button>
            </div>
            <div className="flex flex-wrap gap-2">
              {COLUMNS.map((c) => (
                <button key={c} onClick={() => setStatus(c)}
                  className={`rounded-xl px-4 py-2 text-sm font-semibold transition-colors cursor-pointer ${
                    job.status === c ? 'bg-primary text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                  }`}>
                  {STATUS_META[c].label}
                </button>
              ))}
            </div>
            <div className="mt-4 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
              <Stage label="Applied" date={job.applied_date} />
              <Stage label="Interview" date={job.interview_date} />
              <Stage label="Offer" date={job.offer_date} />
              <Stage label="Rejected" date={job.rejected_date} />
            </div>
          </div>

          <div className="card p-6">
            <h2 className="text-base font-bold text-ink">Job description</h2>
            <p className="mt-2 whitespace-pre-wrap text-sm text-slate-600">
              {job.jd_text || 'No job description saved.'}
            </p>
          </div>
        </div>

        <div className="card p-6">
          <h2 className="text-base font-bold text-ink">Linked documents</h2>
          <p className="text-xs text-slate-500">Generated content attached to this application.</p>
          <div className="mt-4 space-y-3">
            {(!job.generations || job.generations.length === 0) && (
              <p className="text-sm text-slate-400">None yet. Generate content and link it to this job.</p>
            )}
            {job.generations?.map((g) => (
              <div key={g.id} className="rounded-xl border border-slate-200 p-3">
                <div className="flex items-center gap-2">
                  <FileText size={15} className="text-primary" />
                  <Chip tone="violet">{OUTPUT_LABEL[g.output_type] || g.output_type}</Chip>
                </div>
                <p className="mt-2 line-clamp-3 text-sm text-slate-600">{g.output_text}</p>
              </div>
            ))}
          </div>
          <Link to="/generate" className="btn-soft mt-4 w-full">Generate for this role</Link>
        </div>
      </div>
    </Layout>
  )
}

function Stage({ label, date }) {
  return (
    <div className="rounded-xl bg-slate-50 p-3">
      <p className="text-xs font-medium text-slate-400">{label}</p>
      <p className="text-sm font-semibold text-ink">{date ? new Date(date).toLocaleDateString() : '—'}</p>
    </div>
  )
}
