import { useQuery } from '@tanstack/react-query'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || ''

function Dashboard() {
  const { data: accounts } = useQuery({
    queryKey: ['accounts'],
    queryFn: async () => {
      const res = await axios.get(`${API_URL}/api/v1/accounts`)
      return res.data
    },
  })

  const totalBalance = accounts?.reduce((sum: number, acc: any) => 
    sum + parseFloat(acc.balance), 0) || 0

  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">
              Gesamtsaldo
            </dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">
              CHF {totalBalance.toFixed(2)}
            </dd>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">
              Anzahl Konten
            </dt>
            <dd className="mt-1 text-3xl font-semibold text-gray-900">
              {accounts?.length || 0}
            </dd>
          </div>
        </div>

        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <dt className="text-sm font-medium text-gray-500 truncate">
              Status
            </dt>
            <dd className="mt-1 text-3xl font-semibold text-green-600">
              ✓ Aktiv
            </dd>
          </div>
        </div>
      </div>

      <div className="mt-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Schnellzugriff</h2>
        <div className="bg-white shadow rounded-lg p-6">
          <p className="text-gray-600">
            Willkommen beim Money Manager! Nutze das Menü oben, um deine Konten und Transaktionen zu verwalten.
          </p>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
