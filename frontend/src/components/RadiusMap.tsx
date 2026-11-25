type Props = {
  radiusKm: number
  centerName: string
  insideCount: number
  totalCount: number
}

export function RadiusMap({ radiusKm, centerName, insideCount, totalCount }: Props) {
  return (
    <div className="rounded-xl border border-slate-800 bg-gradient-to-br from-slate-900 to-slate-950 p-4">
      <h3 className="mb-2 text-sm font-medium text-slate-300">אזור חיפוש</h3>
      <div className="flex h-40 items-center justify-center rounded-full border-2 border-dashed border-sky-500/40 bg-slate-950/80 text-center">
        <div>
          <div className="text-2xl font-bold text-sky-300">{radiusKm} ק״מ</div>
          <div className="text-sm text-slate-400">סביב {centerName}</div>
        </div>
      </div>
      <p className="mt-3 text-xs text-slate-500">
        מסננים לפי מרחק חישובי (Haversine). כרגע {insideCount} מתוך {totalCount} מודעות בתוך הרדיוס (כשיש קואורדינטות).
      </p>
    </div>
  )
}
