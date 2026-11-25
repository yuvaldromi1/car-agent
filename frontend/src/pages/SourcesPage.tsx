import { useEffect, useState } from 'react'
import { fetchSources, postSource, testSource, updateSource } from '../api/sources'
import type { SourceConfig } from '../types/source'
import { isMockMode } from '../api/client'

export function SourcesPage() {
  const [rows, setRows] = useState<SourceConfig[]>([])
  const [manualUrl, setManualUrl] = useState('')
  const [manualLabel, setManualLabel] = useState('')
  const [msg, setMsg] = useState<string | null>(null)

  const load = () =>
    fetchSources()
      .then(setRows)
      .catch((e) => setMsg(e.message))

  useEffect(() => {
    if (isMockMode()) {
      setMsg('מצב דמה — אין חיבור לשרת המקורות')
      return
    }
    load()
  }, [])

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">מקורות חיפוש</h2>
      {msg && <p className="text-amber-200">{msg}</p>}
      <div className="rounded-xl border border-slate-800 bg-slate-900/50 p-4">
        <h3 className="mb-2 font-semibold">שמירת קישור ידני</h3>
        <div className="flex flex-col gap-2 md:flex-row">
          <input className="flex-1 rounded border border-slate-700 bg-slate-950 px-2 py-1" placeholder="https://..." value={manualUrl} onChange={(e) => setManualUrl(e.target.value)} />
          <input className="md:w-48 rounded border border-slate-700 bg-slate-950 px-2 py-1" placeholder="תווית" value={manualLabel} onChange={(e) => setManualLabel(e.target.value)} />
          <button
            type="button"
            className="rounded-lg bg-sky-600 px-3 py-1 text-white"
            onClick={async () => {
              try {
                const r = await postSource({ manual_url: manualUrl, manual_label: manualLabel })
                setMsg(r.message_he ?? 'נשמר')
                setManualUrl('')
                load()
              } catch (e) {
                setMsg(e instanceof Error ? e.message : 'שגיאה')
              }
            }}
          >
            שמור
          </button>
        </div>
      </div>
      <div className="overflow-x-auto rounded-xl border border-slate-800">
        <table className="min-w-full text-sm">
          <thead className="bg-slate-900 text-slate-400">
            <tr>
              <th className="p-2 text-start">שם</th>
              <th className="p-2 text-start">מצב חוקי</th>
              <th className="p-2 text-start">מופעל</th>
              <th className="p-2 text-start">הערות</th>
              <th className="p-2 text-start">פעולות</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.id} className="border-t border-slate-800">
                <td className="p-2 font-medium">{r.name}</td>
                <td className="p-2">{r.legal_mode}</td>
                <td className="p-2">
                  <input
                    type="checkbox"
                    checked={r.enabled}
                    onChange={async (e) => {
                      await updateSource(r.id, { enabled: e.target.checked })
                      load()
                    }}
                  />
                </td>
                <td className="p-2 text-slate-400">{r.notes}</td>
                <td className="p-2">
                  <button type="button" className="text-sky-400 hover:underline" onClick={() => testSource(r.id).then((x) => setMsg(x.message_he))}>
                    בדיקה
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
