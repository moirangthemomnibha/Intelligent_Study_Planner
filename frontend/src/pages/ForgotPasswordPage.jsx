import { useState } from "react";
import { api } from "../api/client";
import "./AuthPages.css";

export default function ForgotPasswordPage({ onNavigate }) {
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [step, setStep] = useState(1);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  // PASSWORD VALIDATION
  const passwordRules = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    number: /[0-9]/.test(password),
    symbol: /[^A-Za-z0-9\s]/.test(password),
  };

  const isPasswordValid = Object.values(passwordRules).every(Boolean);

  // STEP 1: SEND RESET OTP
  async function handleSendOTP(e) {
    e.preventDefault();

    setError("");
    setSuccess("");

    const normalizedEmail = email.trim().toLowerCase();

    try {
      setLoading(true);

      await api.forgotPassword({
        email: normalizedEmail,
      });

      setEmail(normalizedEmail);
      setStep(2);

      setSuccess(
        "If an account exists, a password reset code has been sent to your email."
      );
    } catch (err) {
      setError(err.message || "Unable to send reset code.");
    } finally {
      setLoading(false);
    }
  }

  // STEP 2: RESET PASSWORD
  async function handleResetPassword(e) {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (otp.length !== 6) {
      setError("Please enter the six-digit verification code.");
      return;
    }

    if (!isPasswordValid) {
      setError("Please meet all password requirements.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);

      await api.resetPassword({
        email,
        otp,
        new_password: password,
      });

      setSuccess(
        "Password reset successfully! You can now sign in."
      );

      setOtp("");
      setPassword("");
      setConfirmPassword("");

      setTimeout(() => {
        onNavigate("login");
      }, 1800);

    } catch (err) {
      setError(err.message || "Unable to reset password.");
    } finally {
      setLoading(false);
    }
  }

  // PASSWORD REQUIREMENT COMPONENT
  function PasswordRequirement({ valid, children }) {
    return (
      <p className={valid ? "valid" : "invalid"}>
        {valid ? "✓" : "○"} {children}
      </p>
    );
  }

  // PAGE UI
  return (
    <main className="auth-page">
      <section className="auth-card">

        <div className="auth-heading">
          <h1>Reset Password 🌸</h1>

          <p>
            {step === 1
              ? "Enter your registered email to receive a reset code."
              : "Enter your verification code and create a new password."}
          </p>
        </div>

        {error && (
          <div className="auth-message error-message" role="alert">
            {error}
          </div>
        )}

        {success && (
          <div className="auth-message success-message" role="status">
            {success}
          </div>
        )}

        {/* STEP 1: EMAIL FORM */}
        {step === 1 && (
          <form onSubmit={handleSendOTP}>

            <div className="auth-field">
              <label htmlFor="reset-email">
                Email Address
              </label>

              <input
                id="reset-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your registered email"
                autoComplete="email"
                required
              />
            </div>

            <button
              type="submit"
              className="auth-submit"
              disabled={loading}
            >
              {loading ? "Sending Code..." : "Send Reset Code"}
            </button>

          </form>
        )}

        {/* STEP 2: RESET PASSWORD FORM */}
        {step === 2 && (
          <form onSubmit={handleResetPassword}>

            <div className="auth-field">
              <label htmlFor="reset-otp">
                Verification Code
              </label>

              <input
                id="reset-otp"
                type="text"
                inputMode="numeric"
                value={otp}
                onChange={(e) =>
                  setOtp(
                    e.target.value.replace(/\D/g, "").slice(0, 6)
                  )
                }
                placeholder="Enter six-digit code"
                maxLength={6}
                autoComplete="one-time-code"
                required
              />
            </div>

            <div className="auth-field">
              <label htmlFor="new-password">
                New Password
              </label>

              <div className="password-wrapper">
                <input
                  id="new-password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Create a new password"
                  autoComplete="new-password"
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowPassword((prev) => !prev)
                  }
                  aria-label={
                    showPassword ? "Hide password" : "Show password"
                  }
                >
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>

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
                  One special character
                </PasswordRequirement>
              </div>
            </div>

            <div className="auth-field">
              <label htmlFor="confirm-new-password">
                Confirm New Password
              </label>

              <div className="password-wrapper">
                <input
                  id="confirm-new-password"
                  type={showConfirmPassword ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) =>
                    setConfirmPassword(e.target.value)
                  }
                  placeholder="Confirm your new password"
                  autoComplete="new-password"
                  required
                />

                <button
                  type="button"
                  className="password-toggle"
                  onClick={() =>
                    setShowConfirmPassword((prev) => !prev)
                  }
                  aria-label={
                    showConfirmPassword
                      ? "Hide password"
                      : "Show password"
                  }
                >
                  {showConfirmPassword ? "Hide" : "Show"}
                </button>
              </div>
            </div>

            <button
              type="submit"
              className="auth-submit"
              disabled={
                loading ||
                otp.length !== 6 ||
                !isPasswordValid ||
                password !== confirmPassword
              }
            >
              {loading ? "Resetting Password..." : "Reset Password"}
            </button>

            <button
              type="button"
              className="auth-link"
              onClick={() => {
                setStep(1);
                setOtp("");
                setError("");
                setSuccess("");
              }}
            >
              Change Email Address
            </button>

          </form>
        )}

        <div className="auth-footer">
          Remember your password?{" "}

          <button
            type="button"
            className="auth-link"
            onClick={() => onNavigate("login")}
          >
            Sign In
          </button>
        </div>

      </section>
    </main>
  );
}