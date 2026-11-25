import { NavLink, Outlet } from 'react-router-dom'

const nav = [
  { to: '/', label: 'לוח בקרה' },
  { to: '/search', label: 'סוכן חיפוש' },
  { to: '/listings', label: 'מודעות' },
  { to: '/listings/new', label: 'הוספת מודעה' },
  { to: '/compare', label: 'השוואה' },
  { to: '/sources', label: 'מקורות' },
  { to: '/dealerships', label: 'סוכנויות' },
]

function linkClass({ isActive }: { isActive: boolean }) {
  return `rounded-lg px-3 py-2 text-sm ${isActive ? 'bg-sky-600 text-white' : 'text-slate-300 hover:bg-slate-800'}`
}

export function Layout() {
  return (
    <div className="min-h-screen">
      <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-col gap-3 px-4 py-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-xl font-bold text-slate-50">סוכן רכב משפחתי</h1>
            <p className="text-sm text-slate-400">קריית טבעון · עד 30 ק״מ · חיפוש חוקי בלבד</p>
          </div>
          <nav className="flex flex-wrap gap-1">
            {nav.map((n) => (
              <NavLink key={n.to} to={n.to} end={n.to === '/'} className={linkClass}>
                {n.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">
        <Outlet />
      </main>
    </div>
  )
}
