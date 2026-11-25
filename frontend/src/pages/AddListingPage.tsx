import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { createListing } from '../api/listings'
import { isMockMode } from '../api/client'

export function AddListingPage() {
  const nav = useNavigate()
  const [title, setTitle] = useState('')
  const [url, setUrl] = useState('')
  const [price, setPrice] = useState('')
  const [year, setYear] = useState('')
  const [mileage, setMileage] = useState('')
  const [location, setLocation] = useState('')
  const [phone, setPhone] = useState('')
  const [msg, setMsg] = useState<string | null>(null)

  async function submit(e: FormEvent) {
    e.preventDefault()
    setMsg(null)
    if (isMockMode()) {
      setMsg('כבו מצב דמה (VITE_USE_MOCK) כדי לשמור לשרת')
      return
    }
    try {
      const listing = await createListing({
        source_url: url,
        title,
        price: price ? Number(price) : null,
        year: year ? Number(year) : null,
        mileage: mileage ? Number(mileage) : null,
        location_text: location,
        seller_phone: phone || null,
        source_name: 'ידני',
        source_type: 'manual',
        seller_type: 'private',
      })
      nav(`/listings/${listing.id}`)
    } catch (err) {
      setMsg(err instanceof Error ? err.message : 'שגיאה')
    }
  }

  return (
    <div className="mx-auto max-w-xl space-y-4">
      <h2 className="text-2xl font-bold">הוספת מודעה ידנית</h2>
      <form onSubmit={submit} className="space-y-3 rounded-xl border border-slate-800 bg-slate-900/50 p-4">
        <label className="block text-sm">
          <span className="text-slate-400">כותרת</span>
          <input required className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1" value={title} onChange={(e) => setTitle(e.target.value)} />
        </label>
        <label className="block text-sm">
          <span className="text-slate-400">קישור למודעה</span>
          <input required type="url" className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1" value={url} onChange={(e) => setUrl(e.target.value)} />
        </label>
        <div className="grid grid-cols-2 gap-2">
          <label className="text-sm">
            <span className="text-slate-400">מחיר</span>
            <input type="number" className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1" value={price} onChange={(e) => setPrice(e.target.value)} />
          </label>
          <label className="text-sm">
            <span className="text-slate-400">שנה</span>
            <input type="number" className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1" value={year} onChange={(e) => setYear(e.target.value)} />
          </label>
        </div>
        <label className="block text-sm">
          <span className="text-slate-400">קילומטראז׳</span>
          <input type="number" className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1" value={mileage} onChange={(e) => setMileage(e.target.value)} />
        </label>
        <label className="block text-sm">
          <span className="text-slate-400">מיקום (טקסט)</span>
          <input className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1" value={location} onChange={(e) => setLocation(e.target.value)} />
        </label>
        <label className="block text-sm">
          <span className="text-slate-400">טלפון מוכר</span>
          <input className="mt-1 w-full rounded border border-slate-700 bg-slate-950 px-2 py-1" value={phone} onChange={(e) => setPhone(e.target.value)} />
        </label>
        {msg && <p className="text-rose-400">{msg}</p>}
        <button type="submit" className="w-full rounded-lg bg-sky-600 py-2 font-medium text-white hover:bg-sky-500">
          שמור
        </button>
      </form>
    </div>
  )
}
