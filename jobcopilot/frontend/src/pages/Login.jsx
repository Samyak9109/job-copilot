import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext.jsx'
import { useToast } from '../components/Toast.jsx'
import { errMessage } from '../api/client.js'
import { Field } from '../components/ui.jsx'
import AuthShell from '../components/AuthShell.jsx'

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
