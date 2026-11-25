import { useEffect, useState } from "react";
import { api } from "../api/client";
import "./TasksPage.css";

export default function TasksPage() {
  const [studentId, setStudentId] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [topics, setTopics] = useState([]);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [form, setForm] = useState({
    title: "",
    description: "",
    subject_id: "",
    topic_id: "",
    priority: "Medium",
    status: "Not Started",
    deadline: "",
    estimated_minutes: 60,
  });

  const [editingId, setEditingId] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState("All");
  const [filterPriority, setFilterPriority] = useState("All");

  useEffect(() => {
    initialize();
  }, []);

  async function initialize() {
    try {
      setError("");

      const profile = await api.getStudentProfile();
      const id = profile.id || profile.student_id;

      setStudentId(id);

      const [taskData, subjectData] = await Promise.all([
        api.getTasks(id),
        api.getSubjects(id),
      ]);

      setTasks(taskData);
      setSubjects(subjectData);
    } catch (err) {
      setError(err.message || "Unable to load tasks and subjects.");
    } finally {
      setLoading(false);
    }
  }

  async function loadTasks() {
    if (!studentId) return;

    const data = await api.getTasks(studentId);
    setTasks(data);
  }

  async function handleSubjectChange(e) {
    const subjectId = e.target.value;

    setForm((previous) => ({
      ...previous,
      subject_id: subjectId,
      topic_id: "",
    }));

    setTopics([]);
    setError("");

    if (!subjectId) return;

    try {
      const data = await api.getTopics(Number(subjectId));
      setTopics(data);
    } catch (err) {
      setError(err.message || "Unable to load topics.");
    }
  }

  function handleChange(e) {
    const { name, value } = e.target;

    setForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();

    setSaving(true);
    setError("");

    try {
      const taskData = {
        ...form,
        student_id: studentId,
        subject_id: form.subject_id
          ? Number(form.subject_id)
          : null,
        topic_id: form.topic_id
          ? Number(form.topic_id)
          : null,
        estimated_minutes: Number(form.estimated_minutes),
        deadline: form.deadline || null,
      };

      if (editingId) {
        await api.updateTask(editingId, studentId, taskData);
      } else {
        await api.createTask(taskData);
      }

      resetForm();
      await loadTasks();
    } catch (err) {
      setError(err.message || "Unable to save task.");
    } finally {
      setSaving(false);
    }
  }

  function resetForm() {
    setForm({
      title: "",
      description: "",
      subject_id: "",
      topic_id: "",
      priority: "Medium",
      status: "Not Started",
      deadline: "",
      estimated_minutes: 60,
    });

    setTopics([]);
    setEditingId(null);
  }

  async function handleEdit(task) {
    setEditingId(task.id);

    let topicData = [];

    if (task.subject_id) {
      try {
        topicData = await api.getTopics(task.subject_id);
      } catch {
        topicData = [];
      }
    }

    setTopics(topicData);

    setForm({
      title: task.title,
      description: task.description || "",
      subject_id: task.subject_id || "",
      topic_id: task.topic_id || "",
      priority: task.priority,
      status: task.status,
      deadline: task.deadline || "",
      estimated_minutes: task.estimated_minutes || 60,
    });

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function handleDelete(taskId) {
    if (!window.confirm("Are you sure you want to delete this task?")) {
      return;
    }

    try {
      setError("");
      await api.deleteTask(taskId, studentId);
      await loadTasks();
    } catch (err) {
      setError(err.message || "Unable to delete task.");
    }
  }

  async function handleStatusChange(task, status) {
    try {
      setError("");

      await api.updateTask(task.id, studentId, { status });
      await loadTasks();
    } catch (err) {
      setError(err.message || "Unable to update task.");
    }
  }

  const completed = tasks.filter(
    (task) => task.status === "Completed"
  ).length;

  const pending = tasks.length - completed;

  const filteredTasks = tasks.filter((task) => {
    const matchesSearch = task.title
      .toLowerCase()
      .includes(searchTerm.toLowerCase());

    const matchesStatus =
      filterStatus === "All" || task.status === filterStatus;

    const matchesPriority =
      filterPriority === "All" || task.priority === filterPriority;

    return matchesSearch && matchesStatus && matchesPriority;
  });

  if (loading) {
    return (
      <div className="tasks-page">
        <div className="tasks-loading">Loading tasks...</div>
      </div>
    );
  }

  return (
    <div className="tasks-page">

      {/* PAGE HEADER */}

      <div className="tasks-header">
        <div>
          <h1>My Tasks</h1>
          <p>Organize your academic work and stay on track.</p>
        </div>
      </div>

      {/* ERROR MESSAGE */}

      {error && (
        <div className="tasks-error">
          {error}
        </div>
      )}

      {/* TASK STATISTICS */}

      <div className="tasks-summary">

        <div className="task-stat-card">
          <span className="task-stat-icon">📚</span>
          <p>Total Tasks</p>
          <h2>{tasks.length}</h2>
        </div>

        <div className="task-stat-card">
          <span className="task-stat-icon">⏳</span>
          <p>Pending</p>
          <h2>{pending}</h2>
        </div>

        <div className="task-stat-card">
          <span className="task-stat-icon">✓</span>
          <p>Completed</p>
          <h2>{completed}</h2>
        </div>

      </div>

      {/* CREATE / EDIT TASK */}

      <section className="tasks-section">

        <div className="tasks-section-heading">
          <h2>
            {editingId ? "Edit Task" : "Create New Task"}
          </h2>

          <p>
            Add and manage your academic activities.
          </p>
        </div>

        <form onSubmit={handleSubmit}>

          <div className="tasks-form-grid">

            <div className="tasks-form-group">
              <label>Task Title *</label>

              <input
                type="text"
                name="title"
                placeholder="Enter task title"
                value={form.title}
                onChange={handleChange}
                required
                minLength={2}
              />
            </div>

            <div className="tasks-form-group">
              <label>Subject</label>

              <select
                value={form.subject_id}
                onChange={handleSubjectChange}
              >
                <option value="">Select Subject (Optional)</option>

                {subjects.map((subject) => (
                  <option key={subject.id} value={subject.id}>
                    {subject.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="tasks-form-group">
              <label>Topic</label>

              <select
                name="topic_id"
                value={form.topic_id}
                onChange={handleChange}
                disabled={!form.subject_id}
              >
                <option value="">Select Topic (Optional)</option>

                {topics.map((topic) => (
                  <option key={topic.id} value={topic.id}>
                    {topic.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="tasks-form-group">
              <label>Priority</label>

              <select
                name="priority"
                value={form.priority}
                onChange={handleChange}
              >
                <option value="Low">Low Priority</option>
                <option value="Medium">Medium Priority</option>
                <option value="High">High Priority</option>
              </select>
            </div>

            <div className="tasks-form-group">
              <label>Status</label>

              <select
                name="status"
                value={form.status}
                onChange={handleChange}
              >
                <option value="Not Started">Not Started</option>
                <option value="In Progress">In Progress</option>
                <option value="Completed">Completed</option>
              </select>
            </div>

            <div className="tasks-form-group">
              <label>Deadline</label>

              <input
                type="date"
                name="deadline"
                value={form.deadline}
                onChange={handleChange}
              />
            </div>

            <div className="tasks-form-group">
              <label>Estimated Time (minutes)</label>

              <input
                type="number"
                name="estimated_minutes"
                value={form.estimated_minutes}
                onChange={handleChange}
                min="1"
                required
              />
            </div>

          </div>

          <div className="tasks-form-group tasks-description">
            <label>Description</label>

            <textarea
              name="description"
              placeholder="Write a short description (optional)"
              value={form.description}
              onChange={handleChange}
            />
          </div>

          <div className="tasks-form-actions">

            <button
              type="submit"
              className="tasks-primary-btn"
              disabled={saving}
            >
              {saving
                ? "Saving..."
                : editingId
                  ? "Update Task"
                  : "+ Add Task"}
            </button>

            {editingId && (
              <button
                type="button"
                className="tasks-secondary-btn"
                onClick={resetForm}
              >
                Cancel
              </button>
            )}

          </div>

        </form>

      </section>

      {/* ALL TASKS */}

      <section className="tasks-section">

        <div className="tasks-section-heading">
          <h2>All Tasks</h2>
          <p>View, filter and manage your tasks.</p>
        </div>

        {/* SEARCH AND FILTER */}

        <div className="tasks-filters">

          <input
            type="text"
            placeholder="Search tasks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />

          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
          >
            <option value="All">All Statuses</option>
            <option value="Not Started">Not Started</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
          </select>

          <select
            value={filterPriority}
            onChange={(e) => setFilterPriority(e.target.value)}
          >
            <option value="All">All Priorities</option>
            <option value="Low">Low Priority</option>
            <option value="Medium">Medium Priority</option>
            <option value="High">High Priority</option>
          </select>

        </div>

        {/* TASK LIST */}

        {tasks.length === 0 ? (

          <div className="tasks-empty">
            <span>📝</span>
            <h3>No Tasks Yet</h3>
            <p>Create your first task to get started.</p>
          </div>

        ) : filteredTasks.length === 0 ? (

          <div className="tasks-empty">
            <h3>No Matching Tasks</h3>
            <p>Try changing your search or filters.</p>
          </div>

        ) : (

          <div className="tasks-list">

            {filteredTasks.map((task) => {

              const subjectName =
                subjects.find(
                  (subject) => subject.id === task.subject_id
                )?.name || "Not assigned";

              return (
                <article className="task-item" key={task.id}>

                  <div className="task-item-content">

                    <div className="task-item-heading">
                      <h3>{task.title}</h3>

                      <span
                        className={`task-priority ${task.priority.toLowerCase()}`}
                      >
                        {task.priority}
                      </span>
                    </div>

                    {task.description && (
                      <p className="task-description-text">
                        {task.description}
                      </p>
                    )}

                    <div className="task-metadata">

                      <span>📚 {subjectName}</span>

                      <span>📅 {task.deadline || "No deadline"}</span>

                      <span>
                        ⏱ {task.estimated_minutes || 0} minutes
                      </span>

                    </div>

                    <div className="task-status-control">

                      <label>Status:</label>

                      <select
                        value={task.status}
                        onChange={(e) =>
                          handleStatusChange(task, e.target.value)
                        }
                      >
                        <option value="Not Started">Not Started</option>
                        <option value="In Progress">In Progress</option>
                        <option value="Completed">Completed</option>
                      </select>

                    </div>

                  </div>

                  <div className="task-item-actions">

                    <button
                      type="button"
                      className="tasks-edit-btn"
                      onClick={() => handleEdit(task)}
                    >
                      Edit
                    </button>

                    <button
                      type="button"
                      className="tasks-delete-btn"
                      onClick={() => handleDelete(task.id)}
                    >
                      Delete
                    </button>

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