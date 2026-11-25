import { scoreHue } from '../utils/scoring'

export function ScoreBadge({ score }: { score: number }) {
  return (
    <span className={`inline-flex min-w-[3rem] justify-center rounded-full border border-slate-600 px-2 py-0.5 text-sm font-semibold ${scoreHue(score)}`}>
      {Math.round(score)}
    </span>
  )
}
