import { BrainCircuit } from 'lucide-react'

export default function AuthShell({ title, subtitle, children }) {
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
