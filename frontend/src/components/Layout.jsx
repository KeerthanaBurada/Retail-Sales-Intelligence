import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Navbar from './Navbar'

/**
 * Main layout with fixed sidebar + navbar.
 * The page content renders via <Outlet /> from react-router nested routes.
 */
export default function Layout() {
  return (
    <div className="min-h-screen bg-[#F8FAFC]">
      <Sidebar />
      <Navbar />
      <main className="ml-64 mt-16 p-6">
        <Outlet />
      </main>
    </div>
  )
}
