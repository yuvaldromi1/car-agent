export function PurchaseChecklist({ items }: { items: string[] }) {
  return (
    <ul className="space-y-1 text-sm text-slate-200">
      {items.map((x) => (
        <li key={x} className="flex gap-2">
          <span className="text-emerald-400">✓</span>
          <span>{x}</span>
        </li>
      ))}
    </ul>
  )
}
