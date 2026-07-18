import { AlertCircle } from 'lucide-react'

export default function ErrorAlert({ message, onRetry }) {
  return (
    <div className="flex items-center gap-3 p-4 rounded-lg bg-red-50 border border-red-200">
      <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
      <p className="text-sm text-red-700 flex-1">{message}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-sm font-medium text-red-600 hover:text-red-800"
        >
          Retry
        </button>
      )}
    </div>
  )
}
