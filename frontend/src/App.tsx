import { Navigate, NavLink, Outlet, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth";
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

function Layout() {
  const { user, loading, logout } = useAuth();
  if (loading) return <div className="page center muted">Loading…</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (!user.onboarding_complete) return <Navigate to="/onboarding" replace />;
  const isAdmin = user.role === "admin" || user.role === "super_admin";
  return (
    <>
      <nav className="nav">
        <span className="brand">CareerBridge</span>
        <NavLink to="/" end className={({ isActive }) => "link" + (isActive ? " active" : "")}>Dashboard</NavLink>
        <NavLink to="/prep" className={({ isActive }) => "link" + (isActive ? " active" : "")}>Prep</NavLink>
        <NavLink to="/questions" className={({ isActive }) => "link" + (isActive ? " active" : "")}>Questions</NavLink>
        <NavLink to="/reviews" className={({ isActive }) => "link" + (isActive ? " active" : "")}>Reviews</NavLink>
        <NavLink to="/applications" className={({ isActive }) => "link" + (isActive ? " active" : "")}>Tracker</NavLink>
        <NavLink to="/resume" className={({ isActive }) => "link" + (isActive ? " active" : "")}>Resume AI</NavLink>
        {isAdmin && <NavLink to="/admin" className={({ isActive }) => "link" + (isActive ? " active" : "")}>Admin</NavLink>}
        <span className="spacer" />
        <span className="email">{user.email}</span>
        <button className="secondary small" onClick={logout}>Log out</button>
      </nav>
      <main className="page">
        <Outlet />
      </main>
    </>
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
