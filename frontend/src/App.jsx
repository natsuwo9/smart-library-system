import { NavLink, Navigate, Route, Routes } from "react-router-dom";
import Dashboard from "./pages/Dashboard.jsx";
import Catalog from "./pages/Catalog.jsx";
import Members from "./pages/Members.jsx";
import Loans from "./pages/Loans.jsx";
import Recommendations from "./pages/Recommendations.jsx";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: "📊" },
  { to: "/catalog", label: "Catalog", icon: "📚" },
  { to: "/loans", label: "Loans", icon: "🔄" },
  { to: "/members", label: "Members", icon: "👥" },
  { to: "/recommendations", label: "Recommendations", icon: "✨" },
];

export default function App() {
  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <span>📖</span> Smart Library
        </div>
        <nav>
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to}>
              <span className="icon">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="content">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/catalog" element={<Catalog />} />
          <Route path="/loans" element={<Loans />} />
          <Route path="/members" element={<Members />} />
          <Route path="/recommendations" element={<Recommendations />} />
        </Routes>
      </main>
    </div>
  );
}
