import type { ReactNode } from 'react'
import type { CarListing } from '../types/car'
import { formatIls, formatKm } from '../utils/format'
import { formatDistanceKm } from '../utils/geo'
import { ScoreBadge } from './ScoreBadge'
import { RedFlagsBox } from './RedFlagsBox'
import { recommendationBadgeClass } from '../utils/scoring'

export function CompareTable({ listings }: { listings: CarListing[] }) {
  if (!listings.length) return <p className="text-slate-500">בחרו עד 3 רכבים להשוואה</p>
  const rows: { label: string; fmt: (l: CarListing) => ReactNode }[] = [
    { label: 'מחיר', fmt: (l: CarListing) => formatIls(l.price) },
    { label: 'שנה', fmt: (l: CarListing) => (l.year != null ? String(l.year) : '—') },
    { label: 'קילומטראז׳', fmt: (l: CarListing) => formatKm(l.mileage) },
    {
      label: 'ק״מ שנתי משוער',
      fmt: (l: CarListing) => {
        if (l.mileage == null || l.year == null) return '—'
        const y = new Date().getFullYear()
        const denom = Math.max(1, y - l.year + 1)
        return `${Math.round(l.mileage / denom).toLocaleString('he-IL')} ק״מ`
      },
    },
    { label: 'דלק', fmt: (l: CarListing) => l.fuel_type },
    { label: 'בעלות', fmt: (l: CarListing) => l.ownership_type },
    { label: 'מרחק', fmt: (l: CarListing) => formatDistanceKm(l.distance_from_kiryat_tivon_km, l.location_unknown) },
    {
      label: 'ציון',
      fmt: (l: CarListing) => (l.evaluation ? <ScoreBadge score={l.evaluation.total_score} /> : '—'),
    },
    {
      label: 'המלצה',
      fmt: (l: CarListing) => {
        const r = l.evaluation?.recommendation ?? '—'
        return <span className={`rounded-full border px-2 py-0.5 text-xs ${recommendationBadgeClass(r)}`}>{r}</span>
      },
    },
  ]
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-800">
      <table className="min-w-full border-collapse text-sm">
        <thead>
          <tr className="bg-slate-900">
            <th className="border border-slate-800 p-2 text-start text-slate-400">מאפיין</th>
            {listings.map((l) => (
              <th key={l.id} className="border border-slate-800 p-2 text-start font-medium text-sky-300">
                {l.make} {l.model}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.label}>
              <td className="border border-slate-800 bg-slate-900/80 p-2 text-slate-400">{row.label}</td>
              {listings.map((l) => (
                <td key={l.id} className="border border-slate-800 p-2">
                  {row.fmt(l)}
                </td>
              ))}
            </tr>
          ))}
          <tr>
            <td className="border border-slate-800 bg-slate-900/80 p-2 text-slate-400">דגלי אזהרה</td>
            {listings.map((l) => (
              <td key={l.id} className="border border-slate-800 p-2 align-top">
                <RedFlagsBox flags={l.evaluation?.red_flags ?? []} />
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  )
}
