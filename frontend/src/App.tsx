import { Navigate, NavLink, Outlet, Route, Routes } from "react-router-dom";
import { IconButton, Tooltip } from "@radix-ui/themes";
import { useAuth } from "./auth";
import { Loading } from "./components/ui";
import Icon from "./components/Icon";
import Login from "./pages/Login";
import Register from "./pages/Register";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Onboarding from "./pages/Onboarding";
import Dashboard from "./pages/Dashboard";
import Questions from "./pages/Questions";
import Reviews from "./pages/Reviews";
import Companies from "./pages/Companies";
import CompanyProfile from "./pages/CompanyProfile";
import Applications from "./pages/Applications";
import Prep from "./pages/Prep";
import Resume from "./pages/Resume";
import Admin from "./pages/Admin";
import Profile from "./pages/Profile";

const NAV_ITEMS = [
  { to: "/", end: true, icon: "home", label: "Dashboard" },
  { to: "/prep", end: false, icon: "prep", label: "Prep" },
  { to: "/questions", end: false, icon: "questions", label: "Questions" },
  { to: "/reviews", end: false, icon: "reviews", label: "Reviews" },
  { to: "/companies", end: false, icon: "companies", label: "Companies" },
  { to: "/applications", end: false, icon: "tracker", label: "Tracker" },
  { to: "/resume", end: false, icon: "resume", label: "Resume AI" },
  { to: "/profile", end: false, icon: "profile", label: "Profile" },
] as const;

function Layout() {
  const { user, loading, logout } = useAuth();
  if (loading) return <Loading />;
  if (!user) return <Navigate to="/login" replace />;
  if (!user.onboarding_complete) return <Navigate to="/onboarding" replace />;
  const isAdmin = user.role === "admin" || user.role === "super_admin";

  return (
    <div className="shell">
      <aside className="sidebar">
          <span className="logo-mark">G.</span>
          <nav className="sidebar-nav" aria-label="Main">
            {NAV_ITEMS.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.end}
                className={({ isActive }) => "sidebar-link" + (isActive ? " active" : "")}
              >
                <Icon name={item.icon} />
                {item.label}
              </NavLink>
            ))}
            {isAdmin && (
              <NavLink to="/admin" className={({ isActive }) => "sidebar-link admin" + (isActive ? " active" : "")}>
                <Icon name="admin" />
                Admin
              </NavLink>
            )}
          </nav>
          <div className="sidebar-foot">
            <Tooltip content={`Log out ${user.email}`}>
              <IconButton variant="ghost" color="gray" size="3" onClick={logout} aria-label="Log out">
                <Icon name="logout" />
              </IconButton>
            </Tooltip>
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
        <Route path="/companies" element={<Companies />} />
        <Route path="/companies/:companyId" element={<CompanyProfile />} />
        <Route path="/applications" element={<Applications />} />
        <Route path="/resume" element={<Resume />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/admin" element={<Admin />} />
      </Route>
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  );
}
