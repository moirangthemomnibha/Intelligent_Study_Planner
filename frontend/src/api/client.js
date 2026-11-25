const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://localhost:8000/api/v1";

async function request(path, options = {}) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
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

export const api = {
  health: () =>
    request("/health/"),

  register: (data) =>
    request("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  verifyEmail: (data) =>
    request("/auth/verify-email", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  resendOTP: (data) =>
    request("/auth/resend-otp", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  login: (data) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  googleLogin: (credential) =>
    request("/auth/google", {
      method: "POST",
      body: JSON.stringify({ credential }),
    }),

  forgotPassword: (data) =>
    request("/auth/forgot-password", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  resetPassword: (data) =>
    request("/auth/reset-password", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  saveToken: (token) =>
    localStorage.setItem("access_token", token),

  getToken: () =>
    localStorage.getItem("access_token"),

  clearToken: () =>
    localStorage.removeItem("access_token"),

  createStudent: (data) =>
    request("/students/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getStudentProfile: () =>
    request("/students/profile"),

  updateStudentProfile: (data) =>
    request("/students/profile", {
      method: "PUT",
      body: JSON.stringify(data),
    }),

  removeProfilePicture: () =>
    request("/students/profile-picture", {
      method: "DELETE",
    }),

  createSubject: (data) =>
    request("/subjects/", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getSubjects: (studentId) =>
    studentId
      ? request(`/subjects/?student_id=${studentId}`)
      : request("/subjects/"),

  getSubject: (subjectId) =>
    request(`/subjects/${subjectId}`),

  deleteSubject: (subjectId) =>
    request(`/subjects/${subjectId}`, {
      method: "DELETE",
    }),

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

  getSessions: (studentId) =>
    studentId
      ? request(`/sessions/?student_id=${studentId}`)
      : request("/sessions/"),

  getSession: (sessionId) =>
    request(`/sessions/${sessionId}`),

  getWeeklyReport: (studentId) =>
    request(`/sessions/weekly-report?student_id=${studentId}`),

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

  generatePlan: (data) =>
    request("/planning/generate", {
      method: "POST",
      body: JSON.stringify(data),
    }),

  getRecommendation: (studentId, question = null) =>
    request("/ai/recommend", {
      method: "POST",
      body: JSON.stringify({
        ...(studentId ? { student_id: studentId } : {}),
        question,
      }),
    }),

    // ==========================================
// TASKS
// ==========================================

getTasks: (studentId) =>
  request(`/tasks/?student_id=${studentId}`),

getTask: (taskId, studentId) =>
  request(`/tasks/${taskId}?student_id=${studentId}`),

createTask: (taskData) =>
  request("/tasks/", {
    method: "POST",
    body: JSON.stringify(taskData),
  }),

updateTask: (taskId, studentId, taskData) =>
  request(`/tasks/${taskId}?student_id=${studentId}`, {
    method: "PUT",
    body: JSON.stringify(taskData),
  }),

deleteTask: (taskId, studentId) =>
  request(`/tasks/${taskId}?student_id=${studentId}`, {
    method: "DELETE",
  }),

getPreferredTimes: (studentId) =>
  request(`/planning/preferred-times/?student_id=${studentId}`),

createPreferredTime: (studentId, data) =>
  request(`/planning/preferred-times/?student_id=${studentId}`, {
    method: "POST",
    body: JSON.stringify(data),
  }),

deletePreferredTime: (studentId, timeId) =>
  request(
    `/planning/preferred-times/${timeId}?student_id=${studentId}`,
    { method: "DELETE" }
  ),
};
