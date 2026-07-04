import { useState } from 'react'
import { UploadCloud, FileText, Type, CheckCircle2 } from 'lucide-react'
import Layout from '../components/Layout.jsx'
import { Field } from '../components/ui.jsx'
import client, { errMessage } from '../api/client.js'
import { useToast } from '../components/Toast.jsx'
import { MEMORY_TYPES } from '../constants.js'

export default function UploadMemory() {
  const toast = useToast()
  const [mode, setMode] = useState('file')
  const [busy, setBusy] = useState(false)
  const [saved, setSaved] = useState(null)

  const [file, setFile] = useState(null)
  const [form, setForm] = useState({ title: '', memory_type: 'resume', text: '' })

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    setSaved(null)
    try {
      let res
      if (mode === 'file') {
        if (!file) throw new Error('Please choose a PDF or DOCX file')
        const fd = new FormData()
        fd.append('file', file)
        fd.append('title', form.title || file.name)
        fd.append('memory_type', form.memory_type)
        res = await client.post('/memory/upload-pdf', fd)
      } else {
        res = await client.post('/memory/remember-text', {
          title: form.title,
          memory_type: form.memory_type,
          text: form.text,
        })
      }
      setSaved(res.data)
      toast.success('Memory remembered successfully.')
      setForm({ title: '', memory_type: form.memory_type, text: '' })
      setFile(null)
    } catch (err) {
      toast.error(errMessage(err, 'Could not save memory'))
    } finally {
      setBusy(false)
    }
  }

  return (
    <Layout title="Add Memory" subtitle="Feed Cognee your career context">
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <form onSubmit={submit} className="card space-y-5 p-6 lg:col-span-2">
          <div className="grid grid-cols-2 gap-2 rounded-xl bg-slate-100 p-1">
            <TabButton active={mode === 'file'} onClick={() => setMode('file')} icon={FileText} label="Upload file" />
            <TabButton active={mode === 'text'} onClick={() => setMode('text')} icon={Type} label="Paste text" />
          </div>

          <Field label="Title" required>
            <input className="input" required placeholder="e.g. My Resume 2026"
              value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </Field>

          <Field label="Memory type" required>
            <select className="input" value={form.memory_type}
              onChange={(e) => setForm({ ...form, memory_type: e.target.value })}>
              {MEMORY_TYPES.map(([v, l]) => <option key={v} value={v}>{l}</option>)}
            </select>
          </Field>

          {mode === 'file' ? (
            <Field label="PDF or DOCX file" required hint="Max 10MB. Resume, project brief, or notes.">
              <label className="flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-center hover:border-primary/50">
                <UploadCloud size={26} className="text-primary" />
                <span className="text-sm font-medium text-slate-600">
                  {file ? file.name : 'Click to choose a file'}
                </span>
                <input type="file" accept=".pdf,.docx" className="hidden"
                  onChange={(e) => setFile(e.target.files?.[0] || null)} />
              </label>
            </Field>
          ) : (
            <Field label="Text" required hint="Paste a project description, job description, or notes.">
              <textarea className="input min-h-[180px]" required
                placeholder="Munchy is a full-stack food ordering platform built with React, Node.js, Express, MongoDB…"
                value={form.text} onChange={(e) => setForm({ ...form, text: e.target.value })} />
            </Field>
          )}

          <button className="btn-primary w-full" disabled={busy}>
            {busy ? 'Remembering…' : 'Remember this'}
          </button>
        </form>

        <div className="space-y-4">
          <div className="card p-5">
            <h3 className="text-sm font-bold text-ink">How memory works</h3>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li>1. We extract the text from your file.</li>
              <li>2. Metadata is stored in the app database.</li>
              <li>3. The content is sent to <span className="font-semibold text-primary-700">Cognee</span> via <code className="rounded bg-slate-100 px-1">remember()</code>.</li>
              <li>4. Later, <code className="rounded bg-slate-100 px-1">recall()</code> pulls it back for generation.</li>
            </ul>
          </div>

          {saved && (
            <div className="card border-emerald-200 bg-emerald-50/50 p-5">
              <div className="flex items-center gap-2 text-emerald-700">
                <CheckCircle2 size={18} />
                <p className="text-sm font-bold">Remembered: {saved.title}</p>
              </div>
              <p className="mt-2 text-xs font-medium text-slate-500">Extracted preview</p>
              <p className="mt-1 max-h-40 overflow-y-auto text-sm text-slate-600">{saved.content_preview}</p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

function TabButton({ active, onClick, icon: Icon, label }) {
  return (
    <button type="button" onClick={onClick}
      className={`flex items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-semibold transition-colors cursor-pointer ${
        active ? 'bg-white text-primary-700 shadow-sm' : 'text-slate-500 hover:text-slate-700'
      }`}>
      <Icon size={16} /> {label}
    </button>
  )
}
