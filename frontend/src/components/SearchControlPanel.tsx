import type { SearchProfile } from '../types/search'

type Props = {
  profile: SearchProfile
  onChange: (p: SearchProfile) => void
  onSave: () => void
  onRun: () => void
  busy: boolean
  message?: string | null
}

export function SearchControlPanel({ profile, onChange, onSave, onRun, busy, message }: Props) {
  const patch = (partial: Partial<SearchProfile>) => onChange({ ...profile, ...partial })

  return (
    <div className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/50 p-4">
      <h2 className="text-lg font-semibold text-slate-100">הגדרות חיפוש</h2>
      <div className="grid gap-3 md:grid-cols-2">
        <label className="text-sm">
          <span className="text-slate-400">מרכז (שם)</span>
          <input
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1"
            value={profile.base_location_name}
            onChange={(e) => patch({ base_location_name: e.target.value })}
          />
        </label>
        <label className="text-sm">
          <span className="text-slate-400">רדיוס (ק״מ)</span>
          <input
            type="number"
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1"
            value={profile.radius_km}
            onChange={(e) => patch({ radius_km: Number(e.target.value) })}
          />
        </label>
        <label className="text-sm">
          <span className="text-slate-400">מחיר מינימום</span>
          <input
            type="number"
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1"
            value={profile.min_price}
            onChange={(e) => patch({ min_price: Number(e.target.value) })}
          />
        </label>
        <label className="text-sm">
          <span className="text-slate-400">מחיר מקסימום</span>
          <input
            type="number"
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1"
            value={profile.max_price}
            onChange={(e) => patch({ max_price: Number(e.target.value) })}
          />
        </label>
        <label className="text-sm">
          <span className="text-slate-400">שנה מינ׳</span>
          <input
            type="number"
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1"
            value={profile.min_year}
            onChange={(e) => patch({ min_year: Number(e.target.value) })}
          />
        </label>
        <label className="text-sm">
          <span className="text-slate-400">שנה מקס׳</span>
          <input
            type="number"
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1"
            value={profile.max_year}
            onChange={(e) => patch({ max_year: Number(e.target.value) })}
          />
        </label>
        <label className="text-sm">
          <span className="text-slate-400">מקס׳ ק״מ מועדף</span>
          <input
            type="number"
            className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1"
            value={profile.max_mileage_preferred}
            onChange={(e) => patch({ max_mileage_preferred: Number(e.target.value) })}
          />
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={profile.include_private_sellers} onChange={(e) => patch({ include_private_sellers: e.target.checked })} />
          כולל מוכרים פרטיים
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={profile.include_dealerships} onChange={(e) => patch({ include_dealerships: e.target.checked })} />
          כולל סוכנויות
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" checked={profile.include_trade_in} onChange={(e) => patch({ include_trade_in: e.target.checked })} />
          כולל טרייד אין
        </label>
      </div>
      <div className="flex flex-wrap gap-2">
        <button type="button" className="rounded-lg bg-slate-800 px-4 py-2 text-sm ring-1 ring-slate-600 hover:bg-slate-700" onClick={onSave} disabled={busy}>
          שמור פרופיל
        </button>
        <button type="button" className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-500 disabled:opacity-50" onClick={onRun} disabled={busy}>
          חפש רכבים עכשיו
        </button>
      </div>
      <p className="text-xs text-slate-400">
        הרדיוס משפיע גם על הרחבת יישובים לשאילתות החיפוש (לא רק על סינון התוצאות אחרי החיפוש).
      </p>
      {message && <p className="text-sm text-amber-200">{message}</p>}
    </div>
  )
}
