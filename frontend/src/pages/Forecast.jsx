import { useState, useEffect } from 'react'
import { TrendingUp, Crosshair, Brain } from 'lucide-react'
import {
  BarChart, Bar, LineChart, Line, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  ReferenceLine,
} from 'recharts'
import { trainModel, getForecastResults, getPredictions } from '../api/forecast'
import { getDatasets } from '../api/datasets'
import KPICard from '../components/KPICard'
import ChartCard from '../components/ChartCard'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import ErrorAlert from '../components/ErrorAlert'

const formatCurrency = (val) =>
  '$' + Number(val).toLocaleString('en-US', { maximumFractionDigits: 0 })

export default function Forecast() {
  const [datasets, setDatasets] = useState([])
  const [selectedDataset, setSelectedDataset] = useState('')
  const [results, setResults] = useState(null)
  const [predictions, setPredictions] = useState([])
  const [loading, setLoading] = useState(true)
  const [training, setTraining] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    getDatasets()
      .then((res) => {
        setDatasets(res.data)
        if (res.data.length > 0) setSelectedDataset(res.data[0].id)
      })
      .catch(() => {})
      .finally(() => setLoading(false))
  }, [])

  // Load existing forecast results when dataset changes
  useEffect(() => {
    if (!selectedDataset) return

    setError('')
    getForecastResults(selectedDataset)
      .then((res) => {
        setResults(res.data)
        // Also fetch future predictions
        return getPredictions(selectedDataset)
      })
      .then((res) => setPredictions(res.data))
      .catch(() => {
        // No model exists yet — that's fine
        setResults(null)
        setPredictions([])
      })
  }, [selectedDataset])

  const handleTrain = async () => {
    if (!selectedDataset) return

    setTraining(true)
    setError('')

    try {
      const res = await trainModel(selectedDataset)
      setResults(res.data)
      // Fetch predictions after training
      const predRes = await getPredictions(selectedDataset)
      setPredictions(predRes.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Training failed. Ensure dataset has enough records.')
    } finally {
      setTraining(false)
    }
  }

  if (loading) return <LoadingSpinner message="Loading forecast..." />

  // Prepare feature importance chart data
  const featureData = results?.feature_importance
    ? Object.entries(results.feature_importance)
        .map(([name, importance]) => ({ name, importance: Number((importance * 100).toFixed(1)) }))
        .sort((a, b) => b.importance - a.importance)
    : []

  return (
    <div className="space-y-6">
      {/* Controls */}
      <div className="flex items-center gap-4 flex-wrap">
        {datasets.length > 0 && (
          <>
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
          </>
        )}

        <button
          onClick={handleTrain}
          disabled={training || !selectedDataset}
          className="btn-primary flex items-center gap-2"
        >
          {training ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Training...
            </>
          ) : (
            <>
              <Brain className="w-4 h-4" />
              Train Model
            </>
          )}
        </button>
      </div>

      {error && <ErrorAlert message={error} />}

      {/* Model explanation card */}
      <div className="card bg-accent-lighter/10 border-accent/20">
        <h3 className="font-semibold text-primary-light mb-2">About the Model</h3>
        <p className="text-sm text-slate-600">
          This uses a <strong>Random Forest Regressor</strong> — an ensemble of 100 decision trees
          that each learn different patterns in the data. It handles non-linear relationships
          (seasonal spikes, category effects) better than Linear Regression, while being simpler
          to train than deep learning approaches like LSTM.
        </p>
      </div>

      {!results ? (
        <EmptyState
          icon={TrendingUp}
          title="No Forecast Model"
          description="Train a model on your dataset to see predictions, accuracy metrics, and feature importance."
        />
      ) : (
        <>
          {/* Model Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <KPICard
              title="RMSE"
              value={results.rmse?.toFixed(2)}
              icon={Crosshair}
              prefix="$"
            />
            <KPICard
              title="MAE"
              value={results.mae?.toFixed(2)}
              icon={Crosshair}
              prefix="$"
            />
            <KPICard
              title="R² Score"
              value={results.r2_score?.toFixed(3)}
              icon={TrendingUp}
            />
          </div>

          {/* Metric explanations */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs text-slate-500">
            <p className="card py-3 px-4">
              <strong>RMSE:</strong> Average prediction error in dollars. Lower is better.
            </p>
            <p className="card py-3 px-4">
              <strong>MAE:</strong> Median prediction error. Less sensitive to outliers than RMSE.
            </p>
            <p className="card py-3 px-4">
              <strong>R²:</strong> How well the model explains variance. 1.0 = perfect, 0 = useless.
            </p>
          </div>

          {/* Feature Importance + Actual vs Predicted */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ChartCard title="Feature Importance" subtitle="What drives sales predictions">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={featureData} layout="vertical" margin={{ left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis type="number" unit="%" tick={{ fontSize: 12 }} />
                  <YAxis type="category" dataKey="name" width={140} tick={{ fontSize: 11 }} />
                  <Tooltip formatter={(val) => val + '%'} />
                  <Bar dataKey="importance" fill="#5483B3" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Actual vs Predicted" subtitle="Model accuracy scatter plot">
              <ResponsiveContainer width="100%" height={300}>
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis dataKey="actual" name="Actual" tick={{ fontSize: 12 }} label={{ value: 'Actual ($)', position: 'bottom', fontSize: 12 }} />
                  <YAxis dataKey="predicted" name="Predicted" tick={{ fontSize: 12 }} label={{ value: 'Predicted ($)', angle: -90, position: 'left', fontSize: 12 }} />
                  <Tooltip formatter={(val) => formatCurrency(val)} />
                  {/* Perfect prediction reference line */}
                  <ReferenceLine
                    segment={[{ x: 0, y: 0 }, { x: Math.max(...(results.predictions || []).map(p => p.actual), 1000), y: Math.max(...(results.predictions || []).map(p => p.actual), 1000) }]}
                    stroke="#CBD5E1"
                    strokeDasharray="5 5"
                  />
                  <Scatter data={results.predictions || []} fill="#5483B3" opacity={0.6} />
                </ScatterChart>
              </ResponsiveContainer>
            </ChartCard>
          </div>

          {/* Future Predictions */}
          {predictions.length > 0 && (
            <ChartCard title="Sales Forecast" subtitle="Predicted revenue for upcoming months">
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={predictions}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
                  <XAxis dataKey="period" tick={{ fontSize: 12 }} />
                  <YAxis tickFormatter={(v) => '$' + (v / 1000).toFixed(0) + 'K'} tick={{ fontSize: 12 }} />
                  <Tooltip formatter={(val) => formatCurrency(val)} />
                  <Line
                    type="monotone"
                    dataKey="predicted_sales"
                    stroke="#052659"
                    strokeWidth={2}
                    dot={{ fill: '#052659', r: 4 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>
          )}
        </>
      )}
    </div>
  )
}
