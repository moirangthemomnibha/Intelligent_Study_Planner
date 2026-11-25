import { useState } from "react";
import { api } from "../api/client";
import "./AuthPages.css";

export default function RegisterPage({ onNavigate }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  // PASSWORD REQUIREMENTS
  const passwordRules = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    symbol: /[^A-Za-z0-9\s]/.test(password),
  };

  const isPasswordValid = Object.values(passwordRules).every(Boolean);

  // REGISTRATION
  const handleRegister = async (e) => {
    e.preventDefault();

    if (!isPasswordValid) {
      alert("Please meet all password requirements.");
      return;
    }

    if (password !== confirmPassword) {
      alert("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);

      await api.register({ email, password });

      localStorage.setItem("pending_verification_email", email);
      onNavigate("verify");

    } catch (error) {
      alert(error.message);

    } finally {
      setLoading(false);
    }
  };

  // PASSWORD REQUIREMENT COMPONENT
  const PasswordRequirement = ({ valid, children }) => (
    <p className={valid ? "valid" : "invalid"}>
      {valid ? "✓" : "○"} {children}
    </p>
  );

  // EYE ICONS
  const EyeIcon = ({ visible }) => (
    visible ? (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" />
        <circle cx="12" cy="12" r="3" />
      </svg>
    ) : (
      <svg viewBox="0 0 24 24" aria-hidden="true">
        <path d="M3 3l18 18M10.6 10.6a2 2 0 0 0 2.8 2.8M9.9 5.2A10.5 10.5 0 0 1 12 5c5.5 0 9 7 9 7a15 15 0 0 1-3.1 3.8M6.2 6.2C3.8 7.8 2 12 2 12s3.5 7 10 7c1 0 2-.2 2.9-.5" />
      </svg>
    )
  );

  return (
    <main className="auth-page">
      <div className="auth-brand">
        <img src="/study_planner_branding.png"
            alt="Intelligent Adaptive Study Planner"/>
      </div>
      <section className="auth-card">

        <div className="auth-heading">
          <h1>Create Account 🌸</h1>
          <p>Start organising your learning journey.</p>
        </div>

        <form onSubmit={handleRegister}>

          {/* EMAIL */}
          <div className="auth-field">
            <label htmlFor="register-email">Email Address</label>

            <input
              id="register-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email address"
              autoComplete="email"
              required
            />
          </div>

          {/* PASSWORD */}
          <div className="auth-field">
            <label htmlFor="register-password">Password</label>

            <div className="password-wrapper">
              <input
                id="register-password"
                type={showPassword ? "text" : "password"}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Create a password"
                autoComplete="new-password"
                required
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword((value) => !value)}
                aria-label={showPassword ? "Hide password" : "Show password"}
              >
                <EyeIcon visible={showPassword} />
              </button>
            </div>

            {/* PASSWORD REQUIREMENTS */}
            <div className="password-requirements">
              <p>Password must contain:</p>

              <PasswordRequirement valid={passwordRules.length}>
                At least 8 characters
              </PasswordRequirement>

              <PasswordRequirement valid={passwordRules.uppercase}>
                One uppercase letter (A-Z)
              </PasswordRequirement>

              <PasswordRequirement valid={passwordRules.lowercase}>
                One lowercase letter (a-z)
              </PasswordRequirement>

              <PasswordRequirement valid={passwordRules.number}>
                One number (0-9)
              </PasswordRequirement>

              <PasswordRequirement valid={passwordRules.symbol}>
                One special character (!@#$%)
              </PasswordRequirement>
            </div>
          </div>

          {/* CONFIRM PASSWORD */}
          <div className="auth-field">
            <label htmlFor="confirm-password">Confirm Password</label>

            <div className="password-wrapper">
              <input
                id="confirm-password"
                type={showConfirmPassword ? "text" : "password"}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm your password"
                autoComplete="new-password"
                required
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() =>
                  setShowConfirmPassword((value) => !value)
                }
                aria-label={
                  showConfirmPassword
                    ? "Hide confirm password"
                    : "Show confirm password"
                }
              >
                <EyeIcon visible={showConfirmPassword} />
              </button>
            </div>
          </div>

          {/* REGISTER BUTTON */}
          <button
            type="submit"
            className="auth-submit"
            disabled={loading}
          >
            {loading ? "Creating Account..." : "Create Account"}
          </button>

        </form>

        {/* FOOTER */}
        <div className="auth-footer">
          Already have an account?{" "}

          <button
            type="button"
            className="auth-link"
            onClick={() => onNavigate("login")}
          >
            Sign in
          </button>
        </div>

      </section>
    </main>
  );
}