import { apiFetch, isMockMode } from './client'
import type { Dealership } from '../types/dealership'

export async function fetchDealerships(): Promise<Dealership[]> {
  if (isMockMode()) return []
  return apiFetch('/dealerships')
}

export async function createDealership(body: Record<string, unknown>): Promise<Dealership> {
  return apiFetch('/dealerships', { method: 'POST', body: JSON.stringify(body) })
}

export async function updateDealership(id: number, body: Record<string, unknown>): Promise<Dealership> {
  return apiFetch(`/dealerships/${id}`, { method: 'PUT', body: JSON.stringify(body) })
}

export async function deleteDealership(id: number): Promise<void> {
  await apiFetch(`/dealerships/${id}`, { method: 'DELETE' })
}
