export function SourceBadge({ name, type }: { name: string; type: string }) {
  return (
    <span className="inline-block rounded-md bg-slate-800 px-2 py-0.5 text-xs text-slate-300 ring-1 ring-slate-600" title={type}>
      {name}
    </span>
  )
}
