export function RedFlagsBox({ flags }: { flags: string[] }) {
  if (!flags.length) return <p className="text-sm text-slate-500">אין דגלי אזהרה אוטומטיים</p>
  return (
    <ul className="list-disc pr-5 text-sm text-amber-200">
      {flags.map((f) => (
        <li key={f}>{f}</li>
      ))}
    </ul>
  )
}
