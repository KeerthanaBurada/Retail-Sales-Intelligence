import { ArrowUpRight, ArrowDownRight } from 'lucide-react'

/**
 * Displays a single metric in a card format.
 * Used on Dashboard and Forecast pages for KPIs.
 *
 * @param {string} title - Metric label (e.g., "Total Revenue")
 * @param {string|number} value - Formatted metric value
 * @param {Component} icon - Lucide icon component
 * @param {number} change - Optional percentage change (positive = green)
 * @param {string} prefix - Value prefix (e.g., "$")
 * @param {string} suffix - Value suffix (e.g., "%")
 */
export default function KPICard({ title, value, icon: Icon, change, prefix = '', suffix = '' }) {
  // Format large numbers with commas
  const formattedValue = typeof value === 'number'
    ? value.toLocaleString('en-US', { maximumFractionDigits: 1 })
    : value

  return (
    <div className="card flex items-center gap-4">
      {Icon && (
        <div className="w-12 h-12 rounded-lg bg-accent-lighter/40 flex items-center justify-center flex-shrink-0">
          <Icon className="w-6 h-6 text-accent" />
        </div>
      )}
      <div className="min-w-0">
        <p className="text-sm text-slate-500 truncate">{title}</p>
        <p className="text-2xl font-bold text-primary mt-0.5">
          {prefix}{formattedValue}{suffix}
        </p>
        {change !== undefined && change !== null && (
          <div className={`flex items-center gap-1 text-xs mt-1 ${change >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
            {change >= 0 ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
            <span>{Math.abs(change).toFixed(1)}%</span>
          </div>
        )}
      </div>
    </div>
  )
}
