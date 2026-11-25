import { Routes, Route } from 'react-router-dom'
import { Layout } from './Layout'
import { DashboardPage } from './pages/DashboardPage'
import { SearchPage } from './pages/SearchPage'
import { ListingsPage } from './pages/ListingsPage'
import { AddListingPage } from './pages/AddListingPage'
import { ListingDetailsPage } from './pages/ListingDetailsPage'
import { ComparePage } from './pages/ComparePage'
import { SourcesPage } from './pages/SourcesPage'
import { DealershipsPage } from './pages/DealershipsPage'

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<DashboardPage />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="listings" element={<ListingsPage />} />
        <Route path="listings/new" element={<AddListingPage />} />
        <Route path="listings/:id" element={<ListingDetailsPage />} />
        <Route path="compare" element={<ComparePage />} />
        <Route path="sources" element={<SourcesPage />} />
        <Route path="dealerships" element={<DealershipsPage />} />
      </Route>
    </Routes>
  )
}
