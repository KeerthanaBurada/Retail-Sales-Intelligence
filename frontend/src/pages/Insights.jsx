import { useState, useEffect } from 'react'
import {
  TrendingUp, TrendingDown, DollarSign, Users as UsersIcon,
  MapPin, ShoppingBag, AlertTriangle, Award, Lightbulb,
} from 'lucide-react'
import { getInsights } from '../api/analytics'
import { getDatasets } from '../api/datasets'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import ErrorAlert from '../components/ErrorAlert'

// Map insight categories to icons and colors
const categoryConfig = {
  'Revenue':    { icon: DollarSign,    bgColor: 'bg-blue-50',    textColor: 'text-blue-700',    borderColor: 'border-blue-200' },
  'Profit':     { icon: TrendingUp,    bgColor: 'bg-emerald-50', textColor: 'text-emerald-700', borderColor: 'border-emerald-200' },
  'Customer':   { icon: UsersIcon,     bgColor: 'bg-purple-50',  textColor: 'text-purple-700',  borderColor: 'border-purple-200' },
  'Region':     { icon: MapPin,        bgColor: 'bg-amber-50',   textColor: 'text-amber-700',   borderColor: 'border-amber-200' },
  'Category':   { icon: ShoppingBag,   bgColor: 'bg-cyan-50',    textColor: 'text-cyan-700',    borderColor: 'border-cyan-200' },
  'Warning':    { icon: AlertTriangle, bgColor: 'bg-red-50',     textColor: 'text-red-700',     borderColor: 'border-red-200' },
  'Seasonal':   { icon: Award,         bgColor: 'bg-indigo-50',  textColor: 'text-indigo-700',  borderColor: 'border-indigo-200' },
}

function getConfig(category) {
  return categoryConfig[category] || categoryConfig['Revenue']
}

export default function Insights() {
  const [datasets, setDatasets] = useState([])
  const [selectedDataset, setSelectedDataset] = useState('')
  const [insights, setInsights] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    getDatasets()
      .then((res) => {
        setDatasets(res.data)
        if (res.data.length > 0) setSelectedDataset(res.data[0].id)
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    if (datasets.length === 0) { setLoading(false); return }

    setLoading(true)
    setError('')
    const did = selectedDataset || undefined

    getInsights(did)
      .then((res) => setInsights(res.data))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load insights'))
      .finally(() => setLoading(false))
  }, [selectedDataset, datasets])

  if (loading) return <LoadingSpinner message="Generating insights..." />
  if (error) return <ErrorAlert message={error} />

  if (insights.length === 0) {
    return (
      <EmptyState
        icon={Lightbulb}
        title="No Insights Available"
        description="Upload a dataset and explore the dashboard to generate business insights."
      />
    )
  }

  return (
    <div className="space-y-6">
      {datasets.length > 1 && (
        <div className="flex items-center gap-3">
          <label className="text-sm font-medium text-slate-600">Dataset:</label>
          <select
            value={selectedDataset}
            onChange={(e) => setSelectedDataset(e.target.value)}
            className="select"
          >
            {datasets.map((ds) => (
              <option key={ds.id} value={ds.id}>{ds.filename}</option>
            ))}
          </select>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {insights.map((insight, index) => {
          const config = getConfig(insight.category)
          const Icon = config.icon

          return (
            <div key={index} className={`card border ${config.borderColor}`}>
              {/* Category badge */}
              <div className="flex items-center gap-2 mb-3">
                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${config.bgColor} ${config.textColor}`}>
                  <Icon className="w-3 h-3" />
                  {insight.category}
                </span>
              </div>

              {/* Title and description */}
              <h3 className="font-semibold text-primary mb-1">{insight.title}</h3>
              <p className="text-sm text-slate-600 mb-3">{insight.description}</p>

              {/* Metric highlight */}
              {insight.metric && (
                <p className="text-lg font-bold text-primary-light mb-3">{insight.metric}</p>
              )}

              {/* Recommendation */}
              {insight.recommendation && (
                <div className="bg-accent-lighter/15 border-l-3 border-accent rounded-r-lg p-3">
                  <p className="text-xs font-medium text-accent mb-0.5">Recommendation</p>
                  <p className="text-sm text-slate-700">{insight.recommendation}</p>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
