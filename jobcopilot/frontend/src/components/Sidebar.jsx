import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Upload,
  Library,
  Sparkles,
  Target,
  MessagesSquare,
  Briefcase,
  History,
  Settings,
  BrainCircuit,
} from 'lucide-react'

const NAV = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/jobs', label: 'Applications', icon: Briefcase },
  { to: '/generate', label: 'Generate', icon: Sparkles },
  { to: '/skill-gap', label: 'Skill Gap', icon: Target },
  { to: '/interview-prep', label: 'Interview Prep', icon: MessagesSquare },
  { to: '/memory/upload', label: 'Add Memory', icon: Upload },
  { to: '/memory/library', label: 'Memory Library', icon: Library },
  { to: '/lifecycle', label: 'Memory Lifecycle', icon: History },
  { to: '/settings', label: 'Settings', icon: Settings },
]

export default function Sidebar({ onNavigate }) {
  return (
    <aside className="flex h-full w-64 flex-col border-r border-slate-200 bg-white">
      <div className="flex items-center gap-2.5 px-5 py-5">
        <div className="grid h-9 w-9 place-items-center rounded-xl bg-primary text-white">
          <BrainCircuit size={20} />
        </div>
        <div>
          <p className="text-sm font-extrabold leading-tight text-ink">Job Copilot</p>
          <p className="text-[11px] font-medium text-slate-400">Career memory engine</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-2">
        {NAV.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onNavigate}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-semibold transition-colors ${
                isActive
                  ? 'bg-primary-50 text-primary-700'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-ink'
              }`
            }
          >
            <Icon size={18} />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-4 py-4">
        <div className="rounded-xl bg-slate-900 p-3 text-white">
          <p className="text-xs font-semibold">Memory-first AI</p>
          <p className="mt-1 text-[11px] leading-snug text-slate-300">
            Cognee remembers · recalls · improves · forgets. LangChain shapes the output.
          </p>
        </div>
      </div>
    </aside>
  )
}
