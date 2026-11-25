import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { fetchListing } from '../api/listings'
import type { CarListingDetail } from '../types/car'
import { ScoreBadge } from '../components/ScoreBadge'
import { RedFlagsBox } from '../components/RedFlagsBox'
import { SellerQuestions } from '../components/SellerQuestions'
import { PurchaseChecklist } from '../components/PurchaseChecklist'
import { formatIls, formatKm } from '../utils/format'
import { formatDistanceKm } from '../utils/geo'

export function ListingDetailsPage() {
  const { id } = useParams()
  const [listing, setListing] = useState<CarListingDetail | null>(null)
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    if (!id) return
    fetchListing(Number(id))
      .then(setListing)
      .catch((e) => setErr(e.message))
  }, [id])

  if (err) return <p className="text-rose-400">{err}</p>
  if (!listing) return <p className="text-slate-400">טוען…</p>

  const ev = listing.evaluation

  return (
    <div className="space-y-6">
      <Link to="/listings" className="text-sm text-sky-400 hover:underline">
        חזרה למודעות
      </Link>
      <h2 className="text-2xl font-bold">{listing.title}</h2>
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <h3 className="mb-2 font-semibold text-slate-200">פרטים</h3>
          <dl className="space-y-1 text-sm">
            <div className="flex justify-between gap-2">
              <dt className="text-slate-500">מחיר</dt>
              <dd>{formatIls(listing.price)}</dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt className="text-slate-500">שנה</dt>
              <dd>{listing.year ?? '—'}</dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt className="text-slate-500">קילומטראז׳</dt>
              <dd>{formatKm(listing.mileage)}</dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt className="text-slate-500">מרחק</dt>
              <dd>{formatDistanceKm(listing.distance_from_kiryat_tivon_km, listing.location_unknown)}</dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt className="text-slate-500">דלק</dt>
              <dd>{listing.fuel_type}</dd>
            </div>
            <div className="flex justify-between gap-2">
              <dt className="text-slate-500">מקור</dt>
              <dd>{listing.source_name}</dd>
            </div>
          </dl>
          <a href={listing.source_url} target="_blank" rel="noreferrer" className="mt-3 inline-block text-sky-400 hover:underline">
            פתח מקור
          </a>
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <h3 className="mb-2 font-semibold text-slate-200">ציון</h3>
          {ev ? (
            <>
              <div className="mb-2 flex items-center gap-2">
                <ScoreBadge score={ev.total_score} />
                <span className="text-slate-300">{ev.recommendation}</span>
              </div>
              <ul className="grid grid-cols-2 gap-1 text-xs text-slate-400">
                <li>מחיר: {ev.price_score}</li>
                <li>ק״מ: {ev.mileage_score}</li>
                <li>שנה: {ev.year_score}</li>
                <li>דלק: {ev.fuel_efficiency_score}</li>
                <li>מיקום: {ev.location_score}</li>
                <li>אמינות: {ev.reliability_score}</li>
                <li>מוכר: {ev.seller_trust_score}</li>
                <li>סיכון: {ev.risk_score}</li>
              </ul>
              <p className="mt-3 text-sm leading-relaxed text-slate-200">{ev.explanation_hebrew}</p>
            </>
          ) : (
            <p>אין הערכה</p>
          )}
        </div>
      </div>
      {ev && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <h3 className="mb-2 font-semibold">דגלי אזהרה</h3>
          <RedFlagsBox flags={ev.red_flags} />
        </div>
      )}
      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <h3 className="mb-2 font-semibold">שאלות למוכר</h3>
          <SellerQuestions items={listing.seller_questions} />
        </div>
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <h3 className="mb-2 font-semibold">צ׳ק-ליסט לפני קנייה</h3>
          <PurchaseChecklist items={listing.purchase_checklist} />
        </div>
      </div>
    </div>
  )
}
