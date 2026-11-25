export function formatDistanceKm(km: number | null | undefined, unknown: boolean): string {
  if (unknown || km == null) return 'מיקום לא ברור'
  return `${km.toFixed(1)} ק״מ מקריית טבעון`
}
