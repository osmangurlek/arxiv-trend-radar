import { NavLink } from 'react-router-dom'
import { Home, Download, TrendingUp, Search, FileText, Radio } from 'lucide-react'

const links = [
  { to: '/', label: 'Home',            icon: Home,        end: true },
  { to: '/ingest',   label: 'Ingest',  icon: Download },
  { to: '/trends',   label: 'Trends',  icon: TrendingUp },
  { to: '/entities', label: 'Entities',icon: Search },
  { to: '/digest',   label: 'Digest',  icon: FileText },
]

export default function Sidebar() {
  return (
    <aside className="w-56 flex-shrink-0 flex flex-col bg-slate-900 border-r border-slate-800">
      {/* Brand */}
      <div className="px-5 py-5 border-b border-slate-800">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-blue-600 flex items-center justify-center shadow-lg shadow-violet-900/40">
            <Radio className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-100 leading-tight">ArXiv Radar</p>
            <p className="text-xs text-slate-500 leading-tight">Trend Intelligence</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-0.5">
        {links.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive
                  ? 'bg-violet-600/15 text-violet-400 ring-1 ring-violet-500/20'
                  : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/70'
              }`
            }
          >
            <Icon className="w-4 h-4 flex-shrink-0" />
            {label}
          </NavLink>
        ))}
      </nav>

      <div className="px-5 py-4 border-t border-slate-800">
        <p className="text-xs text-slate-600">FastAPI · OpenRouter</p>
      </div>
    </aside>
  )
}
