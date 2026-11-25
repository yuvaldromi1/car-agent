import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchListings } from '../api/listings'
import type { CarListing } from '../types/car'
import { ListingCard } from '../components/ListingCard'
import { RadiusMap } from '../components/RadiusMap'
import { fetchProfile } from '../api/search'

export function DashboardPage() {
  const [listings, setListings] = useState<CarListing[]>([])
  const [err, setErr] = useState<string | null>(null)
  const [centerName, setCenterName] = useState('קריית טבעון')
  const [radius, setRadius] = useState(30)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const [l, p] = await Promise.all([fetchListings(), fetchProfile()])
        if (!cancelled) {
          setListings(l)
          setCenterName(p.base_location_name)
          setRadius(p.radius_km)
        }
      } catch (e) {
        if (!cancelled) setErr(e instanceof Error ? e.message : 'שגיאה')
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  const active = useMemo(() => listings.filter((x) => !x.is_duplicate), [listings])
  const inside = useMemo(
    () => active.filter((x) => x.distance_from_kiryat_tivon_km != null && x.distance_from_kiryat_tivon_km <= radius),
    [active, radius],
  )
  const best = useMemo(() => [...active].sort((a, b) => (b.evaluation?.total_score ?? 0) - (a.evaluation?.total_score ?? 0)).slice(0, 5), [active])
  const withPrice = active.filter((x) => x.price != null)
  const withMileage = active.filter((x) => x.mileage != null)
  const avgPrice = withPrice.length ? withPrice.reduce((s, x) => s + (x.price as number), 0) / withPrice.length : 0
  const avgMileage = withMileage.length ? withMileage.reduce((s, x) => s + (x.mileage as number), 0) / withMileage.length : 0
  const redFlags = active.reduce((s, x) => s + (x.evaluation?.red_flags.length ?? 0), 0)
  const bySource = useMemo(() => {
    const m = new Map<string, number>()
    for (const x of active) m.set(x.source_name, (m.get(x.source_name) ?? 0) + 1)
    return [...m.entries()].sort((a, b) => b[1] - a[1])
  }, [active])

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-slate-50">לוח בקרה</h2>
      {err && <p className="text-rose-400">{err}</p>}
      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <div className="text-sm text-slate-400">סה״כ מודעות</div>
          <div className="text-3xl font-bold text-sky-300">{active.length}</div>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <div className="text-sm text-slate-400">בתוך {radius} ק״מ (עם מיקום)</div>
          <div className="text-3xl font-bold text-emerald-300">{inside.length}</div>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <div className="text-sm text-slate-400">דגלי אזהרה (סכום)</div>
          <div className="text-3xl font-bold text-amber-300">{redFlags}</div>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <div className="text-sm text-slate-400">מחיר ממוצע</div>
          <div className="text-2xl font-semibold">{Math.round(avgPrice).toLocaleString('he-IL')} ₪</div>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <div className="text-sm text-slate-400">קילומטראז׳ ממוצע</div>
          <div className="text-2xl font-semibold">{Math.round(avgMileage).toLocaleString('he-IL')} ק״מ</div>
        </div>
        <RadiusMap radiusKm={radius} centerName={centerName} insideCount={inside.length} totalCount={active.length} />
      </div>
      <section>
        <h3 className="mb-3 text-lg font-semibold">פילוח מקורות</h3>
        <ul className="flex flex-wrap gap-2 text-sm">
          {bySource.map(([k, v]) => (
            <li key={k} className="rounded-lg bg-slate-800 px-3 py-1">
              {k}: {v}
            </li>
          ))}
        </ul>
      </section>
      <section>
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-lg font-semibold">חמש המלצות מובילות</h3>
          <Link to="/listings" className="text-sm text-sky-400 hover:underline">
            כל המודעות
          </Link>
        </div>
        <div className="space-y-3">
          {best.map((l) => (
            <ListingCard key={l.id} listing={l} onUpdated={() => fetchListings().then(setListings)} />
          ))}
        </div>
      </section>
    </div>
  )
}
