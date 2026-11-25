import type { CarListing } from '../types/car'
import { formatIls, formatKm } from '../utils/format'
import { formatDistanceKm } from '../utils/geo'
import { recommendationBadgeClass } from '../utils/scoring'
import { ScoreBadge } from './ScoreBadge'
import { SourceBadge } from './SourceBadge'
import { RedFlagsBox } from './RedFlagsBox'
import { Link } from 'react-router-dom'
import { updateListing } from '../api/listings'
import { isMockMode } from '../api/client'

export function ListingCard({ listing, onUpdated }: { listing: CarListing; onUpdated?: () => void }) {
  const ev = listing.evaluation
  const rec = ev?.recommendation ?? '—'

  async function setStatus(status: string) {
    if (isMockMode()) {
      onUpdated?.()
      return
    }
    await updateListing(listing.id, { status })
    onUpdated?.()
  }

  return (
    <article className="flex flex-col gap-3 rounded-xl border border-slate-800 bg-slate-900/60 p-4 shadow-lg shadow-black/20">
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <Link to={`/listings/${listing.id}`} className="text-lg font-semibold text-sky-300 hover:underline">
            {listing.title}
          </Link>
          <p className="text-sm text-slate-400">
            {listing.make} {listing.model} {listing.year ? `· ${listing.year}` : ''}
          </p>
        </div>
        {ev && <ScoreBadge score={ev.total_score} />}
      </div>
      <div className="grid grid-cols-2 gap-2 text-sm md:grid-cols-4">
        <div>
          <div className="text-slate-500">מחיר</div>
          <div className="font-medium">{formatIls(listing.price)}</div>
        </div>
        <div>
          <div className="text-slate-500">קילומטראז׳</div>
          <div className="font-medium">{formatKm(listing.mileage)}</div>
        </div>
        <div>
          <div className="text-slate-500">מרחק</div>
          <div className="font-medium">{formatDistanceKm(listing.distance_from_kiryat_tivon_km, listing.location_unknown)}</div>
        </div>
        <div>
          <div className="text-slate-500">מוכר</div>
          <div className="font-medium">{listing.seller_type}</div>
        </div>
      </div>
      <div className="flex flex-wrap items-center gap-2">
        <SourceBadge name={listing.source_name} type={listing.source_type} />
        {listing.incomplete && <span className="text-xs text-amber-300">חסרים פרטים</span>}
        {listing.beyond_radius && <span className="text-xs text-rose-300">מחוץ לרדיוס</span>}
        <span className={`rounded-full border px-2 py-0.5 text-xs ${recommendationBadgeClass(rec)}`}>{rec}</span>
      </div>
      {ev && ev.red_flags.length > 0 && (
        <div>
          <div className="mb-1 text-xs font-medium text-slate-400">דגלי אזהרה</div>
          <RedFlagsBox flags={ev.red_flags} />
        </div>
      )}
      <div className="flex flex-wrap gap-2">
        <a
          href={listing.source_url}
          target="_blank"
          rel="noreferrer"
          className="rounded-lg bg-slate-800 px-3 py-1.5 text-sm text-slate-100 ring-1 ring-slate-600 hover:bg-slate-700"
        >
          פתח מקור
        </a>
        <button type="button" className="rounded-lg bg-emerald-900/40 px-3 py-1.5 text-sm hover:bg-emerald-900/60" onClick={() => setStatus('favorite')}>
          שמור למועדפים
        </button>
        <button type="button" className="rounded-lg bg-rose-900/30 px-3 py-1.5 text-sm hover:bg-rose-900/50" onClick={() => setStatus('rejected')}>
          דחה
        </button>
        <button type="button" className="rounded-lg bg-slate-800 px-3 py-1.5 text-sm hover:bg-slate-700" onClick={() => setStatus('contacted')}>
          סימנתי שהתקשרתי
        </button>
        <button type="button" className="rounded-lg bg-sky-900/40 px-3 py-1.5 text-sm hover:bg-sky-900/60" onClick={() => setStatus('scheduled_inspection')}>
          קבע בדיקה
        </button>
      </div>
    </article>
  )
}
