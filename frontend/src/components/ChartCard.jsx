/**
 * Consistent wrapper for Recharts visualizations.
 * Provides title, optional subtitle, and padded content area.
 */
export default function ChartCard({ title, subtitle, children }) {
  return (
    <div className="card">
      <div className="mb-4">
        <h3 className="font-semibold text-primary-light">{title}</h3>
        {subtitle && <p className="text-sm text-slate-400 mt-0.5">{subtitle}</p>}
      </div>
      {children}
    </div>
  )
}
