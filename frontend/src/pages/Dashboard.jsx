import { useState, useEffect } from 'react'
import {
  DollarSign, TrendingUp, ShoppingCart, Receipt, Percent, Users,
} from 'lucide-react'
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { getKPIs, getMonthlyRevenue, getRevenueByRegion, getCategoryPerformance, getTopProducts } from '../api/analytics'
import { getDatasets } from '../api/datasets'
import KPICard from '../components/KPICard'
import ChartCard from '../components/ChartCard'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorAlert from '../components/ErrorAlert'
import EmptyState from '../components/EmptyState'

const COLORS = ['#052659', '#5483B3', '#7DA0CA', '#C1E8FF']

// Currency formatter used across all charts and cards
const formatCurrency = (val) =>
  '$' + Number(val).toLocaleString('en-US', { maximumFractionDigits: 0 })

const formatCompact = (val) => {
  if (val >= 1_000_000) return '$' + (val / 1_000_000).toFixed(1) + 'M'
  if (val >= 1_000) return '$' + (val / 1_000).toFixed(0) + 'K'
  return '$' + val.toFixed(0)
}

export default function Dashboard() {
  const [datasets, setDatasets] = useState([])
  const [selectedDataset, setSelectedDataset] = useState('')
  const [kpis, setKpis] = useState(null)
  const [monthlyRevenue, setMonthlyRevenue] = useState([])
  const [regionData, setRegionData] = useState([])
  const [categoryData, setCategoryData] = useState([])
  const [topProducts, setTopProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  // Load dataset list on mount
  useEffect(() => {
    getDatasets()
      .then((res) => {
        setDatasets(res.data)
        if (res.data.length > 0) setSelectedDataset(res.data[0].id)
      })
      .catch(() => setDatasets([]))
  }, [])

  // Fetch all dashboard data when dataset selection changes
  useEffect(() => {
    if (datasets.length === 0) {
      setLoading(false)
      return
    }

    const did = selectedDataset || undefined
    setLoading(true)
    setError('')

    Promise.all([
      getKPIs(did),
      getMonthlyRevenue(did),
      getRevenueByRegion(did),
      getCategoryPerformance(did),
      getTopProducts(did, 5),
    ])
      .then(([kpiRes, revenueRes, regionRes, catRes, prodRes]) => {
        setKpis(kpiRes.data)
        setMonthlyRevenue(revenueRes.data)
        setRegionData(regionRes.data)
        setCategoryData(catRes.data)
        setTopProducts(prodRes.data)
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load dashboard data'))
      .finally(() => setLoading(false))
  }, [selectedDataset, datasets])

  if (loading) return <LoadingSpinner message="Loading dashboard..." />

  if (datasets.length === 0) {
    return (
      <EmptyState
        icon={ShoppingCart}
        title="No Datasets Yet"
        description="Upload a sales dataset to see your dashboard. Go to the Datasets page to get started."
        action={{ label: 'Go to Datasets', onClick: () => window.location.href = '/datasets' }}
      />
    )
  }

  if (error) return <ErrorAlert message={error} onRetry={() => setSelectedDataset(selectedDataset)} />

  return (
    <div className="space-y-6">
      {/* Header with dataset selector */}
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

      {/* KPI Cards */}
      {kpis && (
        <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
          <KPICard title="Total Revenue" value={kpis.total_revenue} icon={DollarSign} prefix="$" />
          <KPICard title="Total Profit" value={kpis.total_profit} icon={TrendingUp} prefix="$" />
          <KPICard title="Total Orders" value={kpis.total_orders} icon={ShoppingCart} />
          <KPICard title="Avg Order Value" value={kpis.avg_order_value} icon={Receipt} prefix="$" />
          <KPICard title="Profit Margin" value={kpis.overall_profit_margin} icon={Percent} suffix="%" />
          <KPICard title="Unique Customers" value={kpis.unique_customers} icon={Users} />
        </div>
      )}

      {/* Charts Row 1: Revenue Trend + Region */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Monthly Revenue Trend" subtitle="Revenue over time">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={monthlyRevenue}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis dataKey="period" tick={{ fontSize: 12 }} />
              <YAxis tickFormatter={formatCompact} tick={{ fontSize: 12 }} />
              <Tooltip formatter={(val) => formatCurrency(val)} />
              <Line
                type="monotone"
                dataKey="revenue"
                stroke="#5483B3"
                strokeWidth={2}
                dot={{ fill: '#5483B3', r: 3 }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Revenue by Region" subtitle="Geographic distribution">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={regionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis dataKey="region" tick={{ fontSize: 12 }} />
              <YAxis tickFormatter={formatCompact} tick={{ fontSize: 12 }} />
              <Tooltip formatter={(val) => formatCurrency(val)} />
              <Bar dataKey="revenue" radius={[4, 4, 0, 0]}>
                {regionData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Charts Row 2: Category Pie + Top Products */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Category Performance" subtitle="Revenue share by category">
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryData}
                dataKey="revenue"
                nameKey="category"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ category, percent }) => `${category} ${(percent * 100).toFixed(0)}%`}
              >
                {categoryData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(val) => formatCurrency(val)} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Top 5 Products" subtitle="By total revenue">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={topProducts} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis type="number" tickFormatter={formatCompact} tick={{ fontSize: 12 }} />
              <YAxis
                type="category"
                dataKey="product_name"
                width={150}
                tick={{ fontSize: 11 }}
                tickFormatter={(name) => name.length > 25 ? name.slice(0, 25) + '...' : name}
              />
              <Tooltip formatter={(val) => formatCurrency(val)} />
              <Bar dataKey="total_revenue" fill="#5483B3" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  )
}
