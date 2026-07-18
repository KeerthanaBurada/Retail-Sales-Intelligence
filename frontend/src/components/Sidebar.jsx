import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Database,
  BarChart3,
  TrendingUp,
  Lightbulb,
  FileText,
  User,
} from 'lucide-react'

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/datasets', label: 'Datasets', icon: Database },
  { to: '/analytics', label: 'Analytics', icon: BarChart3 },
  { to: '/forecast', label: 'Forecast', icon: TrendingUp },
  { to: '/insights', label: 'Insights', icon: Lightbulb },
  { to: '/reports', label: 'Reports', icon: FileText },
]

export default function Sidebar() {
  const linkClasses = ({ isActive }) =>
    `flex items-center gap-3 px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
      isActive
        ? 'bg-white/10 text-white'
        : 'text-slate-400 hover:text-white hover:bg-white/5'
    }`

  return (
    <aside className="fixed left-0 top-0 w-64 h-screen bg-primary flex flex-col z-30">
      {/* App branding */}
      <div className="px-6 py-6 border-b border-white/10">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-7 h-7 text-accent" />
          <div>
            <h1 className="text-white font-bold text-base leading-tight">
              Retail Intelligence
            </h1>
            <p className="text-slate-400 text-xs">Sales Analytics Platform</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink key={item.to} to={item.to} className={linkClasses}>
            <item.icon className="w-5 h-5" />
            {item.label}
          </NavLink>
        ))}

        <div className="border-t border-white/10 my-3" />

        <NavLink to="/profile" className={linkClasses}>
          <User className="w-5 h-5" />
          Profile
        </NavLink>
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-white/10">
        <p className="text-xs text-slate-500">v1.0.0</p>
      </div>
    </aside>
  )
}
