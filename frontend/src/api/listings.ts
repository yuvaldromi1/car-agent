import { apiFetch, isMockMode } from './client'
import type { CarListing, CarListingDetail } from '../types/car'
import { mockListings } from '../mocks/listings'
import { PURCHASE_CHECKLIST_HE, SELLER_QUESTIONS_HE } from '../mocks/hebrewCopy'

export async function fetchListings(params?: { hide_beyond_radius?: boolean }): Promise<CarListing[]> {
  if (isMockMode()) return mockListings()
  const q = new URLSearchParams()
  if (params?.hide_beyond_radius) q.set('hide_beyond_radius', 'true')
  const suffix = q.toString() ? `?${q}` : ''
  return apiFetch<CarListing[]>(`/listings${suffix}`)
}

export async function fetchListing(id: number): Promise<CarListingDetail> {
  if (isMockMode()) {
    const m = mockListings().find((x) => x.id === id)
    if (!m) throw new Error('לא נמצא')
    return {
      ...m,
      seller_questions: SELLER_QUESTIONS_HE,
      purchase_checklist: PURCHASE_CHECKLIST_HE,
    }
  }
  return apiFetch<CarListingDetail>(`/listings/${id}`)
}

export async function createListing(body: Record<string, unknown>): Promise<CarListing> {
  return apiFetch<CarListing>('/listings', { method: 'POST', body: JSON.stringify(body) })
}

export async function updateListing(id: number, body: Record<string, unknown>): Promise<CarListing> {
  return apiFetch<CarListing>(`/listings/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export async function importCsv(file: File): Promise<{ imported: number; message_he: string }> {
  const fd = new FormData()
  fd.append('file', file)
  const url = `${import.meta.env.VITE_API_BASE ?? ''}/listings/import-csv`
  const r = await fetch(url, { method: 'POST', body: fd })
  if (!r.ok) throw new Error('ייבוא נכשל')
  return r.json()
}

export async function deduplicateListings(): Promise<{ marked_duplicates: number }> {
  return apiFetch('/listings/deduplicate', { method: 'POST' })
}
