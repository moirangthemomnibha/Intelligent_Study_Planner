import { useState } from "react";

import { DashboardPage } from "./pages/DashboardPage";
import { SubjectsPage } from "./pages/SubjectsPage";
import { PlannerPage } from "./pages/PlannerPage";
import { AIAgentPanel } from "./components/AIAgentPanel";
import ProfilePage from "./pages/ProfilePage";

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [collapsed, setCollapsed] = useState(false);

  const views = {
    dashboard: <DashboardPage />,
    subjects: <SubjectsPage />,
    planner: <PlannerPage />,
    agent: <AIAgentPanel />,
    profile: <ProfilePage />,
    settings: (
      <section className="panel">
        <h2>Settings</h2>
        <p>Manage your application preferences here.</p>
      </section>
    ),
  };

  const navigation = [
    { id: "dashboard", icon: "⌂", label: "Dashboard" },
    { id: "subjects", icon: "▤", label: "Subjects" },
    { id: "planner", icon: "▦", label: "Planner" },
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
        className={`sidebar-link ${page === item.id ? "active" : ""}`}
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

      {/* LEFT SIDEBAR */}

      <aside className={`sidebar ${collapsed ? "collapsed" : ""}`}>

        <div className="sidebar-header">

          <span className="sidebar-logo">🌸 Study Planner</span>

          <button
            className="sidebar-toggle"
            onClick={() => setCollapsed(!collapsed)}
            title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          >
            {collapsed ? ">>" : "☰"}
          </button>

        </div>

        <nav className="sidebar-nav">
          {renderNavigation(navigation)}
        </nav>

        <div className="sidebar-bottom">

          <div className="sidebar-divider"></div>

          {renderNavigation(bottomNavigation)}

        </div>

      </aside>

      {/* MAIN CONTENT */}

      <div className="main-content">

        <header className="app-header">

          <h1>🌸 Intelligent Adaptive Study Planner</h1>

          <div className="header-profile">
            ♙
          </div>

        </header>

        <main>
          {views[page]}
        </main>

      </div>

    </div>
  );
}