import { useEffect, useState } from "react";
import { usePlanner } from "../context/PlannerContext";
import { api } from "../api/client";

const STUDENT_ID = 3;

export function PlannerPage() {
  const {
    subjects,
    setSubjects,
    topics,
    setTopics,
    plan,
    setPlan,
    overallProgress,
    completedTopics,
    totalTopics,
    inProgressTopics,
    notStartedTopics,
  } = usePlanner();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const [selectedSubject, setSelectedSubject] = useState("");
  const [topicName, setTopicName] = useState("");
  const [difficulty, setDifficulty] = useState(3);
  const [estimatedMinutes, setEstimatedMinutes] = useState(60);

  const [availableMinutes, setAvailableMinutes] = useState(180);
  const [horizonDays, setHorizonDays] = useState(7);
  const [generating, setGenerating] = useState(false);

  // LOAD DATA

  async function loadData() {
    try {
      setError("");

      const subjectData = await api.getSubjects(STUDENT_ID);
      setSubjects(subjectData);

      const topicResults = await Promise.all(
        subjectData.map((subject) => api.getTopics(subject.id))
      );

      setTopics(topicResults.flat());

      const sessionData = await api.getSessions(STUDENT_ID);
      setPlan(sessionData);

    } catch (err) {
      console.error(err);
      setError(err.message || "Unable to load planner data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadData();
  }, []);

  // ADD TOPIC

  async function handleAddTopic(e) {
    e.preventDefault();

    if (!selectedSubject || !topicName.trim()) {
      setError("Select a subject and enter a topic name.");
      return;
    }

    try {
      setError("");
      setMessage("");

      await api.createTopic({
        subject_id: Number(selectedSubject),
        name: topicName.trim(),
        estimated_minutes: Number(estimatedMinutes),
        difficulty: Number(difficulty),
      });

      setTopicName("");
      setEstimatedMinutes(60);
      setDifficulty(3);

      await loadData();
      setMessage("Topic added successfully!");

    } catch (err) {
      console.error(err);
      setError(err.message || "Could not add topic.");
    }
  }

  // UPDATE TOPIC COMPLETION

  async function toggleTopic(topic) {
    try {
      setError("");
      setMessage("");

      const completion =
        Number(topic.completion_percent) >= 100 ? 0 : 100;

      await api.updateTopic(topic.id, {
        ...topic,
        completion_percent: completion,
      });

      await loadData();

    } catch (err) {
      console.error(err);
      setError(err.message || "Could not update topic.");
    }
  }

  // GENERATE LONG-TERM STUDY PLAN

  async function handleGeneratePlan() {
    console.log("GENERATE BUTTON CLICKED");
    if (generating) return;

    setGenerating(true);
    setError("");
    setMessage("");

    try {
      if (topics.length === 0) {
        throw new Error(
          "Please add at least one topic before generating your study plan."
        );
      }

      const minutes = Number(availableMinutes);
      const days = Number(horizonDays);

      if (!Number.isInteger(minutes) || minutes <= 0) {
        throw new Error("Enter valid available study minutes.");
      }

      if (!Number.isInteger(days) || days < 1 || days > 30) {
        throw new Error(
          "Planning period must be between 1 and 30 days."
        );
      }

      const result = await api.generatePlan({
        student_id: STUDENT_ID,
        available_minutes_per_day: minutes,
        horizon_days: days,
      });

      await loadData();

      setMessage(
        `Your ${days}-day study plan was generated successfully!`
      );

      console.log("Generated study plan:", result);

    } catch (err) {
      console.error(err);
      setError(err.message || "Could not generate your study plan.");
    } finally {
      setGenerating(false);
    }
  }

  // UPDATE STUDY SESSION STATUS

  async function updateSession(sessionId, status) {
    try {
      setError("");

      await api.updateSessionStatus(sessionId, status);

      await loadData();

    } catch (err) {
      console.error(err);
      setError(err.message || "Could not update study session.");
    }
  }

  // LOADING SCREEN

  if (loading) {
    return (
      <div className="planner-loading">
        <p>Loading your study planner...</p>
      </div>
    );
  }

  return (
    <div className="planner-page">

      {/* PAGE HEADER */}

      <div className="planner-page-header">
        <h1>Study Planner</h1>
        <p>
          Organize your syllabus, track progress and generate study plans.
        </p>
      </div>

      {/* MESSAGES */}

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {message && (
        <div className="success-message">
          {message}
        </div>
      )}

      {/* OVERALL PROGRESS */}

      <section className="panel progress-panel">

        <h2>Overall Syllabus Progress</h2>

        <div
          className="progress-circle"
          style={{
            background: `conic-gradient(
              #D98FA5 ${overallProgress}%,
              #F8DCE5 ${overallProgress}%
            )`,
          }}
        >
          <strong>{overallProgress}%</strong>
          <span>Completed</span>
        </div>

        <div className="planner-statistics">

          <div className="stat-item">
            <strong>{totalTopics}</strong>
            <span>Total Topics</span>
          </div>

          <div className="stat-item">
            <strong>{completedTopics}</strong>
            <span>Completed</span>
          </div>

          <div className="stat-item">
            <strong>{inProgressTopics}</strong>
            <span>In Progress</span>
          </div>

          <div className="stat-item">
            <strong>{notStartedTopics}</strong>
            <span>Not Started</span>
          </div>

        </div>
      </section>

      {/* ADD TOPICS */}

      <section className="panel add-topic-panel">

        <div className="section-heading">
          <h2>Add Topics to Your Syllabus</h2>
          <p>
            Add the topics from each subject to organize your study schedule.
          </p>
        </div>

        {subjects.length === 0 ? (

          <div className="empty-state">
            <p>Add a subject first from the Subjects page.</p>
          </div>

        ) : (

          <form className="topic-form" onSubmit={handleAddTopic}>

            <div className="form-group">
              <label>Select Subject</label>

              <select
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
                required
              >
                <option value="">Choose a subject</option>

                {subjects.map((subject) => (
                  <option key={subject.id} value={subject.id}>
                    {subject.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Topic Name</label>

              <input
                type="text"
                value={topicName}
                onChange={(e) => setTopicName(e.target.value)}
                placeholder="e.g. Introduction to DBMS"
                required
              />
            </div>

            <div className="form-group">
              <label>Difficulty Level</label>

              <select
                value={difficulty}
                onChange={(e) => setDifficulty(Number(e.target.value))}
              >
                <option value="1">1 - Very Easy</option>
                <option value="2">2 - Easy</option>
                <option value="3">3 - Medium</option>
                <option value="4">4 - Hard</option>
                <option value="5">5 - Very Hard</option>
              </select>
            </div>

            <div className="form-group">
              <label>Estimated Study Time (minutes)</label>

              <input
                type="number"
                min="1"
                value={estimatedMinutes}
                onChange={(e) => setEstimatedMinutes(e.target.value)}
                required
              />
            </div>

            <div className="form-submit">
              <button type="submit">
                + Add Topic
              </button>
            </div>

          </form>
        )}
      </section>

      {/* SYLLABUS CHECKLIST */}

      <section className="panel syllabus-panel">

        <h2>My Syllabus Checklist</h2>

        {subjects.length === 0 ? (

          <div className="empty-state">
            No subjects available yet.
          </div>

        ) : (

          subjects.map((subject) => {

            const subjectTopics = topics.filter(
              (topic) => topic.subject_id === subject.id
            );

            return (
              <div key={subject.id} className="subject-topic-group">

                <h3>{subject.name}</h3>

                {subjectTopics.length === 0 ? (

                  <p className="empty-topics">
                    No topics added yet.
                  </p>

                ) : (

                  <div className="topic-list">

                    {subjectTopics.map((topic) => (

                      <label key={topic.id} className="topic-checkbox">

                        <input
                          type="checkbox"
                          checked={
                            Number(topic.completion_percent) >= 100
                          }
                          onChange={() => toggleTopic(topic)}
                        />

                        <div className="topic-details">
                          <span className="topic-name">
                            {topic.name}
                          </span>

                          <span className="topic-meta">
                            Difficulty: {topic.difficulty}/5
                            {" · "}
                            {topic.estimated_minutes} minutes
                          </span>
                        </div>

                      </label>

                    ))}

                  </div>
                )}
              </div>
            );
          })
        )}
      </section>

      {/* GENERATE LONG-TERM STUDY PLAN */}

      <section className="panel generate-plan-panel">

        <div className="section-heading">
          <h2>Generate Study Plan</h2>

          <p>
            Create a structured study timetable for your selected planning period.
          </p>
        </div>

        <div className="study-plan-form">

          <div className="form-group">
            <label htmlFor="available-minutes">
              Available Study Time Per Day
            </label>

            <div className="input-with-unit">

              <input
                id="available-minutes"
                type="number"
                min="1"
                value={availableMinutes}
                onChange={(e) => setAvailableMinutes(e.target.value)}
              />

              <span>Minutes</span>

            </div>
          </div>

          <div className="form-group">
            <label htmlFor="horizon-days">
              Planning Period
            </label>

            <div className="input-with-unit">

              <input
                id="horizon-days"
                type="number"
                min="1"
                max="30"
                value={horizonDays}
                onChange={(e) => setHorizonDays(e.target.value)}
              />

              <span>Days</span>

            </div>
          </div>

          <div className="generate-button-wrapper">

            <button
              type="button"
              className="generate-plan-button"
              onClick={handleGeneratePlan}
              style={{
                pointerEvents: "auto",
                cursor: "pointer",
                opacity: 1,
                position: "relative",
                zIndex: 10,
              }}
            >
              {generating
                ? "Generating Your Study Plan..."
                : "Generate My Study Plan"}
            </button>

          </div>

        </div>
      </section>

      {/* STUDY SESSIONS */}

      <section className="panel study-sessions-panel">

        <div className="section-heading">
          <h2>My Study Sessions</h2>

          <p>
            View your scheduled study sessions and track your progress.
          </p>
        </div>

        {plan.length === 0 ? (

          <div className="empty-state">
            <h3>No Study Sessions Yet</h3>

            <p>
              Your generated study sessions will appear here.
              Add topics and generate a study plan to get started.
            </p>
          </div>

        ) : (

          <div className="study-session-list">

            {plan.map((session) => {

              const topic = topics.find(
                (item) => item.id === session.topic_id
              );

              const subject = subjects.find(
                (item) => item.id === topic?.subject_id
              );

              const normalizedStatus = String(
                session.status || "planned"
              ).toLowerCase();

              const statusClass =
                normalizedStatus === "completed"
                  ? "completed"
                  : normalizedStatus === "missed"
                    ? "missed"
                    : "pending";

              const statusLabel =
                normalizedStatus.charAt(0).toUpperCase() +
                normalizedStatus.slice(1);

              return (

                <article
                  key={session.id}
                  className="study-session-card"
                >

                  <div className="session-details">

                    <h3>
                      {topic?.name || "Study Session"}
                    </h3>

                    <p className="session-subject">
                      Subject: {subject?.name || "Not available"}
                    </p>

                    <div className="session-meta">
                      <span>
                        📅 {session.planned_date}
                      </span>

                      <span>
                        ⏱ {session.planned_minutes} minutes
                      </span>
                    </div>

                  </div>

                  <div className="session-right">

                    <span className={`session-status ${statusClass}`}>
                      {statusLabel}
                    </span>

                    {normalizedStatus === "planned" && (

                      <div className="session-actions">

                        <button
                          type="button"
                          onClick={() =>
                            updateSession(session.id, "completed")
                          }
                        >
                          Complete
                        </button>

                        <button
                          type="button"
                          className="missed-button"
                          onClick={() =>
                            updateSession(session.id, "missed")
                          }
                        >
                          Mark as Missed
                        </button>

                      </div>
                    )}

                  </div>

                </article>
              );
            })}

          </div>
        )}
      </section>

    </div>
  );
}