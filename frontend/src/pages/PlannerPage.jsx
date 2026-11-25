import { useEffect, useState, useRef } from "react";
import { usePlanner } from "../context/PlannerContext";
import { api } from "../api/client";

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

  const [student, setStudent] = useState(null);

  const [preferredTimes, setPreferredTimes] = useState([]);
  const [selectedTimeSlots, setSelectedTimeSlots] = useState({});
  const [savingPreferredTimes, setSavingPreferredTimes] = useState(false);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  const [selectedSubject, setSelectedSubject] = useState("");
  const [topicName, setTopicName] = useState("");
  const [difficulty, setDifficulty] = useState(3);
  const [estimatedMinutes, setEstimatedMinutes] = useState(60);

  const [availableMinutes, setAvailableMinutes] = useState(180);
  const [horizonDays, setHorizonDays] = useState(7);

  const [studyPreferences, setStudyPreferences] = useState({
    daily_study_target_hours: 3,
    preferred_study_start: "",
    preferred_study_end: "",
  });
  const [generating, setGenerating] = useState(false);

  // POMODORO TIMER

  const [timerMode, setTimerMode] = useState("focus");

  const [focusMinutes, setFocusMinutes] = useState(25);
  const [shortBreakMinutes, setShortBreakMinutes] = useState(5);
  const [longBreakMinutes, setLongBreakMinutes] = useState(15);

  const [sessionsBeforeLongBreak, setSessionsBeforeLongBreak] = useState(4);

  const [timeLeft, setTimeLeft] = useState(25 * 60);

  const [timerRunning, setTimerRunning] = useState(false);

  const [activeSessionId, setActiveSessionId] = useState("");

  const [completedFocusMinutes, setCompletedFocusMinutes] = useState(0);

  const [completedFocusSessions, setCompletedFocusSessions] = useState(0);

  const [pomodoroSettingsLoading, setPomodoroSettingsLoading] = useState(true);

  // LOAD SAVED POMODORO SETTINGS

  useEffect(() => {
    async function loadPomodoroSettings() {
      try {
        const token =
          localStorage.getItem("access_token") ||
          localStorage.getItem("token");

        const response = await fetch(
          "http://127.0.0.1:8000/api/v1/settings/",
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error("Could not load Pomodoro settings.");
        }

        const data = await response.json();

        const focus = Number(data.pomodoro_work_min) || 25;
        const shortBreak =
          Number(data.pomodoro_short_break_min) || 5;
        const longBreak =
          Number(data.pomodoro_long_break_min) || 15;
        const sessions =
          Number(data.sessions_before_long_break) || 4;

        setFocusMinutes(focus);
        setShortBreakMinutes(shortBreak);
        setLongBreakMinutes(longBreak);
        setSessionsBeforeLongBreak(sessions);

        setTimeLeft(focus * 60);

      } catch (error) {
        console.error("Pomodoro settings error:", error);
      } finally {
        setPomodoroSettingsLoading(false);
      }
    }

    loadPomodoroSettings();
  }, []);
  const TIMER_DURATIONS = {
    focus: focusMinutes * 60,
    shortBreak: shortBreakMinutes * 60,
    longBreak: longBreakMinutes * 60,
  };

  const timerModes = ["focus", "shortBreak", "longBreak"];
  const notificationPlayed = useRef(false);

    function getNextTimerMode(currentMode) {

      // After a focus session, determine the correct break.

      if (currentMode === "focus") {

        const nextCompletedSession =
          completedFocusSessions + 1;

        if (
          nextCompletedSession % sessionsBeforeLongBreak === 0
        ) {
          return "longBreak";
        }

        return "shortBreak";
      }

      // After either break, return to focus.

      return "focus";
    }

  // ==========================================
  // POMODORO NOTIFICATIONS
  // ==========================================

  async function sendTimerNotification(title, body) {
    // Sound notification
    try {
      const audioContext = new (
        window.AudioContext || window.webkitAudioContext
      )();

      const oscillator = audioContext.createOscillator();
      const gain = audioContext.createGain();

      oscillator.connect(gain);
      gain.connect(audioContext.destination);

      oscillator.frequency.value = 880;
      gain.gain.value = 0.15;

      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.4);

    } catch (err) {
      console.error("Sound notification failed:", err);
    }

    // Browser notification
    if (!("Notification" in window)) return;

    if (Notification.permission === "granted") {
      new Notification(title, {
        body,
        icon: "/favicon.ico",
      });
    }
  }

  const daysOfWeek = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
  ];

  const studyHours = Array.from(
    { length: 16 },
    (_, index) => index + 6
  );

  // ==========================================
  // LOAD DATA FOR LOGGED-IN STUDENT
  // ==========================================

  async function loadData() {
    try {
      setError("");
      setLoading(true);

      console.log("Planner: Loading profile...");

      const profile = await api.getStudentProfile();

      if (!profile?.id) {
        throw new Error(
          "Student profile not found. Please log in again."
        );
      }

      setStudent(profile);

      const studentId = profile.id;

      // LOAD STUDY PREFERENCES FROM SETTINGS

try {
  const token =
    localStorage.getItem("access_token") ||
    localStorage.getItem("token");

  const response = await fetch(
    "http://127.0.0.1:8000/api/v1/settings/",
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (response.ok) {
    const preferences = await response.json();

    setStudyPreferences(preferences);

    const targetHours = Number(
      preferences.daily_study_target_hours
    );

    if (Number.isFinite(targetHours) && targetHours > 0) {
      setAvailableMinutes(Math.round(targetHours * 60));
    }
  }
} catch (preferenceError) {
  console.error(
    "Could not load study preferences:",
    preferenceError
  );
}

      // LOAD PREFERRED TIMES

      console.log("Planner: Loading preferred times...");

      const savedTimes = await api.getPreferredTimes(studentId);

      setPreferredTimes(savedTimes);

      const selectedSlots = {};

      savedTimes.forEach((item) => {
        const startHour = Number(item.start_time.split(":")[0]);
        const endHour = Number(item.end_time.split(":")[0]);

        for (let hour = startHour; hour < endHour; hour++) {
          selectedSlots[`${item.day_of_week}-${hour}`] = true;
        }
      });

      setSelectedTimeSlots(selectedSlots);

      // LOAD SUBJECTS

      console.log("Planner: Loading subjects...");

      const subjectData = await api.getSubjects(studentId);

      setSubjects(subjectData);

      // LOAD TOPICS

      console.log("Planner: Loading topics...");

      const topicResults = await Promise.all(
        subjectData.map((subject) =>
          api.getTopics(subject.id)
        )
      );

      setTopics(topicResults.flat());

      // LOAD STUDY SESSIONS

      console.log("Planner: Loading sessions...");

      const sessionData = await api.getSessions(studentId);

      setPlan(sessionData);

      console.log("Planner: All data loaded successfully.");

    } catch (err) {
      console.error("Planner loading error:", err);

      setError(
        err.message || "Unable to load planner data."
      );

    } finally {
      setLoading(false);
    }
  }

  // IMPORTANT: LOAD DATA WHEN PLANNER OPENS

  useEffect(() => {
    loadData();
  }, []);

  // ==========================================
  // PREFERRED STUDY TIME
  // ==========================================

  function togglePreferredSlot(day, hour) {
    const key = `${day}-${hour}`;

    setSelectedTimeSlots((previous) => ({
      ...previous,
      [key]: !previous[key],
    }));
  }

  async function savePreferredTimes() {
    if (!student?.id) {
      setError("Student profile not found.");
      return;
    }

    setSavingPreferredTimes(true);
    setError("");
    setMessage("");

    try {
      // DELETE OLD PREFERRED TIMES

      for (const item of preferredTimes) {
        await api.deletePreferredTime(student.id, item.id);
      }

      // SAVE NEW TIME SLOTS

      for (let day = 0; day < 7; day++) {
        const hours = studyHours.filter(
          (hour) => selectedTimeSlots[`${day}-${hour}`]
        );

        if (hours.length === 0) continue;

        let start = hours[0];
        let previous = hours[0];

        for (let i = 1; i <= hours.length; i++) {
          const current = hours[i];

          if (current !== previous + 1) {
            await api.createPreferredTime(student.id, {
              day_of_week: day,
              start_time: `${String(start).padStart(2, "0")}:00`,
              end_time: `${String(previous + 1).padStart(2, "0")}:00`,
            });

            start = current;
          }

          previous = current;
        }
      }

      const updated = await api.getPreferredTimes(student.id);

      setPreferredTimes(updated);

      setMessage(
        "Preferred study times saved successfully!"
      );

    } catch (err) {
      console.error(err);

      setError(
        err.message || "Could not save preferred study times."
      );

    } finally {
      setSavingPreferredTimes(false);
    }
  }

  // ==========================================
  // ADD TOPIC
  // ==========================================

  async function handleAddTopic(e) {
    e.preventDefault();

    if (!student?.id) {
      setError("Student profile not found. Please log in again.");
      return;
    }

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

      setError(
        err.message || "Could not add topic."
      );
    }
  }

  // ==========================================
  // UPDATE TOPIC COMPLETION
  // ==========================================

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

      setError(
        err.message || "Could not update topic."
      );
    }
  }

  // ==========================================
  // GENERATE STUDY PLAN
  // ==========================================

  async function handleGeneratePlan() {
    if (generating) return;

    if (!student?.id) {
      setError("Student profile not found. Please log in again.");
      return;
    }

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
        student_id: student.id,
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

      setError(
        err.message || "Could not generate your study plan."
      );

    } finally {
      setGenerating(false);
    }
  }

  // ==========================================
  // UPDATE STUDY SESSION
  // ==========================================

  async function updateSession(sessionId, status) {
    try {
      setError("");
      setMessage("");

      await api.updateSessionStatus(sessionId, status);

      await loadData();

    } catch (err) {
      console.error(err);

      setError(
        err.message || "Could not update study session."
      );
    }
  }

  // ==========================================
  // POMODORO TIMER
  // ==========================================

  useEffect(() => {
    if (!timerRunning) return;

    const interval = setInterval(() => {
      setTimeLeft((previous) =>
        Math.max(0, previous - 1)
      );
    }, 1000);

    return () => clearInterval(interval);
  }, [timerRunning]);

  // SYNCHRONIZE TIMER WITH UPDATED DURATIONS

useEffect(() => {
  if (timerRunning) return;

  const durations = {
    focus: focusMinutes,
    shortBreak: shortBreakMinutes,
    longBreak: longBreakMinutes,
  };

  setTimeLeft(durations[timerMode] * 60);

  notificationPlayed.current = false;

}, [
  focusMinutes,
  shortBreakMinutes,
  longBreakMinutes,
  timerMode,
  timerRunning,
]);

  // 20-SECOND WARNING

  useEffect(() => {
    if (!timerRunning || timeLeft !== 20) return;

    if (notificationPlayed.current) return;

    notificationPlayed.current = true;

    if (timerMode === "focus") {
      sendTimerNotification(
        "Focus session ending soon!",
        "Your break starts in 20 seconds."
      );
    } else {
      sendTimerNotification(
        "Break ending soon!",
        "Your next study session starts in 20 seconds."
      );
    }
  }, [timeLeft, timerRunning, timerMode]);

async function recordCompletedFocusSession() {
  if (!activeSessionId) return;

  try {
    const selectedSession = plan.find(
      (item) => String(item.id) === String(activeSessionId)
    );

    if (!selectedSession) return;

    const totalActualMinutes =
      Number(selectedSession.actual_minutes || 0) + focusMinutes;

    await api.updateSessionProgress(
      activeSessionId,
      totalActualMinutes
    );

    await loadData();

    setMessage("Study time recorded successfully!");

  } catch (err) {
    console.error("Study time recording failed:", err);
    setError(err.message || "Could not record study time.");
  }
}

  // HANDLE TIMER COMPLETION

  useEffect(() => {
    if (timeLeft !== 0 || !timerRunning) return;

    if (timerMode === "focus") {
      setCompletedFocusMinutes(
        (previous) => previous + focusMinutes
      );

      setCompletedFocusSessions(
        (previous) => previous + focusMinutes
      )
      recordCompletedFocusSession();
    }

    const nextMode = getNextTimerMode(timerMode);

    setTimerMode(nextMode);
    setTimeLeft(TIMER_DURATIONS[nextMode]);

    notificationPlayed.current = false;

    sendTimerNotification(
      nextMode === "focus"
        ? "Focus Time!"
        : nextMode === "shortBreak"
          ? "Short Break!"
          : "Long Break!",
      nextMode === "focus"
        ? "Your break is over. Time to study!"
        : "Your focus session is complete. Relax and recharge!"
    );

  }, [timeLeft, timerRunning, timerMode,
    focusMinutes, shortBreakMinutes, longBreakMinutes,
    sessionsBeforeLongBreak, completedFocusSessions,
    activeSessionId, plan,
  ]);

  // SAVE POMODORO SETTINGS FROM PLANNER

async function savePomodoroSettings() {
  try {
    setError("");
    setMessage("");

    const token =
      localStorage.getItem("access_token") ||
      localStorage.getItem("token");

    if (!token) {
      throw new Error("Please log in again.");
    }

    // Validate durations
    if (
      !Number.isInteger(Number(focusMinutes)) ||
      focusMinutes < 1 ||
      focusMinutes > 180
    ) {
      throw new Error("Focus duration must be between 1 and 180 minutes.");
    }

    if (
      !Number.isInteger(Number(shortBreakMinutes)) ||
      shortBreakMinutes < 1 ||
      shortBreakMinutes > 60
    ) {
      throw new Error("Short break must be between 1 and 60 minutes.");
    }

    if (
      !Number.isInteger(Number(longBreakMinutes)) ||
      longBreakMinutes < 1 ||
      longBreakMinutes > 60
    ) {
      throw new Error("Long break must be between 1 and 60 minutes.");
    }

    if (
      !Number.isInteger(Number(sessionsBeforeLongBreak)) ||
      sessionsBeforeLongBreak < 1 ||
      sessionsBeforeLongBreak > 20
    ) {
      throw new Error("Sessions before long break must be between 1 and 20.");
    }

    // Fetch existing settings to preserve other preferences
    const getResponse = await fetch(
      "http://127.0.0.1:8000/api/v1/settings/",
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!getResponse.ok) {
      throw new Error("Could not retrieve existing settings.");
    }

    const existingSettings = await getResponse.json();

    // Update only Pomodoro values
    const updatedSettings = {
      ...existingSettings,
      pomodoro_work_min: Number(focusMinutes),
      pomodoro_short_break_min: Number(shortBreakMinutes),
      pomodoro_long_break_min: Number(longBreakMinutes),
      sessions_before_long_break: Number(sessionsBeforeLongBreak),
    };

    const response = await fetch(
      "http://127.0.0.1:8000/api/v1/settings/",
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(updatedSettings),
      }
    );

    if (!response.ok) {
      throw new Error("Failed to save Pomodoro settings.");
    }

    const savedSettings = await response.json();

    setFocusMinutes(Number(savedSettings.pomodoro_work_min));
    setShortBreakMinutes(Number(savedSettings.pomodoro_short_break_min));
    setLongBreakMinutes(Number(savedSettings.pomodoro_long_break_min));
    setSessionsBeforeLongBreak(
      Number(savedSettings.sessions_before_long_break)
    );

    // Update countdown when timer is paused
    if (!timerRunning) {
      const durations = {
        focus: Number(savedSettings.pomodoro_work_min),
        shortBreak: Number(savedSettings.pomodoro_short_break_min),
        longBreak: Number(savedSettings.pomodoro_long_break_min),
      };

      setTimeLeft(durations[timerMode] * 60);
    }

    setMessage("Pomodoro settings saved successfully!");

  } catch (error) {
    console.error("Pomodoro save error:", error);
    setError(error.message || "Could not save Pomodoro settings.");
  }
}

  async function startTimer() {
    if (
      "Notification" in window &&
      Notification.permission === "default"
    ) {
      await Notification.requestPermission();
    }

    setError("");
    notificationPlayed.current = false;
    setTimerRunning(true);
  }

  function pauseTimer() {
    setTimerRunning(false);
  }

  function resetTimer() {
    setTimerRunning(false);
    setTimeLeft(TIMER_DURATIONS[timerMode]);
    notificationPlayed.current = false;
  }

  function changeTimerMode(mode) {
    setTimerRunning(false);
    setTimerMode(mode);
    setTimeLeft(TIMER_DURATIONS[mode]);
    notificationPlayed.current = false;
  }

  function skipTimerMode() {
    const nextMode = getNextTimerMode(timerMode);

    changeTimerMode(nextMode);
  }

  function formatTimer(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;

    return `${String(minutes).padStart(2, "0")}:${String(
      remainingSeconds
    ).padStart(2, "0")}`;
  }

  // ==========================================
  // LOADING SCREEN
  // ==========================================

  if (loading) {
    return (
      <div className="planner-loading">
        <p>Loading your study planner...</p>
      </div>
    );
  }

  // ==========================================
  // MAIN PLANNER PAGE
  // ==========================================

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

      {/* PREFERRED STUDY TIMES */}

      <section className="panel preferred-time-panel">

        <div className="section-heading">
          <h2>My Preferred Study Time</h2>

          <p>
            Select the hours you prefer to study each day.
          </p>
        </div>

        <div className="preferred-time-wrapper">

          <table className="preferred-time-table">

            <thead>
              <tr>
                <th>Day</th>

                {studyHours.map((hour) => (
                  <th key={hour}>
                    {`${String(hour).padStart(2, "0")}:00`}
                  </th>
                ))}

              </tr>
            </thead>

            <tbody>

              {daysOfWeek.map((day, dayIndex) => (

                <tr key={day}>

                  <th>{day}</th>

                  {studyHours.map((hour) => {

                    const selected =
                      selectedTimeSlots[`${dayIndex}-${hour}`];

                    return (
                      <td key={hour}>

                        <button
                          type="button"
                          className={`preferred-time-slot ${
                            selected ? "selected" : ""
                          }`}
                          aria-label={`${day}, ${hour}:00`}
                          aria-pressed={Boolean(selected)}
                          onClick={() =>
                            togglePreferredSlot(dayIndex, hour)
                          }
                        >
                          {selected ? "✓" : ""}
                        </button>

                      </td>
                    );
                  })}

                </tr>
              ))}

            </tbody>
          </table>

        </div>

        <button
          type="button"
          onClick={savePreferredTimes}
          disabled={savingPreferredTimes}
          className="generate-plan-button"
        >
          {savingPreferredTimes
            ? "Saving..."
            : "Save Preferred Times"}
        </button>

      </section>

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

          <form
            className="topic-form"
            onSubmit={handleAddTopic}
          >

            <div className="form-group">

              <label>Select Subject</label>

              <select
                value={selectedSubject}
                onChange={(e) =>
                  setSelectedSubject(e.target.value)
                }
                required
              >
                <option value="">Choose a subject</option>

                {subjects.map((subject) => (
                  <option
                    key={subject.id}
                    value={subject.id}
                  >
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
                onChange={(e) =>
                  setTopicName(e.target.value)
                }
                placeholder="e.g. Introduction to DBMS"
                required
              />

            </div>

            <div className="form-group">

              <label>Difficulty Level</label>

              <select
                value={difficulty}
                onChange={(e) =>
                  setDifficulty(Number(e.target.value))
                }
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
                onChange={(e) =>
                  setEstimatedMinutes(e.target.value)
                }
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
              (topic) =>
                Number(topic.subject_id) === Number(subject.id)
            );

            return (

              <div
                key={subject.id}
                className="subject-topic-group"
              >

                <h3>{subject.name}</h3>

                {subjectTopics.length === 0 ? (

                  <p className="empty-topics">
                    No topics added yet.
                  </p>

                ) : (

                  <div className="topic-list">

                    {subjectTopics.map((topic) => (

                      <label
                        key={topic.id}
                        className="topic-checkbox"
                      >

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

      {/* GENERATE STUDY PLAN */}

      <section className="panel generate-plan-panel">

        <div className="section-heading">

          <h2>Generate Study Plan</h2>

          <p>
            Create a structured study timetable for your selected planning period.
          </p>

          <div className="study-preference-summary">

  <p>
    <strong>Daily Study Target:</strong>{" "}
    {studyPreferences.daily_study_target_hours} hours
  </p>

  <p>
    <strong>Preferred Study Hours:</strong>{" "}
    {studyPreferences.preferred_study_start &&
    studyPreferences.preferred_study_end
      ? `${studyPreferences.preferred_study_start} – ${studyPreferences.preferred_study_end}`
      : "Not configured"}
  </p>

</div>

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
                onChange={(e) =>
                  setAvailableMinutes(e.target.value)
                }
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
                onChange={(e) =>
                  setHorizonDays(e.target.value)
                }
              />

              <span>Days</span>

            </div>

          </div>

          <div className="generate-button-wrapper">

            <button
              type="button"
              className="generate-plan-button"
              onClick={handleGeneratePlan}
              disabled={generating}
            >
              {generating
                ? "Generating Your Study Plan..."
                : "Generate My Study Plan"}
            </button>

          </div>

        </div>

      </section>

      {/* POMODORO TIMER */}

      <section className="panel pomodoro-panel">

        <div className="section-heading">

          <h2>Pomodoro Focus Timer</h2>

          <p>
            Stay focused and make every study session count.
          </p>

        </div>

      <div className="break-settings">

        {/* FOCUS DURATION */}
        <div className="form-group">
          <label>Focus Duration (minutes)</label>
            <input
              type="number"
              min="1"
              max="180"
              value={focusMinutes}
              disabled={timerRunning}
              onChange={(e) => {
                const value = Number(e.target.value);

                if (value >= 1 && value <= 180) {
                  setFocusMinutes(value);

                  if (timerMode === "focus") {
                    setTimeLeft(value * 60);
                  }
                }
              }}
            />
          </div>

          {/* SHORT BREAK */}
          <div className="form-group">
            <label>Short Break (minutes)</label>
            <input
              type="number"
              min="1"
              max="60"
              value={shortBreakMinutes}
              disabled={timerRunning}
              onChange={(e) => {
                const value = Number(e.target.value);

                if (value >= 1 && value <= 60) {
                  setShortBreakMinutes(value);

                  if (timerMode === "shortBreak") {
                    setTimeLeft(value * 60);
                  }
                }
              }}
            />
          </div>

          {/* LONG BREAK */}
          <div className="form-group">
            <label>Long Break (minutes)</label>
            <input
              type="number"
              min="1"
              max="60"
              value={longBreakMinutes}
              disabled={timerRunning}
              onChange={(e) => {
                const value = Number(e.target.value);

                if (value >= 1 && value <= 60) {
                  setLongBreakMinutes(value);

                  if (timerMode === "longBreak") {
                    setTimeLeft(value * 60);
                  }
                }
              }}
            />
          </div>

        </div>

        <div className="pomodoro-save-wrapper">
          <button
            type="button"
            className="generate-plan-button"
            onClick={savePomodoroSettings}
            disabled={timerRunning}
          >
            Save Pomodoro Settings
          </button>
        </div>

        <div className="pomodoro-modes">

          {[
            ["focus", "Focus"],
            ["shortBreak", "Short Break"],
            ["longBreak", "Long Break"],
          ].map(([mode, label]) => (

            <button
              key={mode}
              type="button"
              className={timerMode === mode ? "active" : ""}
              onClick={() => changeTimerMode(mode)}
              disabled={timerRunning}
            >
              {label}
            </button>

          ))}

        </div>

        <div className="pomodoro-circle-wrapper">

          <div
            className="pomodoro-circle"
            style={{
              "--timer-progress": `${
                (timeLeft / TIMER_DURATIONS[timerMode]) * 100
              }%`,
            }}
          >

            <div className="pomodoro-circle-inner">

              <div className="pomodoro-time">
                {formatTimer(timeLeft)}
              </div>

              <div className="pomodoro-mode-label">
                {timerMode === "focus"
                  ? "FOCUS"
                  : timerMode === "shortBreak"
                    ? "SHORT BREAK"
                    : "LONG BREAK"}
              </div>

            </div>

          </div>

        </div>

        <p className="pomodoro-label">
          {timerMode === "focus"
            ? "Stay focused. You've got this!"
            : "Relax and recharge."}
        </p>

        <p className="pomodoro-label">
          Completed focus time: {completedFocusMinutes} minutes
        </p>

        <div className="form-group pomodoro-session-select">

          <label>Select Study Session</label>

          <select
            value={activeSessionId}
            onChange={(e) =>
              setActiveSessionId(e.target.value)
            }
            disabled={timerRunning}
          >

            <option value="">
              Choose a planned session
            </option>

            {plan
              .filter((item) => item.status === "planned")
              .map((item) => {

                const topic = topics.find(
                  (topic) => topic.id === item.topic_id
                );

                return (
                  <option
                    key={item.id}
                    value={item.id}
                  >
                    {topic?.name || "Study Session"}
                    {" — "}
                    {item.planned_date}
                  </option>
                );
              })}

          </select>

        </div>

        <div className="pomodoro-controls">

          <button
            type="button"
            className="pomodoro-reset"
            onClick={resetTimer}
            title="Reset"
          >
            ↺
          </button>

          <button
            type="button"
            className="pomodoro-play"
            onClick={
              timerRunning ? pauseTimer : startTimer
            }
            title={timerRunning ? "Pause" : "Start"}
          >
            {timerRunning ? "Ⅱ" : "▶"}
          </button>

          <button
            type="button"
            className="pomodoro-skip"
            onClick={skipTimerMode}
            title="Next mode"
          >
            ↦
          </button>

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
                (item) =>
                  Number(item.id) === Number(topic?.subject_id)
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