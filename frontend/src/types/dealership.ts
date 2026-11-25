export interface Dealership {
  id: number
  name: string
  website: string
  phone: string
  city: string
  address: string
  latitude: number | null
  longitude: number | null
  notes: string
  trust_level: number
  last_checked: string | null
}
