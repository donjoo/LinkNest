import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './pages/Login';
import Register from './pages/Register';
import OTPVerification from './pages/OTPVerification';
import Dashboard from './pages/Dashboard';
import Organization from './pages/Organization';
import Namespace from './pages/Namespace';
import InviteAcceptPage from './pages/invite/InviteAcceptPage';
import InviteManagementPage from './pages/invite/InviteManagementPage';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="App">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/verify-otp" element={<OTPVerification />} />
            <Route 
              path="/dashboard" 
              element={
                <ProtectedRoute>
                  <Dashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/organizations/:id" 
              element={
                <ProtectedRoute>
                  <Organization />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/namespaces/:id" 
              element={
                <ProtectedRoute>
                  <Namespace />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/organizations/:id/invites" 
              element={
                <ProtectedRoute>
                  <InviteManagementPage />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/invite/accept" 
              element={
                <ProtectedRoute>
                  <InviteAcceptPage />
                </ProtectedRoute>
              } 
            />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
