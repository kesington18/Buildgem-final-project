import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "./AuthContext";
import { BootScreen } from "../components/ui";

// Must be logged in. Remembers where you were headed so login can send you back.
export function RequireAuth() {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <BootScreen />;
  if (!user) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  return <Outlet />;
}

// Must be a site admin or a group owner.
export function RequireManager() {
  const { canManage } = useAuth();
  if (!canManage) return <Navigate to="/app" replace />;
  return <Outlet />;
}

// Login/register pages: already logged in? go to the app.
export function GuestOnly() {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <BootScreen />;
  if (user) return <Navigate to={location.state?.from || "/app"} replace />;
  return <Outlet />;
}
