import { useState, useEffect } from 'react'
import { Database, Trash2, CheckCircle } from 'lucide-react'
import { uploadDataset, getDatasets, deleteDataset } from '../api/datasets'
import FileUpload from '../components/FileUpload'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import ErrorAlert from '../components/ErrorAlert'

export default function Datasets() {
  const [datasets, setDatasets] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState(null)
  const [error, setError] = useState('')

  const fetchDatasets = () => {
    setLoading(true)
    getDatasets()
      .then((res) => setDatasets(res.data))
      .catch((err) => setError(err.response?.data?.detail || 'Failed to load datasets'))
      .finally(() => setLoading(false))
  }

  useEffect(() => { fetchDatasets() }, [])

  const handleUpload = async (file) => {
    setUploading(true)
    setUploadResult(null)
    setError('')

    try {
      const res = await uploadDataset(file)
      setUploadResult(res.data)
      fetchDatasets()
    } catch (err) {
      const detail = err.response?.data?.detail
      if (Array.isArray(detail)) {
        setError(detail.join(', '))
      } else {
        setError(detail || 'Upload failed. Please check your CSV format.')
      }
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (id, filename) => {
    if (!window.confirm(`Delete "${filename}" and all its data?`)) return

    try {
      await deleteDataset(id)
      setDatasets((prev) => prev.filter((d) => d.id !== id))
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete dataset')
    }
  }

  return (
    <div className="space-y-6">
      <FileUpload onUpload={handleUpload} loading={uploading} />

      {/* Upload result summary */}
      {uploadResult && (
        <div className="card bg-emerald-50 border-emerald-200">
          <div className="flex items-center gap-2 mb-3">
            <CheckCircle className="w-5 h-5 text-emerald-600" />
            <h3 className="font-semibold text-emerald-800">Upload Successful</h3>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-slate-500">File</p>
              <p className="font-medium">{uploadResult.filename}</p>
            </div>
            <div>
              <p className="text-slate-500">Rows Processed</p>
              <p className="font-medium">{uploadResult.rows_processed?.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-slate-500">Rows After Cleaning</p>
              <p className="font-medium">{uploadResult.rows_cleaned?.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-slate-500">Duplicates Removed</p>
              <p className="font-medium">{uploadResult.etl_stats?.duplicates_removed || 0}</p>
            </div>
          </div>
          {uploadResult.validation_errors?.length > 0 && (
            <div className="mt-3 text-sm text-amber-700">
              <p className="font-medium">Warnings:</p>
              <ul className="list-disc list-inside mt-1">
                {uploadResult.validation_errors.map((e, i) => <li key={i}>{e}</li>)}
              </ul>
            </div>
          )}
        </div>
      )}

      {error && <ErrorAlert message={error} onRetry={fetchDatasets} />}

      {/* Dataset list */}
      <div className="card">
        <h3 className="card-header">Your Datasets</h3>

        {loading ? (
          <LoadingSpinner message="Loading datasets..." />
        ) : datasets.length === 0 ? (
          <EmptyState
            icon={Database}
            title="No Datasets"
            description="Upload a CSV file above to get started with analytics."
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Filename</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Rows</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Columns</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Status</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Uploaded</th>
                  <th className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody>
                {datasets.map((ds) => (
                  <tr key={ds.id} className="border-b border-slate-100 hover:bg-slate-50 transition-colors">
                    <td className="px-4 py-3 font-medium">{ds.filename}</td>
                    <td className="px-4 py-3">{ds.row_count?.toLocaleString()}</td>
                    <td className="px-4 py-3">{ds.column_count}</td>
                    <td className="px-4 py-3">
                      <span className="px-2 py-0.5 text-xs font-medium rounded-full bg-emerald-100 text-emerald-700">
                        {ds.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-500">
                      {new Date(ds.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-4 py-3">
                      <button
                        onClick={() => handleDelete(ds.id, ds.filename)}
                        className="text-slate-400 hover:text-red-500 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
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
