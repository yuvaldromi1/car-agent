const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'
const API_BASE = import.meta.env.VITE_API_BASE ?? ''

export function isMockMode(): boolean {
  return USE_MOCK
}

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  if (USE_MOCK) {
    throw new Error('apiFetch called in mock mode')
  }
  const url = `${API_BASE}${path}`
  const r = await fetch(url, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!r.ok) {
    let msg = r.statusText
    try {
      const j = await r.json()
      msg = (j.detail as string) || (j.message_he as string) || msg
    } catch {
      /* ignore */
    }
    throw new Error(msg || 'שגיאת שרת')
  }
  if (r.status === 204) return undefined as T
  const text = await r.text()
  if (!text) return undefined as T
  try {
    return JSON.parse(text) as T
  } catch {
    return undefined as T
  }
}
