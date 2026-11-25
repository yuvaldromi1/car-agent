/** UI-only helpers; authoritative scores come from API. */

export function scoreHue(score: number): string {
  if (score >= 75) return 'text-emerald-400'
  if (score >= 55) return 'text-amber-300'
  return 'text-rose-400'
}

export function recommendationBadgeClass(rec: string): string {
  if (rec.includes('כדאי')) return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
  if (rec.includes('אפשרי')) return 'bg-slate-500/20 text-slate-200 border-slate-500/40'
  if (rec.includes('להיזהר')) return 'bg-amber-500/20 text-amber-200 border-amber-500/40'
  return 'bg-rose-500/20 text-rose-200 border-rose-500/40'
}
