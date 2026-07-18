import { useState, useEffect } from 'react'
import {
  BarChart, Bar, LineChart, Line,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import {
  getRevenueByState, getCustomerSegments, getSubcategoryPerformance,
  getTopCustomers, getSalesTrend,
} from '../api/analytics'
import { getDatasets } from '../api/datasets'
import ChartCard from '../components/ChartCard'
import DataTable from '../components/DataTable'
import LoadingSpinner from '../components/LoadingSpinner'
import ErrorAlert from '../components/ErrorAlert'

const COLORS = ['#052659', '#5483B3', '#7DA0CA', '#C1E8FF']

const formatCurrency = (val) =>
  '$' + Number(val).toLocaleString('en-US', { maximumFractionDigits: 0 })

const formatCompact = (val) => {
  if (val >= 1_000_000) return '$' + (val / 1_000_000).toFixed(1) + 'M'
  if (val >= 1_000) return '$' + (val / 1_000).toFixed(0) + 'K'
  return '$' + val.toFixed(0)
}

export default function Analytics() {
  const [datasets, setDatasets] = useState([])
  const [selectedDataset, setSelectedDataset] = useState('')
  const [stateData, setStateData] = useState([])
  const [segmentData, setSegmentData] = useState([])
  const [subcatData, setSubcatData] = useState([])
  const [customerData, setCustomerData] = useState([])
  const [trendData, setTrendData] = useState([])
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

    const did = selectedDataset || undefined
    setLoading(true)
    setError('')

    Promise.all([
      getRevenueByState(did),
      getCustomerSegments(did),
      getSubcategoryPerformance(did),
      getTopCustomers(did),
      getSalesTrend(did),
    ])
      .then(([stateRes, segRes, subcatRes, custRes, trendRes]) => {
        setStateData(stateRes.data)
        setSegmentData(segRes.data)
        setSubcatData(subcatRes.data.slice(0, 10))
        setCustomerData(custRes.data)
        setTrendData(trendRes.data)
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load analytics'))
      .finally(() => setLoading(false))
  }, [selectedDataset, datasets])

  if (loading) return <LoadingSpinner message="Loading analytics..." />
  if (error) return <ErrorAlert message={error} />

  const customerColumns = [
    { key: 'customer_name', label: 'Customer' },
    { key: 'segment', label: 'Segment' },
    { key: 'total_revenue', label: 'Revenue', render: (v) => formatCurrency(v) },
    { key: 'order_count', label: 'Orders' },
  ]

  return (
    <div className="space-y-6">
      {/* Dataset selector */}
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

      {/* Row 1: State Revenue + Customer Segments */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ChartCard title="Revenue by State" subtitle="Top states by total revenue">
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={stateData} layout="vertical" margin={{ left: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis type="number" tickFormatter={formatCompact} tick={{ fontSize: 12 }} />
              <YAxis type="category" dataKey="state" width={100} tick={{ fontSize: 11 }} />
              <Tooltip formatter={(val) => formatCurrency(val)} />
              <Bar dataKey="revenue" fill="#5483B3" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Customer Segments" subtitle="Revenue and customers by segment">
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={segmentData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis dataKey="segment" tick={{ fontSize: 12 }} />
              <YAxis tickFormatter={formatCompact} tick={{ fontSize: 12 }} />
              <Tooltip formatter={(val, name) =>
                name === 'revenue' ? formatCurrency(val) : val
              } />
              <Bar dataKey="revenue" fill="#052659" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Row 2: Subcategory Performance */}
      <ChartCard title="Subcategory Performance" subtitle="Top 10 sub-categories by revenue">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={subcatData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis
              dataKey="sub_category"
              tick={{ fontSize: 11 }}
              angle={-30}
              textAnchor="end"
              height={60}
            />
            <YAxis tickFormatter={formatCompact} tick={{ fontSize: 12 }} />
            <Tooltip formatter={(val) => formatCurrency(val)} />
            <Bar dataKey="revenue" radius={[4, 4, 0, 0]}>
              {subcatData.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* Row 3: Top Customers Table + Sales Trend */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h3 className="card-header">Top Customers</h3>
          <DataTable columns={customerColumns} data={customerData} />
        </div>

        <ChartCard title="Month-over-Month Growth" subtitle="Revenue growth rate (%)">
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
              <XAxis dataKey="period" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} unit="%" />
              <Tooltip formatter={(val) => val !== null ? val.toFixed(1) + '%' : 'N/A'} />
              <Line
                type="monotone"
                dataKey="growth_pct"
                stroke="#5483B3"
                strokeWidth={2}
                dot={{ fill: '#5483B3', r: 3 }}
                connectNulls
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  )
}
