import { useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext.jsx'
import { useToast } from '../components/Toast.jsx'
import { errMessage } from '../api/client.js'
import { Field } from '../components/ui.jsx'
import { AuthShell } from './Login.jsx'

export default function Register() {
  const { user, register } = useAuth()
  const toast = useToast()
  const navigate = useNavigate()
  const [form, setForm] = useState({ name: '', email: '', password: '' })
  const [busy, setBusy] = useState(false)

  if (user) return <Navigate to="/dashboard" replace />

  async function submit(e) {
    e.preventDefault()
    setBusy(true)
    try {
      await register(form.name, form.email, form.password)
      toast.success('Account created — welcome!')
      navigate('/dashboard')
    } catch (err) {
      toast.error(errMessage(err, 'Registration failed'))
    } finally {
      setBusy(false)
    }
  }

  return <AuthShell title="Create your account" subtitle="Start building your AI career memory.">
    <form onSubmit={submit} className="space-y-4">
      <Field label="Name" required>
        <input type="text" autoComplete="name" required className="input"
          value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
      </Field>
      <Field label="Email" required>
        <input type="email" autoComplete="email" required className="input"
          value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
      </Field>
      <Field label="Password" required hint="At least 6 characters.">
        <input type="password" autoComplete="new-password" required minLength={6} className="input"
          value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} />
      </Field>
      <button className="btn-primary w-full" disabled={busy}>{busy ? 'Creating…' : 'Create account'}</button>
    </form>
    <p className="mt-5 text-center text-sm text-slate-500">
      Already have an account? <Link to="/login" className="font-semibold text-primary-700 hover:underline">Sign in</Link>
    </p>
  </AuthShell>
}
