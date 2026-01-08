import { ReactNode } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Home, CreditCard, ArrowLeftRight, Users, Settings, LogOut, User, GitCompare, Upload } from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

interface LayoutProps {
  children: ReactNode
}

function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/accounts', icon: CreditCard, label: 'Konten' },
    { path: '/transactions', icon: ArrowLeftRight, label: 'Transaktionen' },
    { path: '/shared-accounts', icon: Users, label: 'Gemeinschaft' },
    { path: '/bank-import', icon: Upload, label: 'Bank Import' },
    { path: '/reconciliation', icon: GitCompare, label: 'Abstimmung' },
    { path: '/settings', icon: Settings, label: 'Einstellungen' },
  ]

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex space-x-8">
              <div className="flex items-center">
                <h1 className="text-2xl font-bold text-primary-600">💰 Money Manager</h1>
              </div>
              <div className="flex space-x-4">
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
            </div>

            <div className="flex items-center space-x-4">
              {user && (
                <>
                  <div className="flex items-center text-sm text-gray-700">
                    <User className="w-4 h-4 mr-1" />
                    <span>{user.username}</span>
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
          </div>
        </div>
      </nav>
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {children}
      </main>
    </div>
  )
}

export default Layout
