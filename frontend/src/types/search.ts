export interface SearchProfile {
  id: number
  name: string
  is_active: boolean
  base_location_name: string
  base_latitude: number
  base_longitude: number
  radius_km: number
  min_price: number
  max_price: number
  min_year: number
  max_year: number
  max_mileage_preferred: number
  max_mileage_absolute: number
  family_car_only: boolean
  fuel_preference: string
  include_private_sellers: boolean
  include_dealerships: boolean
  include_trade_in: boolean
  excluded_keywords: string[]
  preferred_models: string[]
  rejected_models: string[]
}

export interface SearchRunSource {
  id: number
  source_id: string
  status: string
  results_found: number
  valid_listings: number
  error_he: string | null
  started_at: string | null
  completed_at: string | null
}

export interface SearchRun {
  id: number
  started_at: string
  completed_at: string | null
  status: string
  error_message_he: string | null
  sources: SearchRunSource[]
}
