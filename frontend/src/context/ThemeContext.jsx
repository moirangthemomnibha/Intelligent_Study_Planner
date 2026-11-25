import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

const ThemeContext = createContext(null);

const THEME_STORAGE_KEY = "study_planner_theme";
const DEFAULT_ACCENT = "#D98FA5";

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(() => {
    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);

    return ["light", "dark", "system"].includes(savedTheme)
      ? savedTheme
      : "system";
  });

  const [accentColor, setAccentColor] = useState(() => {
    return localStorage.getItem("study_planner_accent_color") || DEFAULT_ACCENT;
  });
  const [fontSize, setFontSize] = useState(() => {
    const savedFontSize = localStorage.getItem("study_planner_font_size");

    return ["small", "medium", "large"].includes(savedFontSize)
        ? savedFontSize
        : "medium";
    });

    // SAVE FONT SIZE LOCALLY

useEffect(() => {
  localStorage.setItem("study_planner_font_size", fontSize);
}, [fontSize]);

  // UPDATE THEME
  function setTheme(value) {
    if (!["light", "dark", "system"].includes(value)) return;

    setThemeState(value);
    localStorage.setItem(THEME_STORAGE_KEY, value);
  }

  // APPLY THEME
  useEffect(() => {
    const root = document.documentElement;

    const mediaQuery = window.matchMedia(
      "(prefers-color-scheme: dark)"
    );

    function applyTheme() {
      const isDark =
        theme === "dark" ||
        (theme === "system" && mediaQuery.matches);

      root.setAttribute(
        "data-theme",
        isDark ? "dark" : "light"
      );

      root.style.colorScheme = isDark ? "dark" : "light";
    }

    applyTheme();

    if (theme === "system") {
      mediaQuery.addEventListener("change", applyTheme);
    }

    return () => {
      mediaQuery.removeEventListener("change", applyTheme);
    };
  }, [theme]);

  // APPLY ACCENT COLOR GLOBALLY
useEffect(() => {
  const root = document.documentElement;

  localStorage.setItem("study_planner_accent_color", accentColor);

  root.style.setProperty("--accent-color", accentColor);
  root.style.setProperty("--accent-hover", accentColor);

  root.style.setProperty("--app-accent", accentColor);
  root.style.setProperty(
    "--app-accent-hover",
    `color-mix(in srgb, ${accentColor}, black 15%)`
  );

  root.style.setProperty("--pink-medium", accentColor);
  root.style.setProperty("--pink-dark", `color-mix(in srgb, ${accentColor}, black 15%)`);

  root.style.setProperty("--app-progress-fill", accentColor);

}, [accentColor]);

  // APPLY FONT SIZE TO MAIN APPLICATION ONLY
  useEffect(() => {
    const root = document.documentElement;

    root.style.setProperty(
      "--app-font-scale",
      fontSize === "small"
        ? "0.90"
        : fontSize === "large"
          ? "1.12"
          : "1"
    );

    root.setAttribute("data-app-font-size", fontSize);

  }, [fontSize]);

  return (
    <ThemeContext.Provider
      value={{
        theme,
        setTheme,
        accentColor,
        setAccentColor,
        fontSize,
        setFontSize,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);

  if (!context) {
    throw new Error(
      "useTheme must be used inside ThemeProvider"
    );
  }

  return context;
}