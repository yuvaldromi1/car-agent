import { apiFetch, isMockMode } from './client'
import type { SourceConfig } from '../types/source'

export async function fetchSources(): Promise<SourceConfig[]> {
  if (isMockMode()) return []
  return apiFetch('/sources')
}

export async function updateSource(id: string, body: { enabled?: boolean; notes?: string }): Promise<SourceConfig> {
  return apiFetch(`/sources/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export async function postSource(body: Record<string, unknown>): Promise<{ ok: boolean; message_he?: string }> {
  return apiFetch('/sources', { method: 'POST', body: JSON.stringify(body) })
}

export async function testSource(id: string): Promise<{ ok: boolean; message_he: string }> {
  return apiFetch(`/sources/${id}/test`, { method: 'POST' })
}
