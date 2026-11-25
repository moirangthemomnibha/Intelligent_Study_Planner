import { useState } from "react";

import { DashboardPage } from "./pages/DashboardPage";
import { SubjectsPage } from "./pages/SubjectsPage";
import { PlannerPage } from "./pages/PlannerPage";
import { AIAgentPanel } from "./components/AIAgentPanel";
import ProfilePage from "./pages/ProfilePage";
import { Settings } from "lucide-react";

import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import VerifyEmailPage from "./pages/VerifyEmailPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import TasksPage from "./pages/TasksPage";
import SettingsPage from "./pages/SettingsPage";

export default function App() {
  const [page, setPage] = useState(() => {
    if (apiTokenExists()) return "dashboard";

    const pendingEmail = localStorage.getItem(
      "pending_verification_email"
    );

    return pendingEmail ? "verify" : "login";
  });

  const [isAuthenticated, setIsAuthenticated] = useState(
    apiTokenExists()
  );

  const [collapsed, setCollapsed] = useState(false);

  function handleLogin() {
    setIsAuthenticated(true);
    setPage("dashboard");
  }

  function handleLogout() {
    localStorage.removeItem("access_token");
    setIsAuthenticated(false);
    setPage("login");
  }

  // AUTHENTICATION PAGES
  if (!isAuthenticated) {
    if (page === "register") {
      return <RegisterPage onNavigate={setPage} />;
    }

    if (page === "verify") {
      return <VerifyEmailPage onNavigate={setPage} />;
    }

    if (page === "forgot") {
      return <ForgotPasswordPage onNavigate={setPage} />;
    }

    return (
      <LoginPage
        onLogin={handleLogin}
        onNavigate={setPage}
      />
    );
  }

  // APPLICATION PAGES
  const views = {
    dashboard: <DashboardPage />,
    subjects: <SubjectsPage />,
    planner: <PlannerPage />,
    agent: <AIAgentPanel />,
    profile: <ProfilePage />,
    tasks: <TasksPage />,
    settings: <SettingsPage />,
  };

  const navigation = [
    { id: "dashboard", icon: "⌂", label: "Dashboard" },
    { id: "subjects", icon: "▤", label: "Subjects" },
    { id: "planner", icon: "▦", label: "Planner" },
    { id: "tasks", icon: "✓", label: "My Tasks" },
    { id: "agent", icon: "✧", label: "AI Agent" },
  ];

  const bottomNavigation = [
    { id: "profile", icon: "♙", label: "Profile" },
    { id: "settings", icon: "⚙", label: "Settings" },
  ];

  function renderNavigation(items) {
    return items.map((item) => (
      <button
        key={item.id}
        className={`sidebar-link ${
          page === item.id ? "active" : ""
        }`}
        onClick={() => setPage(item.id)}
        title={collapsed ? item.label : ""}
      >
        <span className="sidebar-icon">{item.icon}</span>
        <span className="sidebar-label">{item.label}</span>
      </button>
    ));
  }

  return (
    <div className="app-shell">

      <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>

        <div className="sidebar-header">
          <span className="sidebar-logo">
            🌸 Study Planner
          </span>

          <button
            className="sidebar-toggle"
            onClick={() => setCollapsed(!collapsed)}
          >
            {collapsed ? ">>" : "☰"}
          </button>
        </div>

        <nav className="sidebar-nav">
          {renderNavigation(navigation)}
        </nav>

        <div className="sidebar-bottom">

          <div className="sidebar-divider" />

          {renderNavigation(bottomNavigation)}

          <button
            className="sidebar-link"
            onClick={handleLogout}
          >
            <span className="sidebar-icon">↪</span>
            <span className="sidebar-label">Logout</span>
          </button>

        </div>
      </aside>

      <div className="main-content">

        <header className="app-header">
          <h1>🌸 Intelligent Adaptive Study Planner</h1>
            <button
              type="button"
              className="header-profile"
              onClick={() => setPage("profile")}
              title="Open Profile"
              aria-label="Open Profile"
            >
              ♙
            </button>
        </header>

        <main key={page} className="page-content">
          {views[page] || <DashboardPage />}
        </main>

      </div>
    </div>
  );
}

function apiTokenExists() {
  return Boolean(localStorage.getItem("access_token"));
}