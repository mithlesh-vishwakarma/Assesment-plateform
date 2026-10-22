import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { getAuthToken } from '../services/api';

export function getSessionUser(): { name: string; email: string; role: 'candidate' | 'admin' | 'reviewer' } | null {
  try {
    const session = JSON.parse(localStorage.getItem('aec-session') || 'null');
    const token = getAuthToken();
    if (!token && !session) return null;
    return session;
  } catch {
    return null;
  }
}

/**
 * PublicRoute:
 * Blocks logged-in users from viewing public marketing / auth pages.
 * Redirects them directly to their authorized workspace dashboard.
 */
export function PublicRoute({ children }: { children?: React.ReactNode }) {
  const token = getAuthToken();
  const session = getSessionUser();

  if (token || session) {
    const role = (session?.role?.toLowerCase() || localStorage.getItem('aec-active-role') || 'candidate') as 'candidate' | 'admin' | 'reviewer';
    if (role === 'admin') return <Navigate to="/admin" replace />;
    if (role === 'reviewer') return <Navigate to="/reviewer" replace />;
    return <Navigate to="/candidate" replace />;
  }

  return children ? <>{children}</> : <Outlet />;
}

/**
 * RoleProtectedRoute:
 * Enforces strict role-based access control (RBAC).
 * - Unauthenticated users are redirected to /login.
 * - Candidates trying to access /admin or /reviewer are strictly redirected to /candidate.
 * - Reviewers trying to access /admin are strictly redirected to /reviewer.
 * - Administrators can access both admin and reviewer workspaces.
 */
export function RoleProtectedRoute({
  allowedRoles,
}: {
  allowedRoles: ('candidate' | 'admin' | 'reviewer')[];
}) {
  const token = getAuthToken();
  const session = getSessionUser();
  const location = useLocation();

  if (!token && !session) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  const userRole = (session?.role?.toLowerCase() || localStorage.getItem('aec-active-role') || 'candidate') as 'candidate' | 'admin' | 'reviewer';

  // Administrators have full access across admin, reviewer, and candidate preview pages
  if (userRole === 'admin') {
    return <Outlet />;
  }

  // User role matches the required allowed roles
  if (allowedRoles.includes(userRole)) {
    return <Outlet />;
  }

  // Unauthorized candidate attempting to open admin or reviewer routes
  if (userRole === 'candidate') {
    return <Navigate to="/candidate" replace />;
  }

  // Unauthorized reviewer attempting to open admin routes
  if (userRole === 'reviewer') {
    return <Navigate to="/reviewer" replace />;
  }

  return <Navigate to="/login" replace />;
}
