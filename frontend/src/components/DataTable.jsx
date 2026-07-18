/**
 * Simple, reusable table for displaying tabular data.
 *
 * @param {Array} columns - Array of { key, label, render? } objects.
 *        render is an optional function (value, row) => ReactNode for custom formatting.
 * @param {Array} data - Array of row objects.
 * @param {string} emptyMessage - Message shown when data is empty.
 */
export default function DataTable({ columns, data, emptyMessage = 'No data available' }) {
  if (!data || data.length === 0) {
    return <p className="text-center text-slate-400 py-8">{emptyMessage}</p>
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="bg-slate-50 border-b border-slate-200">
            {columns.map((col) => (
              <th
                key={col.key}
                className="text-left px-4 py-3 text-xs font-semibold text-slate-500 uppercase tracking-wider"
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, rowIndex) => (
            <tr
              key={rowIndex}
              className="border-b border-slate-100 hover:bg-slate-50 transition-colors"
            >
              {columns.map((col) => (
                <td key={col.key} className="px-4 py-3 text-slate-700">
                  {col.render ? col.render(row[col.key], row) : row[col.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
