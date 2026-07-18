export default function EmptyState({ icon: Icon, title, description, action }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      {Icon && (
        <div className="w-16 h-16 rounded-full bg-accent-lighter/40 flex items-center justify-center mb-4">
          <Icon className="w-8 h-8 text-accent" />
        </div>
      )}
      <h3 className="text-lg font-semibold text-slate-700">{title}</h3>
      <p className="mt-1 text-sm text-slate-500 max-w-md">{description}</p>
      {action && (
        <button onClick={action.onClick} className="btn-primary mt-4">
          {action.label}
        </button>
      )}
    </div>
  )
}
