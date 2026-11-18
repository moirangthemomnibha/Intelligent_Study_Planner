const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000/api/v1";

// ==========================================
// COMMON API REQUEST FUNCTION
// ==========================================

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));

    throw new Error(
      body.detail || `Request failed (${response.status})`
    );
  }

  return response.json();
}

// ==========================================
// API METHODS
// ==========================================

export const api = {

  // HEALTH
  health: () =>
    request("/health/"),

  // STUDENTS
  createStudent: (data) =>
    request("/students/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

      // STUDENT PROFILE
  getStudentProfile: (studentId) =>
    request(`/students/${studentId}/profile`),

  updateStudentProfile: (studentId, data) =>
    request(`/students/${studentId}/profile`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  removeProfilePicture: (studentId) =>
    request(`/students/${studentId}/profile-picture`, {
      method: "DELETE",
    }),

  // SUBJECTS
  createSubject: (data) =>
    request("/subjects/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getSubjects: (studentId) =>
    request(`/subjects/?student_id=${studentId}`),

  getSubject: (subjectId) =>
    request(`/subjects/${subjectId}`),

  deleteSubject: (subjectId) =>
    request(`/subjects/${subjectId}`, {
      method: "DELETE",
    }),

  // TOPICS
  createTopic: (data) =>
    request("/topics/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getTopics: (subjectId) =>
    request(`/topics/?subject_id=${subjectId}`),

  getTopic: (topicId) =>
    request(`/topics/${topicId}`),

  updateTopic: (topicId, data) =>
    request(`/topics/${topicId}`, {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  deleteTopic: (topicId) =>
    request(`/topics/${topicId}`, {
      method: "DELETE",
    }),

  // STUDY SESSIONS
  getSessions: (studentId) =>
    request(`/sessions/?student_id=${studentId}`),

  getSession: (sessionId) =>
    request(`/sessions/${sessionId}`),

  updateSessionStatus: (sessionId, status) =>
    request(
      `/sessions/${sessionId}/status?status=${encodeURIComponent(status)}`,
      { method: "PATCH" }
    ),

  updateSessionProgress: (sessionId, actualMinutes) =>
    request(
      `/sessions/${sessionId}/progress?actual_minutes=${actualMinutes}`,
      { method: "PATCH" }
    ),

  updateSessionReflection: (sessionId, reflection) =>
    request(
      `/sessions/${sessionId}/reflection?reflection=${encodeURIComponent(reflection)}`,
      { method: "PATCH" }
    ),

  // STUDY PLANNING
  generatePlan: (data) =>
    request("/planning/generate", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  // AI RECOMMENDATIONS
  getRecommendation: (studentId, question = null) =>
    request("/ai/recommend", {
      method: "POST",
      body: JSON.stringify({
        student_id: studentId,
        question,
      }),
    }),

};