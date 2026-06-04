import { ReactNode, useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import {
  Home,
  CreditCard,
  ArrowLeftRight,
  Users,
  Settings,
  LogOut,
  User,
  GitCompare,
  Upload,
  Repeat,
  Menu,
  X,
} from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

interface LayoutProps {
  children: ReactNode
}

function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()
  const [mobileOpen, setMobileOpen] = useState(false)

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/accounts', icon: CreditCard, label: 'Konten' },
    { path: '/transactions', icon: ArrowLeftRight, label: 'Transaktionen' },
    { path: '/shared-accounts', icon: Users, label: 'Gemeinschaft' },
    { path: '/bank-import', icon: Upload, label: 'Bank Import' },
    { path: '/reconciliation', icon: GitCompare, label: 'Abstimmung' },
    { path: '/recurring', icon: Repeat, label: 'Dauerbuchungen' },
    { path: '/settings', icon: Settings, label: 'Einstellungen' },
  ]

  const handleLogout = () => {
    setMobileOpen(false)
    logout()
    navigate('/login')
  }

  // Close the mobile drawer whenever the route changes (link click).
  useEffect(() => {
    setMobileOpen(false)
  }, [location.pathname])

  // Prevent background scroll while the drawer is open.
  useEffect(() => {
    if (mobileOpen) {
      const prev = document.body.style.overflow
      document.body.style.overflow = 'hidden'
      return () => {
        document.body.style.overflow = prev
      }
    }
  }, [mobileOpen])

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Brand */}
            <div className="flex items-center min-w-0">
              <h1 className="text-xl sm:text-2xl font-bold text-primary-600 truncate">
                💰 Money Manager
              </h1>
            </div>

            {/* Desktop nav (>=lg) */}
            <div className="hidden lg:flex lg:items-center lg:space-x-4">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md ${
                      isActive
                        ? 'text-primary-600 bg-primary-50'
                        : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-4 h-4 mr-2" />
                    {item.label}
                  </Link>
                )
              })}
            </div>

            {/* Desktop user-zone (>=lg) */}
            <div className="hidden lg:flex lg:items-center lg:space-x-4">
              {user && (
                <>
                  <div className="flex items-center text-sm text-gray-700">
                    <User className="w-4 h-4 mr-1" />
                    <span className="truncate max-w-[12rem]">{user.username}</span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-red-600 hover:bg-gray-50 rounded-md"
                  >
                    <LogOut className="w-4 h-4 mr-2" />
                    Abmelden
                  </button>
                </>
              )}
            </div>

            {/* Mobile hamburger (<lg) */}
            <button
              type="button"
              aria-label={mobileOpen ? 'Navigation schließen' : 'Navigation öffnen'}
              aria-expanded={mobileOpen}
              aria-controls="mobile-nav"
              onClick={() => setMobileOpen((v) => !v)}
              className="lg:hidden inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-primary-600 hover:bg-gray-50"
            >
              {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile drawer (<lg). Conditional render so screen readers don't see
            the hidden links and Playwright `getByRole('navigation')` reflects
            the visible state. */}
        {mobileOpen && (
          <div
            id="mobile-nav"
            className="lg:hidden border-t border-gray-200 bg-white shadow-inner"
          >
            <nav aria-label="Mobile" className="px-4 py-3 space-y-1">
              {navItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`flex items-center px-3 py-3 rounded-md text-base font-medium ${
                      isActive
                        ? 'text-primary-600 bg-primary-50'
                        : 'text-gray-700 hover:text-primary-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-5 h-5 mr-3" />
                    {item.label}
                  </Link>
                )
              })}
              {user && (
                <div className="pt-3 mt-3 border-t border-gray-200">
                  <div className="flex items-center px-3 py-2 text-sm text-gray-700">
                    <User className="w-4 h-4 mr-2" />
                    <span className="truncate">{user.username}</span>
                  </div>
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center px-3 py-3 rounded-md text-base font-medium text-gray-700 hover:text-red-600 hover:bg-gray-50"
                  >
                    <LogOut className="w-5 h-5 mr-3" />
                    Abmelden
                  </button>
                </div>
              )}
            </nav>
          </div>
        )}
      </nav>
      <main className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">{children}</main>
    </div>
  )
}

export default Layout
