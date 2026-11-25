import { useEffect, useState } from 'react'
import { createDealership, deleteDealership, fetchDealerships, updateDealership } from '../api/dealerships'
import type { Dealership } from '../types/dealership'
import { isMockMode } from '../api/client'

export function DealershipsPage() {
  const [rows, setRows] = useState<Dealership[]>([])
  const [name, setName] = useState('')
  const [website, setWebsite] = useState('')
  const [city, setCity] = useState('')
  const [phone, setPhone] = useState('')
  const [msg, setMsg] = useState<string | null>(null)

  const load = () =>
    fetchDealerships()
      .then(setRows)
      .catch((e) => setMsg(e.message))

  useEffect(() => {
    if (isMockMode()) {
      setMsg('מצב דמה — סוכנויות לא נשמרות לשרת')
      return
    }
    load()
  }, [])

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">סוכנויות</h2>
      {msg && <p className="text-amber-200">{msg}</p>}
      <form
        className="grid gap-2 rounded-xl border border-slate-800 bg-slate-900/50 p-4 md:grid-cols-2"
        onSubmit={async (e) => {
          e.preventDefault()
          if (isMockMode()) return
          await createDealership({ name, website, city, phone })
          setName('')
          setWebsite('')
          setCity('')
          setPhone('')
          load()
        }}
      >
        <input required placeholder="שם" className="rounded border border-slate-700 bg-slate-950 px-2 py-1" value={name} onChange={(e) => setName(e.target.value)} />
        <input placeholder="אתר" className="rounded border border-slate-700 bg-slate-950 px-2 py-1" value={website} onChange={(e) => setWebsite(e.target.value)} />
        <input placeholder="עיר" className="rounded border border-slate-700 bg-slate-950 px-2 py-1" value={city} onChange={(e) => setCity(e.target.value)} />
        <input placeholder="טלפון" className="rounded border border-slate-700 bg-slate-950 px-2 py-1" value={phone} onChange={(e) => setPhone(e.target.value)} />
        <button type="submit" className="rounded-lg bg-sky-600 py-2 text-white md:col-span-2">
          הוסף סוכנות
        </button>
      </form>
      <ul className="space-y-2">
        {rows.map((d) => (
          <li key={d.id} className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-slate-800 bg-slate-900/40 p-3">
            <div>
              <div className="font-medium">{d.name}</div>
              <div className="text-xs text-slate-400">
                {d.city} · {d.website}
              </div>
            </div>
            <div className="flex gap-2">
              <button type="button" className="text-sm text-slate-300 hover:underline" onClick={() => updateDealership(d.id, { last_checked: new Date().toISOString() }).then(load)}>
                סומן נבדק
              </button>
              <button type="button" className="text-sm text-rose-400 hover:underline" onClick={() => deleteDealership(d.id).then(load)}>
                מחק
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
