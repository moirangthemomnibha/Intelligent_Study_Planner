import { useState } from "react";
import { api } from "../api/client";

export function AIAgentPanel() {
  const [intent, setIntent] = useState("");
  const [proposal, setProposal] = useState(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  async function askAgent() {
    if (!intent.trim()) {
      setError("Please enter your instructions first.");
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");
    setProposal(null);

    try {
      const profile = await api.getStudentProfile();

      if (!profile?.id) {
        throw new Error("Student profile not found. Please log in again.");
      }

      const token = localStorage.getItem("access_token");

      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1"}/agent/run`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({
            student_id: profile.id,
            intent,
            approval_mode: "ask_before_changes",
            available_minutes_per_day: 180,
            horizon_days: 7,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Agent request failed.");
      }

      setProposal(data);

    } catch (err) {
      console.error("AI agent error:", err);
      setError(err.message || "Unable to contact the study agent.");
    } finally {
      setLoading(false);
    }
  }

  async function approvePlan() {
    const studyPlan = proposal?.actions?.find(
      (action) => action.type === "study_plan"
    );

    if (!studyPlan) {
      setError("No study plan was found in the proposal.");
      return;
    }

    setSaving(true);
    setError("");
    setMessage("");

    try {
      const profile = await api.getStudentProfile();

      if (!profile?.id) {
        throw new Error("Student profile not found. Please log in again.");
      }

      const token = localStorage.getItem("access_token");

      const response = await fetch(
        `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1"}/agent/confirm`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
          body: JSON.stringify({
            student_id: profile.id,
            start_date: studyPlan.start_date,
            horizon_days: studyPlan.horizon_days,
            available_minutes_per_day:
              studyPlan.available_minutes_per_day,
            generated_plan: studyPlan.sessions,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Unable to save study plan.");
      }

      setMessage(
        `Success! ${data.saved_sessions} study session(s) saved.`
      );

      setProposal(null);
      setIntent("");

    } catch (err) {
      console.error("AI agent save error:", err);
      setError(err.message || "Unable to save study plan.");
    } finally {
      setSaving(false);
    }
  }

  const studyPlan = proposal?.actions?.find(
    (action) => action.type === "study_plan"
  );

  const recommendation = proposal?.actions?.find(
    (action) => action.type === "recommendation"
  );

  const deadlineRisks = proposal?.actions?.find(
    (action) => action.type === "deadline_risks"
  );

  return (
    <section className="panel ai-agent-panel">
      <h2>✧ AI Study Agent</h2>

      <p>
        Tell your AI agent about your available time, completed topics,
        missed sessions or upcoming exams.
      </p>

      <textarea
        value={intent}
        onChange={(e) => setIntent(e.target.value)}
        placeholder="Example: I have only 30 minutes today. Adjust my study plan."
        rows={5}
        style={{
          width: "100%",
          padding: "14px",
          borderRadius: "10px",
          border: "1px solid #e5b8c7",
          marginTop: "15px",
          resize: "vertical",
          boxSizing: "border-box",
        }}
      />

      <button
        type="button"
        onClick={askAgent}
        disabled={loading || saving}
        style={{ marginTop: "12px" }}
      >
        {loading ? "Agent is thinking..." : "✧ Ask Study Agent"}
      </button>

      {error && (
        <p style={{ color: "red", marginTop: "15px" }}>
          {error}
        </p>
      )}

      {message && (
        <p style={{ color: "green", marginTop: "15px" }}>
          {message}
        </p>
      )}

      {proposal && (
        <div style={{ marginTop: "25px" }}>
          <h3>Agent Proposal</h3>

          <p>{proposal.summary}</p>

          {recommendation && (
            <div className="panel" style={{ marginTop: "15px" }}>
              <h4>Next Study Recommendation</h4>
              <p>{recommendation.message}</p>

              <ul>
                {recommendation.reasons?.map((reason, index) => (
                  <li key={index}>{reason}</li>
                ))}
              </ul>
            </div>
          )}

          {deadlineRisks?.risks?.length > 0 && (
            <div className="panel" style={{ marginTop: "15px" }}>
              <h4>⚠ Deadline Risks</h4>
              <ul>
                {deadlineRisks.risks.map((risk, index) => (
                  <li key={index}>{risk}</li>
                ))}
              </ul>
            </div>
          )}

          {studyPlan && (
            <div className="panel" style={{ marginTop: "15px" }}>
              <h4>Proposed Study Schedule</h4>

              {studyPlan.sessions.length === 0 ? (
                <p>No study sessions could be scheduled.</p>
              ) : (
                studyPlan.sessions.map((item, index) => (
                  <div
                    key={index}
                    style={{
                      padding: "12px",
                      marginBottom: "10px",
                      borderRadius: "8px",
                      background: "#fff5f7",
                    }}
                  >
                    <strong>{item.topic_name}</strong>
                    <p>
                      Date: {item.day}
                      <br />
                      Duration: {item.duration_minutes} minutes
                    </p>
                    <small>{item.reason}</small>
                  </div>
                ))
              )}
            </div>
          )}

          {proposal.requires_confirmation && studyPlan && (
            <button
              type="button"
              onClick={approvePlan}
              disabled={saving || studyPlan.sessions.length === 0}
              style={{ marginTop: "15px" }}
            >
              {saving ? "Saving Plan..." : "✓ Approve & Save Plan"}
            </button>
          )}
        </div>
      )}

      <p className="muted" style={{ marginTop: "20px" }}>
        Your agent proposes changes first. You approve the plan before
        it is saved.
      </p>
    </section>
  );
}