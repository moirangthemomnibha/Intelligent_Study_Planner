import { useEffect, useState } from "react";
import { StatCard } from "../components/StatCard";
import { api } from "../api/client";

export function DashboardPage() {
  const [student, setStudent] = useState(null);
  const [subjects, setSubjects] = useState([]);
  const [topics, setTopics] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [recommendation, setRecommendation] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadDashboard() {
    try {
      setLoading(true);
      setError("");

      setSubjects([]);
      setTopics([]);
      setSessions([]);
      setTasks([]);
      setRecommendation(null);

      const profile = await api.getStudentProfile();

      if (!profile || !profile.id) {
        throw new Error("Student profile not found.");
      }

      const studentId = profile.id;

      setStudent({
        ...profile,
        name: profile.full_name || "Student",
        id: studentId,
      });

      const [subjectData, sessionData, taskData, aiData] =
        await Promise.all([
          api.getSubjects(studentId),
          api.getSessions(studentId),
          api.getTasks(studentId),
          api.getRecommendation(studentId),
        ]);

      setSubjects(subjectData);
      setSessions(sessionData);
      setTasks(taskData);
      setRecommendation(aiData);

      const topicResults = await Promise.all(
        subjectData.map((subject) => api.getTopics(subject.id))
      );

      setTopics(topicResults.flat());

    } catch (err) {
      console.error("Dashboard loading error:", err);
      setError(err.message || "Unable to load dashboard.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  // ==========================================
  // DASHBOARD STATISTICS
  // ==========================================

  const totalSubjects = subjects.length;
  const totalTopics = topics.length;

  const completedTopics = topics.filter(
    (topic) => Number(topic.completion_percent) >= 100
  ).length;

  const inProgressTopics = topics.filter(
    (topic) =>
      Number(topic.completion_percent) > 0 &&
      Number(topic.completion_percent) < 100
  ).length;

  const notStartedTopics = topics.filter(
    (topic) => Number(topic.completion_percent || 0) === 0
  ).length;

  const overallProgress =
    totalTopics > 0
      ? Math.round(
          topics.reduce(
            (total, topic) =>
              total + Number(topic.completion_percent || 0),
            0
          ) / totalTopics
        )
      : 0;

  const completedSessions = sessions.filter(
    (session) =>
      String(session.status).trim().toLowerCase() === "completed"
  ).length;

  // ==========================================
  // TASK STATISTICS
  // ==========================================

  const totalTasks = tasks.length;

  const completedTasks = tasks.filter(
    (task) => task.status === "Completed"
  ).length;

  const pendingTasks = tasks.filter(
    (task) => task.status !== "Completed"
  ).length;

  const todayDate = new Date();
  todayDate.setHours(0, 0, 0, 0);

  const upcomingTasks = tasks
    .filter((task) => {
      if (!task.deadline || task.status === "Completed") return false;

      const deadline = new Date(`${task.deadline}T00:00:00`);

      const daysRemaining = Math.ceil(
        (deadline - todayDate) / (1000 * 60 * 60 * 24)
      );

      return daysRemaining >= 0 && daysRemaining <= 7;
    })
    .sort((a, b) => a.deadline.localeCompare(b.deadline));

  const overdueTasks = tasks
    .filter((task) => {
      if (!task.deadline || task.status === "Completed") return false;

      return new Date(`${task.deadline}T00:00:00`) < todayDate;
    })
    .sort((a, b) => a.deadline.localeCompare(b.deadline));

  // ==========================================
  // TODAY'S STUDY PLAN
  // ==========================================

  const now = new Date();

  const today = [
    now.getFullYear(),
    String(now.getMonth() + 1).padStart(2, "0"),
    String(now.getDate()).padStart(2, "0"),
  ].join("-");

  const todaySessions = sessions.filter(
    (session) =>
      String(session.planned_date).slice(0, 10) === today &&
      String(session.status).trim().toLowerCase() === "planned"
  );

  const totalStudyMinutes = todaySessions.reduce(
    (total, session) =>
      total + Number(session.planned_minutes || 0),
    0
  );

  // ==========================================
  // TOPIC LOOKUP
  // ==========================================

  const getTopicName = (topicId) => {
    const topic = topics.find((item) => item.id === topicId);
    return topic ? topic.name : "Unknown topic";
  };

  const getTaskSubject = (subjectId) => {
    const subject = subjects.find((item) => item.id === subjectId);
    return subject ? subject.name : "General task";
  };

  // ==========================================
  // LOADING STATE
  // ==========================================

  if (loading) {
    return (
      <div className="dashboard">
        <section className="panel">
          <h2>Loading your dashboard...</h2>
          <p>Please wait while we retrieve your study data.</p>
        </section>
      </div>
    );
  }

  // ==========================================
  // ERROR STATE
  // ==========================================

  if (error) {
    return (
      <div className="dashboard">
        <section className="panel">
          <h2>Unable to load dashboard</h2>
          <p>{error}</p>
          <button onClick={loadDashboard}>Try Again</button>
        </section>
      </div>
    );
  }

  // ==========================================
  // DASHBOARD
  // ==========================================

  return (
    <div className="dashboard">

      {/* WELCOME BANNER */}

      <div className="welcome-banner">
        <div>
          <h2>
            Welcome back, {student?.name || "Student"} ♡
          </h2>
          <p>Stay consistent. Every study session counts.</p>
        </div>

        <div className="date-card">
          <h3>
            {new Date().toLocaleDateString("en-IN", {
              weekday: "long",
              day: "numeric",
              month: "long",
              year: "numeric",
            })}
          </h3>
          <p>Your study dashboard</p>
        </div>

        <div className="goal-card">
          <h3>Overall Study Progress</h3>
          <p>
            {completedTopics} of {totalTopics} topics completed
          </p>

          <div className="progress-track">
            <div style={{ width: `${overallProgress}%` }} />
          </div>

          <span>{overallProgress}%</span>
        </div>
      </div>

      {/* STATISTICS */}

      <div className="grid stats-grid">
        <StatCard
          label="Subjects"
          value={totalSubjects}
          helper="Active subjects"
        />

        <StatCard
          label="Topics"
          value={totalTopics}
          helper="Total topics"
        />

        <StatCard
          label="Completed Sessions"
          value={completedSessions}
          helper="Study history"
        />

        <StatCard
          label="Overall Progress"
          value={`${overallProgress}%`}
          helper="Topic completion"
        />

        <StatCard
          label="Total Tasks"
          value={totalTasks}
          helper="All your tasks"
        />

        <StatCard
          label="Pending Tasks"
          value={pendingTasks}
          helper="Tasks remaining"
        />

        <StatCard
          label="Completed Tasks"
          value={completedTasks}
          helper="Tasks finished"
        />

        <StatCard
          label="Overdue Tasks"
          value={overdueTasks.length}
          helper="Past deadline"
        />
      </div>

      {/* MAIN DASHBOARD GRID */}

      <div className="dashboard-grid">

        {/* TODAY'S STUDY PLAN */}

        <section className="panel study-plan">
          <h3>▤ Today's Study Plan</h3>

          <p className="muted">
            Remaining: {(totalStudyMinutes / 60).toFixed(1)} hours
          </p>

          {todaySessions.length === 0 ? (
            <p>No pending study sessions scheduled for today.</p>
          ) : (
            todaySessions.map((session) => (
              <div className="schedule-row" key={session.id}>
                <span>{session.planned_minutes} min</span>
                <span>{getTopicName(session.topic_id)}</span>
                <span>Planned</span>
              </div>
            ))
          )}
        </section>

        {/* STUDY PROGRESS */}

        <section className="panel study-progress">
          <h3>Study Progress</h3>

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

          <div className="progress-legend">
            <p>🟢 Completed: {completedTopics}</p>
            <p>🟣 In Progress: {inProgressTopics}</p>
            <p>⚪ Not Started: {notStartedTopics}</p>
          </div>
        </section>

        {/* SUBJECT PROGRESS */}

        <section className="panel subject-progress">
          <h3>Subject Progress</h3>

          {subjects.length === 0 ? (
            <p>No subjects added yet.</p>
          ) : (
            subjects.map((subject) => {
              const subjectTopics = topics.filter(
                (topic) => topic.subject_id === subject.id
              );

              const progress =
                subjectTopics.length > 0
                  ? Math.round(
                      subjectTopics.reduce(
                        (total, topic) =>
                          total +
                          Number(topic.completion_percent || 0),
                        0
                      ) / subjectTopics.length
                    )
                  : 0;

              return (
                <div className="subject-row" key={subject.id}>
                  <span>{subject.name}</span>

                  <div className="progress-track">
                    <div style={{ width: `${progress}%` }} />
                  </div>

                  <strong>{progress}%</strong>
                </div>
              );
            })
          )}
        </section>

        {/* NEXT PRIORITIES */}

        <section className="panel priorities">
          <h3>Next Priorities</h3>

          {recommendation ? (
            <>
              <p>{recommendation.recommendation}</p>
              <ul>
                {(recommendation.reasons || []).map(
                  (reason, index) => (
                    <li key={index}>{reason}</li>
                  )
                )}
              </ul>
            </>
          ) : (
            <p>No recommendations available.</p>
          )}
        </section>

        {/* TASK OVERVIEW */}

        <section className="panel">
          <h3>My Task Overview</h3>

          <div className="task-dashboard-stats">
            <p>Total: <strong>{totalTasks}</strong></p>
            <p>Pending: <strong>{pendingTasks}</strong></p>
            <p>Completed: <strong>{completedTasks}</strong></p>
          </div>

          <h4>Upcoming Deadlines</h4>

          {upcomingTasks.length === 0 ? (
            <p>No upcoming deadlines in the next 7 days.</p>
          ) : (
            upcomingTasks.slice(0, 5).map((task) => (
              <div className="schedule-row" key={task.id}>
                <span>{task.title}</span>
                <span>{task.deadline}</span>
                <span>{task.priority}</span>
              </div>
            ))
          )}

          <h4 style={{ color: "#C0395B", marginTop: "20px" }}>
            Overdue Tasks
          </h4>

          {overdueTasks.length === 0 ? (
            <p>No overdue tasks. Great work!</p>
          ) : (
            overdueTasks.slice(0, 5).map((task) => (
              <div className="schedule-row" key={task.id}>
                <span>{task.title}</span>
                <span>{task.deadline}</span>
                <span style={{ color: "#C0395B" }}>Overdue</span>
              </div>
            ))
          )}
        </section>

        {/* QUICK ACTIONS */}

        <section className="panel quick-actions">
          <h3>Quick Actions</h3>

          <button onClick={loadDashboard}>
            Refresh Dashboard
          </button>

          <button onClick={() => window.location.reload()}>
            Reload Application
          </button>
        </section>

      </div>
    </div>
  );
}