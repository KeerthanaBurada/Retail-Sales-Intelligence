export default function LoadingSpinner({ message = 'Loading...' }) {
  return (
    <div className="flex flex-col items-center justify-center py-16">
      <div className="w-10 h-10 border-4 border-accent/30 border-t-accent rounded-full animate-spin" />
      <p className="mt-4 text-sm text-slate-500">{message}</p>
    </div>
  )
}
