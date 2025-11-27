import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/auth/ProtectedRoute'
import Layout from './components/layout/Layout'
import Login from './pages/Login'
import Register from './pages/Register'
import Dashboard from './pages/Dashboard'
import Users from './pages/Users'
import Roles from './pages/Roles'
import Locations from './pages/Locations'
import Residents from './pages/Residents'
import Devices from './pages/Devices'
import Alerts from './pages/Alerts'
import CareQuality from './pages/CareQuality'
import IoTData from './pages/IoTData'
import Cards from './pages/Cards'
import AlertPolicies from './pages/AlertPolicies'
import PermissionSettings from './pages/PermissionSettings'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Public Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          {/* Protected Routes */}
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            
            {/* User Management */}
            <Route path="users" element={<Users />} />
            <Route path="roles" element={<Roles />} />
            <Route path="permissions" element={<PermissionSettings />} />
            
            {/* Location & Residents */}
            <Route path="locations" element={<Locations />} />
            <Route path="residents" element={<Residents />} />
            
            {/* Devices & Monitoring */}
            <Route path="devices" element={<Devices />} />
            <Route path="iot-data" element={<IoTData />} />
            <Route path="cards" element={<Cards />} />
            <Route path="alerts" element={<Alerts />} />
            <Route path="alert-policies" element={<AlertPolicies />} />
            
            {/* Quality & Reports */}
            <Route path="care-quality" element={<CareQuality />} />
          </Route>
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
