import { Navigate, NavLink, Outlet, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth";
import Icon from "./components/Icon";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Onboarding from "./pages/Onboarding";
import Dashboard from "./pages/Dashboard";
import Questions from "./pages/Questions";
import Reviews from "./pages/Reviews";
import Applications from "./pages/Applications";
import Prep from "./pages/Prep";
import Resume from "./pages/Resume";
import Admin from "./pages/Admin";

const NAV_ITEMS = [
  { to: "/", end: true, icon: "home", label: "Dashboard" },
  { to: "/prep", end: false, icon: "prep", label: "Prep" },
  { to: "/questions", end: false, icon: "questions", label: "Questions" },
  { to: "/reviews", end: false, icon: "reviews", label: "Reviews" },
  { to: "/applications", end: false, icon: "tracker", label: "Tracker" },
  { to: "/resume", end: false, icon: "resume", label: "Resume AI" },
] as const;

function Layout() {
  const { user, loading, logout } = useAuth();
  if (loading) return <div className="page center muted">Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (!user.onboarding_complete) return <Navigate to="/onboarding" replace />;
  const isAdmin = user.role === "admin" || user.role === "super_admin";

  return (
    <div className="shell">
      <aside className="sidebar">
        <div className="sidebar-logo">
          C<span className="logo-dot">.</span>
        </div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => "sidebar-link" + (isActive ? " active" : "")}
              title={item.label}
            >
              <Icon name={item.icon} />
              <span className="sidebar-label">{item.label}</span>
            </NavLink>
          ))}
          {isAdmin && (
            <NavLink
              to="/admin"
              className={({ isActive }) => "sidebar-link admin" + (isActive ? " active" : "")}
              title="Admin"
            >
              <Icon name="admin" />
              <span className="sidebar-label">Admin</span>
            </NavLink>
          )}
        </nav>
        <div className="sidebar-foot">
          <span className="sidebar-email">{user.email}</span>
          <button className="sidebar-logout" onClick={logout} title="Log out">
            <Icon name="logout" />
          </button>
        </div>
      </aside>
      <main className="page">
        <Outlet />
      </main>
    </div>
  );
}

export default function App() {
  const { user } = useAuth();
  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to="/" /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to="/" /> : <Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/onboarding" element={<Onboarding />} />
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/prep" element={<Prep />} />
        <Route path="/questions" element={<Questions />} />
        <Route path="/reviews" element={<Reviews />} />
        <Route path="/applications" element={<Applications />} />
        <Route path="/resume" element={<Resume />} />
        <Route path="/admin" element={<Admin />} />
      </Route>
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}
