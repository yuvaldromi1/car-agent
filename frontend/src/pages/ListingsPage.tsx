import { useEffect, useState } from 'react'
import { fetchListings } from '../api/listings'
import type { CarListing } from '../types/car'
import { ListingCard } from '../components/ListingCard'

export function ListingsPage() {
  const [listings, setListings] = useState<CarListing[]>([])
  const [hideFar, setHideFar] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  const load = () =>
    fetchListings({ hide_beyond_radius: hideFar })
      .then(setListings)
      .catch((e) => setErr(e.message))

  useEffect(() => {
    load()
  }, [hideFar])

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="text-2xl font-bold">מודעות</h2>
        <label className="flex items-center gap-2 text-sm text-slate-300">
          <input type="checkbox" checked={hideFar} onChange={(e) => setHideFar(e.target.checked)} />
          הסתר מחוץ לרדיוס
        </label>
      </div>
      {err && <p className="text-rose-400">{err}</p>}
      <div className="space-y-3">
        {listings.map((l) => (
          <ListingCard key={l.id} listing={l} onUpdated={load} />
        ))}
      </div>
    </div>
  )
}
