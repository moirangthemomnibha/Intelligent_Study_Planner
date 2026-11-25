import { useEffect, useState } from "react";
import { useTheme } from "../context/ThemeContext";

const API_URL = "http://127.0.0.1:8000/api/v1";

const defaultSettings = {
  theme: "system",
  accent_color: "#D98FA5",
  font_size: "medium",

  pomodoro_work_min: 25,
  pomodoro_short_break_min: 5,
  pomodoro_long_break_min: 15,
  sessions_before_long_break: 4,

  daily_study_target_hours: 3,
  preferred_study_start: "",
  preferred_study_end: "",

  study_reminders: true,
  assignment_reminders: true,
  exam_reminders: true,
  break_reminders: true,
  motivational_notifications: false,

  ai_personalization: true,
};

const THEME_STORAGE_KEY = "study_planner_theme";

export default function SettingsPage() {
  const {
    theme,
    setTheme,
    accentColor,
    setAccentColor,
    fontSize,
    setFontSize,
  } = useTheme();

  const [settings, setSettings] = useState({
    ...defaultSettings,
    theme,
    accent_color: accentColor,
    font_size: fontSize,
  });

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  const token =
    localStorage.getItem("access_token") ||
    localStorage.getItem("token");

  // LOAD SETTINGS
  useEffect(() => {
    loadSettings();
  }, []);

  async function loadSettings() {
    try {
      if (!token) {
        throw new Error("Authentication required. Please log in again.");
      }

      const response = await fetch(`${API_URL}/settings/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Unable to load settings.");
      }

      const data = await response.json();

      const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);

      const loadedSettings = {
        ...defaultSettings,
        ...data,
        theme: savedTheme || data.theme || "system",
      };

      setSettings(loadedSettings);

      // Synchronize global theme
      setTheme(loadedSettings.theme);
      setAccentColor(loadedSettings.accent_color);
      setFontSize(loadedSettings.font_size);

    } catch (error) {
      setMessage(error.message);

    } finally {
      setLoading(false);
    }
  }

  // HANDLE INPUT CHANGES
  function handleChange(name, value) {
    setSettings((previous) => ({
      ...previous,
      [name]: value,
    }));

    // Update global theme immediately
    if (name === "theme") {
      setTheme(value);
      localStorage.setItem(THEME_STORAGE_KEY, value);
    }

    if (name === "accent_color") {
      setAccentColor(value);
    }

    if (name === "font_size") {
      setFontSize(value);
    }
  }

  // SAVE SETTINGS
  async function saveSettings() {
    setSaving(true);
    setMessage("");

    try {
      if (!token) {
        throw new Error("Authentication required.");
      }

      const response = await fetch(`${API_URL}/settings/`, {
        method: "PUT",

        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },

        body: JSON.stringify({
          ...settings,
          theme,
          accent_color: accentColor,
          font_size: fontSize,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to save settings.");
      }

      const data = await response.json();

      setSettings({
        ...defaultSettings,
        ...data,
        theme,
        accent_color: accentColor,
        font_size: fontSize,
      });

      localStorage.setItem(THEME_STORAGE_KEY, theme);

      setMessage("Settings saved successfully!");

    } catch (error) {
      setMessage(error.message);

    } finally {
      setSaving(false);
    }
  }

  if (loading) {
    return (
      <div className="settings-loading">
        Loading settings...
      </div>
    );
  }

  return (
    <div className="settings-page">

      <div className="settings-header">
        <div>
          <h1>Settings</h1>
          <p>Customize your study experience.</p>
        </div>

        <button
          className="save-settings-btn"
          onClick={saveSettings}
          disabled={saving}
        >
          {saving ? "Saving..." : "Save Changes"}
        </button>
      </div>

      {message && (
        <div className="settings-message">
          {message}
        </div>
      )}

      {/* APPEARANCE */}

      <section className="settings-card">

        <h2>Appearance</h2>

        <p>Personalize how your application looks.</p>

        <div className="setting-row">
          <label>Theme</label>

          <select
            value={theme}
            onChange={(e) =>
              handleChange("theme", e.target.value)
            }
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="system">System Default</option>
          </select>
        </div>

        <div className="setting-row">
          <label>Accent Color</label>

          <input
            type="color"
            value={accentColor}
            onChange={(e) =>
              handleChange("accent_color", e.target.value)
            }
          />
        </div>

        <div className="setting-row">
          <label>Font Size</label>

          <select
            value={fontSize}
            onChange={(e) =>
              handleChange("font_size", e.target.value)
            }
          >
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </select>
        </div>

      </section>

      {/* POMODORO */}

      <section className="settings-card">

        <h2>Pomodoro Timer</h2>

        <p>Configure your focus and break sessions.</p>

        {[
          ["pomodoro_work_min", "Focus Duration (minutes)"],
          ["pomodoro_short_break_min", "Short Break (minutes)"],
          ["pomodoro_long_break_min", "Long Break (minutes)"],
          ["sessions_before_long_break", "Sessions Before Long Break"],
        ].map(([key, label]) => (
          <div className="setting-row" key={key}>

            <label>{label}</label>

            <input
              type="number"
              min="1"
              value={settings[key]}
              onChange={(e) =>
                handleChange(key, Number(e.target.value))
              }
            />

          </div>
        ))}

      </section>

      {/* STUDY PREFERENCES */}

      <section className="settings-card">

        <h2>Study Preferences</h2>

        <p>Set your daily study goals and preferred hours.</p>

        <div className="setting-row">
          <label>Daily Study Target (hours)</label>

          <input
            type="number"
            min="0.5"
            max="24"
            step="0.5"
            value={settings.daily_study_target_hours}
            onChange={(e) =>
              handleChange(
                "daily_study_target_hours",
                Number(e.target.value)
              )
            }
          />
        </div>

        <div className="setting-row">
          <label>Preferred Start Time</label>

          <input
            type="time"
            value={settings.preferred_study_start || ""}
            onChange={(e) =>
              handleChange("preferred_study_start", e.target.value)
            }
          />
        </div>

        <div className="setting-row">
          <label>Preferred End Time</label>

          <input
            type="time"
            value={settings.preferred_study_end || ""}
            onChange={(e) =>
              handleChange("preferred_study_end", e.target.value)
            }
          />
        </div>

      </section>

      {/* NOTIFICATIONS */}

      <section className="settings-card">

        <h2>Notifications</h2>

        <p>Manage your study reminders.</p>

        {[
          ["study_reminders", "Study Reminders"],
          ["assignment_reminders", "Assignment Deadlines"],
          ["exam_reminders", "Exam Reminders"],
          ["break_reminders", "Break Reminders"],
          ["motivational_notifications", "Daily Motivation"],
        ].map(([key, label]) => (
          <div className="setting-row" key={key}>

            <label>{label}</label>

            <input
              type="checkbox"
              checked={Boolean(settings[key])}
              onChange={(e) =>
                handleChange(key, e.target.checked)
              }
            />

          </div>
        ))}

      </section>

      {/* AI PREFERENCES */}

      <section className="settings-card">

        <h2>AI Preferences</h2>

        <p>Manage AI personalization.</p>

        <div className="setting-row">

          <label>Personalized AI Recommendations</label>

          <input
            type="checkbox"
            checked={Boolean(settings.ai_personalization)}
            onChange={(e) =>
              handleChange("ai_personalization", e.target.checked)
            }
          />

        </div>

      </section>

      <button
        className="save-settings-btn bottom-save"
        onClick={saveSettings}
        disabled={saving}
      >
        {saving ? "Saving..." : "Save All Settings"}
      </button>

      {/* PAGE STYLES */}

      <style>{`

        .settings-page {
          padding: 30px;
          max-width: 1000px;
          margin: auto;
          color: var(--text-primary);
        }

        .settings-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 15px;
          margin-bottom: 25px;
        }

        .settings-header h1 {
          color: var(--text-primary);
          margin-bottom: 6px;
        }

        .settings-header p,
        .settings-card p {
          color: var(--text-muted);
          font-size: 14px;
        }

        .settings-card {
          background: var(--white);
          color: var(--text-primary);
          border: 1px solid var(--border-color);
          border-radius: 14px;
          padding: 24px;
          margin-bottom: 22px;
        }

        .settings-card h2 {
          font-size: 18px;
          margin-top: 0;
          color: var(--text-primary);
        }

        .setting-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 20px;
          padding: 15px 0;
          border-bottom: 1px solid var(--border-color);
        }

        .setting-row:last-child {
          border-bottom: none;
        }

        .setting-row label {
          font-size: 14px;
          font-weight: 500;
          color: var(--text-primary);
        }

        .setting-row input:not([type="checkbox"]):not([type="color"]),
        .setting-row select {
          padding: 9px 12px;
          border: 1px solid var(--border-color);
          border-radius: 8px;
          background: var(--white);
          color: var(--text-primary);
          min-width: 130px;
        }

        .setting-row input[type="checkbox"] {
          width: 19px;
          height: 19px;
          accent-color: var(--pink-medium);
          cursor: pointer;
        }

        .setting-row input[type="color"] {
          width: 55px;
          height: 35px;
          border: none;
          cursor: pointer;
          background: transparent;
        }

        .save-settings-btn {
          background: var(--pink-medium);
          color: white;
          border: none;
          border-radius: 9px;
          padding: 12px 22px;
          font-weight: 600;
          cursor: pointer;
        }

        .save-settings-btn:hover {
          background: var(--pink-dark);
        }

        .save-settings-btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }

        .bottom-save {
          width: 100%;
          margin-bottom: 30px;
        }

        .settings-message {
          padding: 12px;
          background: var(--pink-soft);
          color: var(--text-primary);
          border-radius: 8px;
          margin-bottom: 20px;
        }

        .settings-loading {
          padding: 40px;
          text-align: center;
          color: var(--text-primary);
        }

        @media (max-width: 600px) {

          .settings-page {
            padding: 15px;
          }

          .settings-header {
            align-items: flex-start;
            flex-direction: column;
          }

          .setting-row {
            gap: 10px;
          }

        }

      `}</style>

    </div>
  );
}