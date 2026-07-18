import { useLocation } from 'react-router-dom'
import { LogOut } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

// Map pathnames to human-readable page titles
const pageTitles = {
  '/dashboard': 'Dashboard Overview',
  '/datasets': 'Dataset Management',
  '/analytics': 'Analytics',
  '/forecast': 'Sales Forecast',
  '/insights': 'Business Insights',
  '/reports': 'Reports',
  '/profile': 'Profile',
}

export default function Navbar() {
  const { user, logout } = useAuth()
  const location = useLocation()

  const title = pageTitles[location.pathname] || 'Dashboard'

  return (
    <header className="fixed top-0 left-64 right-0 h-16 bg-white border-b border-slate-200 z-20 flex items-center justify-between px-6">
      <h2 className="text-lg font-semibold text-primary-light">{title}</h2>

      <div className="flex items-center gap-4">
        {user && (
          <span className="text-sm text-slate-600">
            {user.name}
          </span>
        )}
        <button
          onClick={logout}
          className="flex items-center gap-1.5 text-sm text-slate-500 hover:text-red-500 transition-colors"
        >
          <LogOut className="w-4 h-4" />
          Logout
        </button>
      </div>
    </header>
  )
}
