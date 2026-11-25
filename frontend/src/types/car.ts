export interface CarEvaluation {
  total_score: number
  price_score: number
  mileage_score: number
  year_score: number
  fuel_efficiency_score: number
  reliability_score: number
  location_score: number
  seller_trust_score: number
  risk_score: number
  explanation_hebrew: string
  red_flags: string[]
  recommendation: string
}

export interface CarListing {
  id: number
  source_name: string
  source_type: string
  source_url: string
  external_id: string | null
  title: string
  make: string
  model: string
  trim: string | null
  year: number | null
  price: number | null
  mileage: number | null
  fuel_type: string
  transmission: string
  engine_size: string | null
  ownership_type: string
  previous_owners: number | null
  seller_type: string
  seller_name: string | null
  seller_phone: string | null
  location_text: string
  city: string | null
  latitude: number | null
  longitude: number | null
  distance_from_kiryat_tivon_km: number | null
  location_unknown: boolean
  description: string
  image_urls: string[]
  date_found: string
  date_updated: string
  license_plate: string | null
  test_valid_until: string | null
  notes: string
  status: string
  incomplete: boolean
  beyond_radius: boolean
  is_duplicate: boolean
  duplicate_of_id: number | null
  evaluation: CarEvaluation | null
}

export interface CarListingDetail extends CarListing {
  seller_questions: string[]
  purchase_checklist: string[]
}
