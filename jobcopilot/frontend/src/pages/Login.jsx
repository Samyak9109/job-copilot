import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { BrainCircuit } from 'lucide-react'
import { useAuth } from '../auth/AuthContext.jsx'
import { useToast } from '../components/Toast.jsx'
import { errMessage } from '../api/client.js'
import { Field } from '../components/ui.jsx'

export default function Login() {
  const { user, login } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', password: '' })
  const [busy, setBusy] = useState(false)

  if (user) return <Navigate to="/dashboard" replace />

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    try {
      await login(form.email, form.password)
      toast.success('Welcome back!')
      navigate('/dashboard')
    } catch (err) {
      toast.error(errMessage(err, 'Login failed'))
    } finally {
      setBusy(false)
    }
  }

  return <AuthShell title="Welcome back" subtitle="Sign in to your career memory.">
    <form onSubmit={submit} className="space-y-4">
      <Field label="Email" required>
        <input type="email" autoComplete="email" required className="input"
          value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
      </Field>
      <Field label="Password" required>
        <input type="password" autoComplete="current-password" required className="input"
          value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
      </Field>
      <button className="btn-primary w-full" disabled={busy}>{busy ? 'Signing in…' : 'Sign in'}</button>
    </form>
    <p className="mt-5 text-center text-sm text-slate-500">
      New here? <Link to="/register" className="font-semibold text-primary-700 hover:underline">Create an account</Link>
    </p>
  </AuthShell>
}

export function AuthShell({ title, subtitle, children }) {
  return (
    <div className="flex min-h-dvh items-center justify-center bg-gradient-to-br from-primary-50 via-slate-50 to-white px-4">
      <div className="w-full max-w-md">
        <div className="mb-6 flex flex-col items-center gap-2 text-center">
          <div className="grid h-12 w-12 place-items-center rounded-2xl bg-primary text-white shadow-card">
            <BrainCircuit size={24} />
          </div>
          <div>
            <h1 className="text-xl font-extrabold text-ink">Job Copilot</h1>
            <p className="text-sm text-slate-500">AI job applications that remember, learn & improve.</p>
          </div>
        </div>
        <div className="card p-7">
          <h2 className="text-lg font-bold text-ink">{title}</h2>
          <p className="mb-5 mt-0.5 text-sm text-slate-500">{subtitle}</p>
          {children}
        </div>
      </div>
    </div>
  )
}
