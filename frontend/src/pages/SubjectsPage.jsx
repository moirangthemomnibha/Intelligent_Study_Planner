import { useEffect, useState } from "react";
import { api } from "../api/client";

export function SubjectsPage() {
  const [student, setStudent] = useState(null);
  const [subjects, setSubjects] = useState([]);

  const today = new Date();
  const minDate = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [form, setForm] = useState({
    name: "",
    exam_date: "",
    exam_weight: 1,
  });

  const [adding, setAdding] = useState(false);

  // ==========================================
  // LOAD AUTHENTICATED STUDENT AND SUBJECTS
  // ==========================================

  async function loadSubjects(studentId) {
    try {
      const data = await api.getSubjects(studentId);
      setSubjects(data);
    } catch (err) {
      setError(err.message || "Unable to load subjects.");
      throw err;
    }
  }

  async function initializePage() {
    try {
      setLoading(true);
      setError("");

      const profile = await api.getStudentProfile();

      if (!profile || !profile.id) {
        throw new Error(
          "Student profile not found. Please complete your profile."
        );
      }

      setStudent(profile);

      await loadSubjects(profile.id);

    } catch (err) {
      setError(err.message || "Unable to initialize subjects.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    initializePage();
  }, []);

  // ==========================================
  // HANDLE FORM INPUT
  // ==========================================

  function handleChange(e) {
    const { name, value } = e.target;

    setForm(previous => ({
      ...previous,
      [name]: name === "exam_weight"
        ? Number(value)
        : value,
    }));
  }

  // ==========================================
  // ADD SUBJECT
  // ==========================================

  async function handleSubmit(e) {
    e.preventDefault();

    if (!student?.id) {
      setError("Student profile not found.");
      return;
    }

    try {
      setAdding(true);
      setError("");
      setSuccess("");

      await api.createSubject({
        student_id: student.id,
        name: form.name.trim(),
        exam_date: form.exam_date,
        exam_weight: form.exam_weight,
      });

      setForm({
        name: "",
        exam_date: "",
        exam_weight: 1,
      });

      await loadSubjects(student.id);

      setSuccess("Subject added successfully!");

    } catch (err) {
      setError(err.message || "Unable to add subject.");
    } finally {
      setAdding(false);
    }
  }

  // ==========================================
  // DELETE SUBJECT
  // ==========================================

  async function handleDelete(subjectId) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this subject and its associated data?"
    );

    if (!confirmed) return;

    try {
      setError("");
      setSuccess("");

      await api.deleteSubject(subjectId);

      await loadSubjects(student.id);

      setSuccess("Subject deleted successfully!");

    } catch (err) {
      setError(err.message || "Unable to delete subject.");
    }
  }

  // ==========================================
  // LOADING STATE
  // ==========================================

  if (loading) {
    return (
      <div className="dashboard">
        <section className="panel">
          <h2>Loading your subjects...</h2>
          <p>Please wait while we retrieve your information.</p>
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
          <h2>My Subjects ♡</h2>

          <p>
            Organize your subjects and examination schedules.
          </p>
        </div>

        <div className="date-card">
          <h3>{subjects.length}</h3>
          <p>Total Subjects</p>
        </div>

      </div>

      {/* ERROR MESSAGE */}

      {error && (
        <div style={messageStyle}>
          {error}
        </div>
      )}

      {/* SUCCESS MESSAGE */}

      {success && (
        <div
          style={{
            ...messageStyle,
            background: "#E6F7EC",
            color: "#287A46",
          }}
        >
          {success}
        </div>
      )}

      {/* ADD SUBJECT FORM */}

      <section
        className="panel"
        style={{ marginBottom: 24 }}
      >

        <h3>＋ Add New Subject</h3>

        <form onSubmit={handleSubmit}>

          <div style={formGridStyle}>

            <div>
              <label>Subject Name *</label>

              <input
                type="text"
                name="name"
                placeholder="e.g. Computer Networks"
                value={form.name}
                onChange={handleChange}
                minLength={1}
                maxLength={100}
                required
                style={inputStyle}
              />
            </div>

            <div>
              <label>Exam / Target Date *</label>

              <input
                type="date"
                name="exam_date"
                value={form.exam_date}
                min={minDate}
                onChange={handleChange}
                required
                style={inputStyle}
              />
            </div>

            <div>
              <label>Subject Weightage *</label>

              <input
                type="number"
                name="exam_weight"
                min="0.1"
                step="0.1"
                value={form.exam_weight}
                onChange={handleChange}
                required
                style={inputStyle}
              />
            </div>

          </div>

          <button
            type="submit"
            disabled={adding || !student}
            style={{
              ...buttonStyle,
              opacity: adding ? 0.7 : 1,
              cursor: adding ? "not-allowed" : "pointer",
            }}
          >
            {adding ? "Adding Subject..." : "+ Add Subject"}
          </button>

        </form>

      </section>

      {/* SUBJECT LIST */}

      <section className="panel">

        <h3>▤ Your Subjects</h3>

        {subjects.length === 0 ? (

          <div style={emptyStyle}>
            <h3>No subjects added yet ♡</h3>

            <p>
              Start organizing your academic journey
              by adding your first subject.
            </p>
          </div>

        ) : (

          <div style={subjectGridStyle}>

            {subjects.map(subject => (

              <div
                key={subject.id}
                className="subjecy-card"
                style={subjectCardStyle}
              >

                <h3>{subject.name}</h3>

                <p>
                  📅 Exam: {subject.exam_date}
                </p>

                <p>
                  ⭐ Exam Weight: {subject.exam_weight}
                </p>

                <p>
                  Subject ID: {subject.id}
                </p>

                <button
                  type="button"
                  onClick={() => handleDelete(subject.id)}
                  style={deleteButtonStyle}
                >
                  Delete Subject
                </button>

              </div>

            ))}

          </div>

        )}

      </section>

    </div>
  );
}

// ==========================================
// STYLES
// ==========================================

const formGridStyle = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
  gap: 18,
  marginTop: 20,
};

const inputStyle = {
  display: "block",
  width: "100%",
  padding: 12,
  marginTop: 8,
  borderRadius: 9,
  border: "1px solid var(--app-border)",
  background: "var(--app-input)",
  color: "var(--app-text)",
  boxSizing: "border-box",
  fontSize: 14,
};

const buttonStyle = {
  background: "#D98FA5",
  color: "#FFFFFF",
  border: "none",
  borderRadius: 9,
  padding: "12px 20px",
  marginTop: 20,
  fontWeight: 600,
};

const deleteButtonStyle = {
  ...buttonStyle,
  background: "#C87994",
  marginTop: 10,
  cursor: "pointer",
};

const messageStyle = {
  background: "#FCE4EC",
  color: "#A33D60",
  padding: 14,
  borderRadius: 9,
  marginBottom: 18,
};

const emptyStyle = {
  textAlign: "center",
  padding: 35,
};

const subjectGridStyle = {
  display: "grid",
  gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))",
  gap: 18,
  marginTop: 20,
};

const subjectCardStyle = {
  background: "var(--app-card-secondary)",
  color: "var(--app-text)",
  border: "1px solid var(--app-border)",
  borderRadius: 14,
  padding: 20,
};