import { Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import { GuestOnly, RequireAuth, RequireManager } from "./auth/guards";
import { ToastProvider } from "./components/Toast";
import { AppShell } from "./components/AppShell";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Feed from "./pages/Feed";
import Notifications from "./pages/Notifications";
import Following from "./pages/Following";
import ClaimGroup from "./pages/ClaimGroup";
import ManageGroups from "./pages/manage/Groups";
import GroupDetail from "./pages/manage/GroupDetail";
import Moderation from "./pages/manage/Moderation";
import Analytics from "./pages/manage/Analytics";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <Routes>
          {/* Public */}
          <Route path="/" element={<Landing />} />
          <Route element={<GuestOnly />}>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Route>

          {/* Signed-in app */}
          <Route element={<RequireAuth />}>
            <Route path="/app" element={<AppShell />}>
              <Route index element={<Feed />} />
              <Route path="notifications" element={<Notifications />} />
              <Route path="groups" element={<Following />} />
              <Route path="claim" element={<ClaimGroup />} />

              {/* Site admins and group owners only */}
              <Route element={<RequireManager />}>
                <Route path="manage/groups" element={<ManageGroups />} />
                <Route path="manage/groups/:id" element={<GroupDetail />} />
                <Route path="manage/announcements" element={<Moderation />} />
                <Route path="manage/analytics" element={<Analytics />} />
              </Route>
            </Route>
          </Route>

          <Route path="*" element={<NotFound />} />
        </Routes>
      </ToastProvider>
    </AuthProvider>
  );
}
