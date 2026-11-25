import { useEffect, useState } from 'react'
import { fetchProfile, runSearch, saveProfile, fetchRun } from '../api/search'
import type { SearchProfile } from '../types/search'
import { SearchControlPanel } from '../components/SearchControlPanel'

export function SearchPage() {
  const [profile, setProfile] = useState<SearchProfile | null>(null)
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)
  const [runId, setRunId] = useState<number | null>(null)
  const [run, setRun] = useState<Awaited<ReturnType<typeof fetchRun>> | null>(null)

  useEffect(() => {
    fetchProfile().then(setProfile).catch((e) => setMsg(e.message))
  }, [])

  useEffect(() => {
    if (!runId) return
    const t = setInterval(() => {
      fetchRun(runId)
        .then(setRun)
        .catch(() => {})
    }, 1200)
    return () => clearInterval(t)
  }, [runId])

  if (!profile) return <p className="text-slate-400">טוען פרופיל…</p>

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">סוכן חיפוש</h2>
      <SearchControlPanel
        profile={profile}
        onChange={setProfile}
        busy={busy}
        message={msg}
        onSave={async () => {
          setBusy(true)
          setMsg(null)
          try {
            const p = await saveProfile(profile)
            setProfile(p)
            setMsg('הפרופיל נשמר')
          } catch (e) {
            setMsg(e instanceof Error ? e.message : 'שגיאה')
          } finally {
            setBusy(false)
          }
        }}
        onRun={async () => {
          setBusy(true)
          setMsg(null)
          try {
            await saveProfile(profile)
            const r = await runSearch()
            setRunId(r.run_id)
            setMsg(`${r.message_he}. הופעל חיפוש מורחב לפי רדיוס של ${Math.round(profile.radius_km)} ק״מ.`)
          } catch (e) {
            setMsg(e instanceof Error ? e.message : 'שגיאה')
          } finally {
            setBusy(false)
          }
        }}
      />
      {run && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
          <h3 className="mb-2 font-semibold">התקדמות ריצה #{run.id}</h3>
          <p className="text-sm text-slate-400">סטטוס: {run.status}</p>
          {run.sources.some((s) => (s.error_he ?? '').includes('Google')) && (
            <p className="mt-2 rounded border border-amber-600/40 bg-amber-900/20 px-3 py-2 text-sm text-amber-200">
              כדי לקבל יותר תוצאות אוטומטיות, יש להגדיר GOOGLE_CSE_ID ו-GOOGLE_API_KEY בקובץ .env.
              בינתיים הופעל fallback חוקי ממקורות ידניים וקישורי חיפוש.
            </p>
          )}
          {run.error_message_he && <p className="text-sm text-rose-400">{run.error_message_he}</p>}
          <ul className="mt-2 space-y-2 text-sm">
            {run.sources.map((s) => (
              <li key={s.id} className="rounded border border-slate-800 p-2">
                <span className="font-medium text-slate-200">{s.source_id}</span> — {s.status} · נמצאו {s.results_found} · תקפים {s.valid_listings}
                {s.error_he && <span className="block text-rose-300">{s.error_he}</span>}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
