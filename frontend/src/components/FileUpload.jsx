import { useState, useRef } from 'react'
import { Upload, File, X } from 'lucide-react'

/**
 * Drag-and-drop CSV file upload with visual feedback.
 *
 * @param {Function} onUpload - Callback receiving the selected File object.
 * @param {boolean} loading - True while the upload/ETL is processing.
 */
export default function FileUpload({ onUpload, loading }) {
  const [file, setFile] = useState(null)
  const [dragOver, setDragOver] = useState(false)
  const inputRef = useRef(null)

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && droppedFile.name.endsWith('.csv')) {
      setFile(droppedFile)
    }
  }

  const handleFileSelect = (e) => {
    const selected = e.target.files[0]
    if (selected) setFile(selected)
  }

  const handleUpload = () => {
    if (file && onUpload) {
      onUpload(file)
    }
  }

  const clearFile = () => {
    setFile(null)
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <div className="card">
      <h3 className="card-header">Upload Dataset</h3>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
          ${dragOver
            ? 'border-accent bg-accent-lighter/20'
            : 'border-slate-300 hover:border-accent/50 hover:bg-slate-50'
          }
        `}
      >
        <Upload className="w-10 h-10 text-slate-400 mx-auto mb-3" />
        <p className="text-sm font-medium text-slate-600">
          Drag & drop your CSV file here
        </p>
        <p className="text-xs text-slate-400 mt-1">or click to browse</p>
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      {/* Selected file display */}
      {file && (
        <div className="flex items-center justify-between mt-4 p-3 bg-slate-50 rounded-lg">
          <div className="flex items-center gap-2">
            <File className="w-4 h-4 text-accent" />
            <span className="text-sm font-medium text-slate-700">{file.name}</span>
            <span className="text-xs text-slate-400">
              ({(file.size / 1024).toFixed(1)} KB)
            </span>
          </div>
          <button onClick={clearFile} className="text-slate-400 hover:text-slate-600">
            <X className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* Upload button */}
      {file && (
        <button
          onClick={handleUpload}
          disabled={loading}
          className="btn-primary w-full mt-4 flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Upload className="w-4 h-4" />
              Upload & Process
            </>
          )}
        </button>
      )}
    </div>
  )
}
