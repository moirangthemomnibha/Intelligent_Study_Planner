import { useEffect, useState } from "react";
import { api } from "../api/client";
import "./AuthPages.css";

export default function LoginPage({ onLogin, onNavigate }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);
  const [loading, setLoading] = useState(false);
  const [googleLoading, setGoogleLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      setLoading(true);

      const data = await api.login({ email, password });

      api.saveToken(data.access_token);
      localStorage.setItem("remember_me", String(rememberMe));

      onLogin(data);
    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;

    if (!clientId) {
      console.error("Google Client ID is missing.");
      return;
    }

    const script = document.createElement("script");
    script.src = "https://accounts.google.com/gsi/client";
    script.async = true;
    script.defer = true;

    script.onload = () => {
      if (!window.google) return;

      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: async (response) => {
          try {
            setGoogleLoading(true);

            const data = await api.googleLogin(response.credential);

            api.saveToken(data.access_token);
            localStorage.setItem("remember_me", "true");

            onLogin(data);
          } catch (error) {
            alert(error.message);
          } finally {
            setGoogleLoading(false);
          }
        },
      });

      const button = document.getElementById("google-signin-button");

      if (button) {
        window.google.accounts.id.renderButton(button, {
          theme: "outline",
          size: "large",
          shape: "rectangular",
          text: "continue_with",
          logo_alignment: "center",
          width: 350,
        });
      }
    };

    document.head.appendChild(script);

    return () => {
      document.head.removeChild(script);
    };
  }, [onLogin]);

  return (
    <main className="auth-page">
      <div className="auth-brand">
        <img
          src="/study_planner_branding.png"
          alt="Intelligent Adaptive Study Planner"
        />
      </div>

      <section className="auth-card">
        <div className="auth-heading">
          <h1>Welcome Back 🌸</h1>
          <p>Sign in to continue your learning journey.</p>
        </div>

        <form onSubmit={handleLogin}>
          <div className="auth-field">
            <label htmlFor="login-email">Email Address</label>
            <input
              id="login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email address"
              autoComplete="username"
              required
            />
          </div>

          <div className="auth-field">
            <label htmlFor="login-password">Password</label>

            <div className="password-wrapper">
              <input
                id="login-password"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                autoComplete="current-password"
                required
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword((previous) => !previous)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>
          </div>

          <div className="auth-options">
            <label className="remember-option">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
              />
              <span>Remember me</span>
            </label>

            <button
              type="button"
              className="auth-link"
              onClick={() => onNavigate("forgot")}
            >
              Forgot password?
            </button>
          </div>

          <button
            type="submit"
            className="auth-submit"
            disabled={loading}
          >
            {loading ? "Signing in..." : "Sign In"}
          </button>
        </form>

        <div className="auth-divider">
          <span>OR</span>
        </div>

        <div className="google-signin-container">
          <div id="google-signin-button"></div>
          {googleLoading && <p>Signing in with Google...</p>}
        </div>

        <div className="auth-footer">
          Don't have an account?{" "}
          <button
            type="button"
            className="auth-link"
            onClick={() => onNavigate("register")}
          >
            Create account
          </button>
        </div>
      </section>
    </main>
  );
}