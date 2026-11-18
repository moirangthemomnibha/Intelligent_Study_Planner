import { useEffect, useState } from "react";
import { api } from "../api/client";

const STUDENT_ID = 3;

export function SubjectsPage() {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [form, setForm] = useState({
    name: "",
    exam_date: "",
    exam_weight: 1,
  });

  const [adding, setAdding] = useState(false);

  // LOAD SUBJECTS
  async function loadSubjects() {
    try {
      setLoading(true);
      setError("");

      const data = await api.getSubjects(STUDENT_ID);
      setSubjects(data);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadSubjects();
  }, []);

  // HANDLE FORM INPUT
  function handleChange(e) {
    const { name, value } = e.target;

    setForm(previous => ({
      ...previous,
      [name]:
        name === "exam_weight"
          ? Number(value)
          : value,
    }));
  }

  // ADD SUBJECT
  async function handleSubmit(e) {
    e.preventDefault();

    try {
      setAdding(true);
      setError("");
      setSuccess("");

      await api.createSubject({
        student_id: STUDENT_ID,
        name: form.name.trim(),
        exam_date: form.exam_date,
        exam_weight: form.exam_weight,
      });

      setForm({
        name: "",
        exam_date: "",
        exam_weight: 1,
      });

      setSuccess("Subject added successfully!");

      await loadSubjects();

    } catch (err) {
      setError(err.message);
    } finally {
      setAdding(false);
    }
  }

  // DELETE SUBJECT
  async function handleDelete(subjectId) {
    const confirmed = window.confirm(
      "Are you sure you want to delete this subject?"
    );

    if (!confirmed) return;

    try {
      setError("");
      setSuccess("");

      await api.deleteSubject(subjectId);

      setSuccess("Subject deleted successfully!");

      await loadSubjects();

    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="dashboard">

      <div className="welcome-banner">
        <div>
          <h2>My Subjects ♡</h2>
          <p>Organize your subjects and examination schedules.</p>
        </div>

        <div className="date-card">
          <h3>{subjects.length}</h3>
          <p>Total Subjects</p>
        </div>
      </div>

      {/* ADD SUBJECT FORM */}

      <section className="panel" style={{ marginBottom: 24 }}>

        <h3>＋ Add New Subject</h3>

        <form onSubmit={handleSubmit}>

          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))",
            gap: 18,
            marginTop: 20
          }}>

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
              <label>Examination Date *</label>

              <input
                type="date"
                name="exam_date"
                value={form.exam_date}
                onChange={handleChange}
                required
                style={inputStyle}
              />
            </div>

            <div>
              <label>Exam Weight *</label>

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
            disabled={adding}
            style={buttonStyle}
          >
            {adding ? "Adding..." : "+ Add Subject"}
          </button>

        </form>

      </section>

      {/* MESSAGES */}

      {error && (
        <div style={messageStyle}>
          {error}
        </div>
      )}

      {success && (
        <div style={{
          ...messageStyle,
          background: "#E6F7EC",
          color: "#287A46"
        }}>
          {success}
        </div>
      )}

      {/* SUBJECT LIST */}

      <section className="panel">

        <h3>▤ Your Subjects</h3>

        {loading ? (

          <p>Loading subjects...</p>

        ) : subjects.length === 0 ? (

          <div style={{ textAlign: "center", padding: 35 }}>
            <h3>No subjects added yet ♡</h3>
            <p>Use the form above to add your first subject.</p>
          </div>

        ) : (

          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(230px, 1fr))",
            gap: 18,
            marginTop: 20
          }}>

            {subjects.map(subject => (

              <div
                key={subject.id}
                style={{
                  background: "#FFF5F7",
                  border: "1px solid #F8DCE5",
                  borderRadius: 14,
                  padding: 20
                }}
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
                  onClick={() => handleDelete(subject.id)}
                  style={{
                    ...buttonStyle,
                    background: "#C87994",
                    marginTop: 10
                  }}
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

// INPUT STYLING

const inputStyle = {
  display: "block",
  width: "100%",
  padding: 12,
  marginTop: 8,
  borderRadius: 9,
  border: "1px solid #E8C5D1",
  background: "#FFFFFF",
  color: "#593B49",
  boxSizing: "border-box",
  fontSize: 14
};

// BUTTON STYLING

const buttonStyle = {
  background: "#D98FA5",
  color: "#FFFFFF",
  border: "none",
  borderRadius: 9,
  padding: "12px 20px",
  marginTop: 20,
  cursor: "pointer",
  fontWeight: 600
};

// MESSAGE STYLING

const messageStyle = {
  background: "#FCE4EC",
  color: "#A33D60",
  padding: 14,
  borderRadius: 9,
  marginBottom: 18
};