import { apiFetch, isMockMode } from './client'
import type { SearchProfile, SearchRun } from '../types/search'

const mockProfile: SearchProfile = {
  id: 1,
  name: 'ברירת מחדל',
  is_active: true,
  base_location_name: 'קריית טבעון',
  base_latitude: 32.7142,
  base_longitude: 35.1261,
  radius_km: 30,
  min_price: 35000,
  max_price: 43000,
  min_year: 2018,
  max_year: 2026,
  max_mileage_preferred: 110000,
  max_mileage_absolute: 140000,
  family_car_only: true,
  fuel_preference: 'any',
  include_private_sellers: true,
  include_dealerships: true,
  include_trade_in: true,
  excluded_keywords: [],
  preferred_models: [],
  rejected_models: [],
}

export async function fetchProfile(): Promise<SearchProfile> {
  if (isMockMode()) return mockProfile
  return apiFetch('/search/profile')
}

export async function saveProfile(body: Partial<SearchProfile>): Promise<SearchProfile> {
  if (isMockMode()) return { ...mockProfile, ...body }
  return apiFetch('/search/profile', { method: 'PUT', body: JSON.stringify(body) })
}

export async function runSearch(extraUrls: string[] = []): Promise<{ run_id: number; message_he: string }> {
  if (isMockMode()) return { run_id: 1, message_he: 'מצב דמה — לא רץ חיפוש אמיתי' }
  return apiFetch('/search/run', {
    method: 'POST',
    body: JSON.stringify({ extra_manual_urls: extraUrls }),
  })
}

export async function fetchRuns(limit = 20): Promise<SearchRun[]> {
  if (isMockMode()) return []
  return apiFetch(`/search/runs?limit=${limit}`)
}

export async function fetchRun(id: number): Promise<SearchRun> {
  if (isMockMode()) {
    return {
      id,
      started_at: new Date().toISOString(),
      completed_at: new Date().toISOString(),
      status: 'done',
      error_message_he: null,
      sources: [],
    }
  }
  return apiFetch(`/search/runs/${id}`)
}
