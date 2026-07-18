import { useState, useEffect } from 'react'
import { FileText, Download, Trash2, Plus } from 'lucide-react'
import { generateReport, getReports, downloadReport, deleteReport } from '../api/reports'
import { getDatasets } from '../api/datasets'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import ErrorAlert from '../components/ErrorAlert'

export default function Reports() {
  const [datasets, setDatasets] = useState([])
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Form state
  const [selectedDataset, setSelectedDataset] = useState('')
  const [title, setTitle] = useState('')
  const [reportType, setReportType] = useState('summary')

  useEffect(() => {
    Promise.all([getDatasets(), getReports()])
      .then(([dsRes, rpRes]) => {
        setDatasets(dsRes.data)
        setReports(rpRes.data)
        if (dsRes.data.length > 0) setSelectedDataset(dsRes.data[0].id)
      })
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load data'))
      .finally(() => setLoading(false))
  }, [])

  const handleGenerate = async (e) => {
    e.preventDefault()
    if (!selectedDataset || !title) return

    setGenerating(true)
    setError('')
    setSuccess('')

    try {
      await generateReport(selectedDataset, title, reportType)
      setSuccess('Report generated successfully!')
      setTitle('')
      // Refresh reports list
      const res = await getReports()
      setReports(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate report')
    } finally {
      setGenerating(false)
    }
  }

  const handleDownload = async (reportId, format) => {
    try {
      const response = await downloadReport(reportId, format)
      // Create a download link from the blob response
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.download = `report_${reportId}.${format}`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (err) {
      setError('Download failed. Please try again.')
    }
  }

  const handleDelete = async (reportId) => {
    if (!window.confirm('Delete this report?')) return

    try {
      await deleteReport(reportId)
      setReports((prev) => prev.filter((r) => r.id !== reportId))
    } catch (err) {
      setError('Failed to delete report')
    }
  }

  if (loading) return <LoadingSpinner message="Loading reports..." />

  return (
    <div className="space-y-6">
      {/* Generate Report Form */}
      <div className="card">
        <h3 className="card-header">Generate Report</h3>

        <form onSubmit={handleGenerate} className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Dataset</label>
            <select
              value={selectedDataset}
              onChange={(e) => setSelectedDataset(e.target.value)}
              className="select w-full"
            >
              {datasets.map((ds) => (
                <option key={ds.id} value={ds.id}>{ds.filename}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Report Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="input"
              placeholder="e.g. Q4 Sales Analysis"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Type</label>
            <select
              value={reportType}
              onChange={(e) => setReportType(e.target.value)}
              className="select w-full"
            >
              <option value="summary">Summary</option>
              <option value="forecast">Forecast</option>
              <option value="full">Full Report</option>
            </select>
          </div>

          <div className="flex items-end">
            <button
              type="submit"
              disabled={generating || !title}
              className="btn-primary flex items-center gap-2 w-full justify-center"
            >
              {generating ? (
                <>
                  <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Plus className="w-4 h-4" />
                  Generate
                </>
              )}
            </button>
          </div>
        </form>
      </div>

      {success && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-sm text-emerald-700">
          {success}
        </div>
      )}

      {error && <ErrorAlert message={error} />}

      {/* Reports List */}
      <div className="card">
        <h3 className="card-header">Saved Reports</h3>

        {reports.length === 0 ? (
          <EmptyState
            icon={FileText}
            title="No Reports"
            description="Generate a report above to create your first business report."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Title</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Type</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Created</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody>
                {reports.map((report) => (
                  <tr key={report.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-medium">{report.title}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-accent-lighter/40 text-accent">
                        {report.report_type}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-500">
                      {new Date(report.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleDownload(report.id, 'csv')}
                          className="text-xs text-accent hover:text-accent/70 flex items-center gap-1"
                          title="Download CSV"
                        >
                          <Download className="w-3.5 h-3.5" />
                          CSV
                        </button>
                        <button
                          onClick={() => handleDownload(report.id, 'pdf')}
                          className="text-xs text-accent hover:text-accent/70 flex items-center gap-1"
                          title="Download PDF"
                        >
                          <Download className="w-3.5 h-3.5" />
                          PDF
                        </button>
                        <button
                          onClick={() => handleDelete(report.id)}
                          className="text-slate-400 hover:text-red-500 ml-2"
                          title="Delete"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
