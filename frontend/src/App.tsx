import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from '@/contexts/ThemeContext';
import { AuthProvider, useAuth } from '@/contexts/AuthContext';
import { Layout } from '@/components/layout/Layout';
import { Login } from '@/pages/Login';
import { Dashboard } from '@/pages/Dashboard';
import { TimeBlocks } from '@/pages/TimeBlocks';
import { Priorities } from '@/pages/Priorities';
import { Cadence } from '@/pages/Cadence';
import { Reports } from '@/pages/Reports';
import { Domains } from '@/pages/Domains';
import { AuditLog } from '@/pages/AuditLog';
import { Learning } from '@/pages/Learning';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <ThemeProvider>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route
              element={
                <ProtectedRoute>
                  <Layout />
                </ProtectedRoute>
              }
            >
              <Route path="/" element={<Dashboard />} />
              <Route path="/time-blocks" element={<TimeBlocks />} />
              <Route path="/priorities" element={<Priorities />} />
              <Route path="/cadence" element={<Cadence />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/domains" element={<Domains />} />
              <Route path="/audit-log" element={<AuditLog />} />
              <Route path="/learning" element={<Learning />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}
