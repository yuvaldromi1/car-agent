export interface SourceConfig {
  id: string
  name: string
  source_type: string
  enabled: boolean
  legal_mode: string
  base_url: string
  search_instructions: string
  parser_available: boolean
  notes: string
  last_searched_at: string | null
  last_result_count: number
}
