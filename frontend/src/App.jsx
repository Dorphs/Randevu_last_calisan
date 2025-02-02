import React from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { Box } from '@mui/material'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ToplantiListesi from './pages/ToplantiListesi'
import ZiyaretciListesi from './pages/ZiyaretciListesi'
import Login from './pages/Login'
import Raporlar from './pages/Raporlar'
import { AuthProvider } from './contexts/AuthContext'

function App() {
  // Giriş yapmış kullanıcı kontrolü
  const isAuthenticated = localStorage.getItem('token') !== null

  return (
    <AuthProvider>
      <Box sx={{ display: 'flex' }}>
        <Routes>
          <Route
            path="/login"
            element={isAuthenticated ? <Navigate to="/" /> : <Login />}
          />
          
          {/* Korumalı rotalar */}
          <Route
            path="/"
            element={isAuthenticated ? <Layout /> : <Navigate to="/login" />}
          >
            <Route index element={<Dashboard />} />
            <Route path="toplantilar" element={<ToplantiListesi />} />
            <Route path="ziyaretciler" element={<ZiyaretciListesi />} />
            <Route path="raporlar" element={<Raporlar />} />
          </Route>
        </Routes>
      </Box>
    </AuthProvider>
  )
}

export default App
