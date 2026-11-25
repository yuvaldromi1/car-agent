import { useEffect, useMemo, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { fetchListings } from '../api/listings'
import type { CarListing } from '../types/car'
import { CompareTable } from '../components/CompareTable'

export function ComparePage() {
  const [params] = useSearchParams()
  const ids = useMemo(() => {
    const raw = params.get('ids')?.split(',').map(Number).filter(Boolean) ?? []
    return raw.slice(0, 3)
  }, [params])
  const [listings, setListings] = useState<CarListing[]>([])
  const [all, setAll] = useState<CarListing[]>([])

  useEffect(() => {
    fetchListings().then((d) => {
      setAll(d)
      setListings(d.filter((x) => ids.includes(x.id)))
    })
  }, [ids.join(',')])

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">השוואת רכבים</h2>
      <p className="text-sm text-slate-400">הוסיפו עד 3 מזהים ב-query: ?ids=1,2,3</p>
      <div className="flex flex-wrap gap-2 text-sm">
        {all.slice(0, 12).map((l) => (
          <Link key={l.id} to={`/compare?ids=${[...new Set([...ids, l.id])].slice(0, 3).join(',')}`} className="rounded-lg bg-slate-800 px-2 py-1 hover:bg-slate-700">
            + {l.make} {l.model}
          </Link>
        ))}
      </div>
      <CompareTable listings={listings} />
    </div>
  )
}
