import { useState, useEffect } from 'react'
import { User, Calendar, Database, FileText } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { getDatasets } from '../api/datasets'
import { getReports } from '../api/reports'

export default function Profile() {
  const { user } = useAuth()
  const [stats, setStats] = useState({ datasets: 0, reports: 0 })

  useEffect(() => {
    // Fetch counts for the stats cards
    Promise.all([getDatasets(), getReports()])
      .then(([dsRes, rpRes]) => {
        setStats({
          datasets: dsRes.data.length,
          reports: rpRes.data.length,
        })
      })
      .catch(() => {})
  }, [])

  if (!user) return null

  // Generate initials for the avatar
  const initials = user.name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* User Info Card */}
      <div className="card flex items-center gap-6">
        <div className="w-20 h-20 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
          <span className="text-2xl font-bold text-white">{initials}</span>
        </div>
        <div>
          <h2 className="text-xl font-bold text-primary">{user.name}</h2>
          <p className="text-slate-500 mt-0.5">{user.email}</p>
          <div className="flex items-center gap-1 text-xs text-slate-400 mt-2">
            <Calendar className="w-3.5 h-3.5" />
            Member since {new Date(user.created_at).toLocaleDateString('en-US', {
              month: 'long',
              year: 'numeric',
            })}
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 gap-4">
        <div className="card flex items-center gap-4">
          <div className="w-10 h-10 rounded-lg bg-accent-lighter/40 flex items-center justify-center">
            <Database className="w-5 h-5 text-accent" />
          </div>
          <div>
            <p className="text-sm text-slate-500">Datasets Uploaded</p>
            <p className="text-2xl font-bold text-primary">{stats.datasets}</p>
          </div>
        </div>

        <div className="card flex items-center gap-4">
          <div className="w-10 h-10 rounded-lg bg-accent-lighter/40 flex items-center justify-center">
            <FileText className="w-5 h-5 text-accent" />
          </div>
          <div>
            <p className="text-sm text-slate-500">Reports Generated</p>
            <p className="text-2xl font-bold text-primary">{stats.reports}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
