export function SellerQuestions({ items }: { items: string[] }) {
  return (
    <ol className="list-decimal pr-5 space-y-1 text-sm text-slate-200">
      {items.map((q) => (
        <li key={q}>{q}</li>
      ))}
    </ol>
  )
}
