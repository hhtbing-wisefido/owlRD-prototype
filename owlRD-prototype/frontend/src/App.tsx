import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Users from './pages/Users'
import Roles from './pages/Roles'
import Locations from './pages/Locations'
import Residents from './pages/Residents'
import Devices from './pages/Devices'
import Alerts from './pages/Alerts'
import CareQuality from './pages/CareQuality'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          
          {/* User Management */}
          <Route path="users" element={<Users />} />
          <Route path="roles" element={<Roles />} />
          
          {/* Location & Residents */}
          <Route path="locations" element={<Locations />} />
          <Route path="residents" element={<Residents />} />
          
          {/* Devices & Monitoring */}
          <Route path="devices" element={<Devices />} />
          <Route path="alerts" element={<Alerts />} />
          
          {/* Quality & Reports */}
          <Route path="care-quality" element={<CareQuality />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
