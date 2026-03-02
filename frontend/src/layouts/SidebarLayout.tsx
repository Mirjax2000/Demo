/**
 * Sidebar layout — hlavní navigace aplikace.
 * Obsahuje navigaci, theme toggle, error badge, uživatelský panel.
 */
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth, useRole } from "../auth";
import { useQuery } from "@tanstack/react-query";
import { dashboardApi } from "../api";
import {
  LayoutDashboard,
  ClipboardList,
  Users,
  Building2,
  Upload,
  BarChart3,
  LogOut,
  Menu,
  X,
  Sun,
  Moon,
  Shield,
} from "lucide-react";
import { useState, useEffect } from "react";
import { WrenchIcon } from "../auth/LoginPage";

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/orders", label: "Zakázky", icon: ClipboardList },
  { to: "/teams", label: "Týmy", icon: Users },
  { to: "/clients", label: "Zákazníci", icon: Building2 },
  { to: "/import", label: "Vytvořit", icon: Upload },
  { to: "/reports", label: "Sestavy", icon: BarChart3 },
];

function getInitialTheme(): "dark" | "light" {
  const stored = localStorage.getItem("ams-theme");
  if (stored === "light" || stored === "dark") return stored;
  return "dark";
}

export default function SidebarLayout() {
  const { user, logout } = useAuth();
  const { isAdmin } = useRole();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [theme, setTheme] = useState<"dark" | "light">(getInitialTheme);

  // Error badge — count of problematic ADVICED orders
  const { data: dashData } = useQuery({
    queryKey: ["dashboard-badge"],
    queryFn: () => dashboardApi.get(),
    select: (res) => res.data,
    refetchInterval: 60_000,
  });

  const errorCount = dashData?.invalid_count ?? 0;

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("ams-theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="app-layout">
      {/* Mobile toggle */}
      <button
        className="sidebar-toggle"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label="Toggle menu"
      >
        {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
      </button>

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? "sidebar--open" : ""}`}>
        <div className="sidebar__header">
          <div className="sidebar__brand-icon"><WrenchIcon size={28} /></div>
          <h2 className="sidebar__title">Rhenus HD — <span>AMS</span></h2>
          <span className="sidebar__subtitle">Správa montáží</span>
        </div>

        <nav className="sidebar__nav">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `sidebar__link ${isActive ? "sidebar__link--active" : ""}`
              }
              onClick={() => setSidebarOpen(false)}
            >
              <Icon size={18} />
              <span>{label}</span>
              {/* Error badge on Zakázky link */}
              {to === "/orders" && errorCount > 0 && (
                <span className="sidebar__badge sidebar__badge--error">
                  {errorCount}
                </span>
              )}
            </NavLink>
          ))}
          {/* Admin-only: Uživatelé */}
          {isAdmin && (
            <NavLink
              to="/users"
              className={({ isActive }) =>
                `sidebar__link ${isActive ? "sidebar__link--active" : ""}`
              }
              onClick={() => setSidebarOpen(false)}
            >
              <Shield size={18} />
              <span>Uživatelé</span>
            </NavLink>
          )}
        </nav>

        <div className="sidebar__footer">
          {/* Theme toggle */}
          <button
            className="sidebar__theme-toggle"
            onClick={toggleTheme}
            title={theme === "dark" ? "Přepnout na světlý režim" : "Přepnout na tmavý režim"}
          >
            {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
            <span>{theme === "dark" ? "Světlý" : "Tmavý"}</span>
          </button>

          <div className="sidebar__user">
            <span>{user?.first_name || user?.username}</span>
            {user?.role && <span className="sidebar__role">{user.role}</span>}
          </div>
          <button className="sidebar__logout" onClick={handleLogout}>
            <LogOut size={18} />
            <span>Odhlásit</span>
          </button>
        </div>
      </aside>

      {/* Overlay for mobile */}
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main content */}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
