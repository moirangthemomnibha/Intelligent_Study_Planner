import { useState } from "react";
import { api } from "../api/client";

export default function VerifyEmailPage({ onNavigate }) {
  const [otp, setOtp] = useState("");
  const [loading, setLoading] = useState(false);

  const email = localStorage.getItem("pending_verification_email");

  const handleVerify = async (e) => {
    e.preventDefault();

    if (!email) {
      alert("Registration email not found. Please register again.");
      onNavigate("register");
      return;
    }

    try {
      setLoading(true);

      await api.verifyEmail({ email, otp });

      localStorage.removeItem("pending_verification_email");

      alert("Email verified successfully! Please log in.");

      onNavigate("login");

    } catch (error) {
      alert(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    try {
      await api.resendOTP({ email });
      alert("A new verification code has been sent.");
    } catch (error) {
      alert(error.message);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1>Verify Your Email 🌸</h1>

        <p>
          Enter the six-digit verification code sent to:
        </p>

        <strong>{email || "Email not found"}</strong>

        <form onSubmit={handleVerify}>
          <label>Verification Code</label>

          <input
            type="text"
            value={otp}
            onChange={(e) =>
              setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))
            }
            placeholder="Enter 6-digit OTP"
            maxLength={6}
            required
          />

          <button
            type="submit"
            disabled={loading || otp.length !== 6}
          >
            {loading ? "Verifying..." : "Verify Email"}
          </button>
        </form>

        <button type="button" onClick={handleResend}>
          Resend Verification Code
        </button>

        <p>
          Wrong email?{" "}
          <button onClick={() => onNavigate("register")}>
            Register Again
          </button>
        </p>
      </div>
    </div>
  );
}