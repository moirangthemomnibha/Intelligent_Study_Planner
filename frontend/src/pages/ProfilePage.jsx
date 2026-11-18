import React, { useState, useEffect, useRef } from "react";
import "./ProfilePage.css";

function ProfilePage() {
  const [isEditing, setIsEditing] = useState(false);

  // Profile picture
  const [profileImage, setProfileImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  // Camera
  const [showCamera, setShowCamera] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);

  const videoRef = useRef(null);
  const fileInputRef = useRef(null);

  // Profile information
  const [profile, setProfile] = useState({
    fullName: "",
    email: "",
    phone: "",
    dob: "",
    gender: "",
    address: "",

    category: "",

    // School
    schoolName: "",
    schoolBoard: "",
    classLevel: "",

    // Undergraduate / Postgraduate
    college: "",
    department: "",
    course: "",
    semester: "",

    // Diploma
    institutionName: "",
    programName: "",
    studyYear: "",

    // Research
    researchProgram: "",
    researchArea: "",
    supervisorName: "",

    // Other
    currentStudyLevel: "",

    // Common academic details
    academicYear: "",
    rollNumber: "",
  });

  // Load saved profile from database
  useEffect(() => {
    const loadProfile = async () => {
      try {
        const data = await api.getStudentProfile(STUDENT_ID);

        setProfile({
          fullName: data.full_name || "",
          email: data.email || "",
          phone: data.phone || "",
          dob: data.dob || "",
          gender: data.gender || "",
          address: data.address || "",
          category: data.category || "",

          schoolName: data.school_name || "",
          schoolBoard: data.school_board || "",
          classLevel: data.class_level || "",

          college: data.college || "",
          department: data.department || "",
          course: data.course || "",
          semester: data.semester || "",

          institutionName: data.institution_name || "",
          programName: data.program_name || "",
          studyYear: data.study_year || "",

          researchProgram: data.research_program || "",
          researchArea: data.research_area || "",
          supervisorName: data.supervisor_name || "",

          currentStudyLevel: data.current_study_level || "",
          academicYear: data.academic_year || "",
          rollNumber: data.roll_number || "",
        });

        setProfileImage(data.profile_picture_url || null);

      } catch (error) {
        console.error("Profile loading error:", error);
        alert("Unable to load your profile: " + error.message);
      }
    };

    loadProfile();
  }, []);

  // Academic fields to clear when the category changes
  const academicFields = [
    "schoolName",
    "schoolBoard",
    "classLevel",
    "college",
    "department",
    "course",
    "semester",
    "institutionName",
    "programName",
    "studyYear",
    "researchProgram",
    "researchArea",
    "supervisorName",
    "currentStudyLevel",
    "academicYear",
    "rollNumber",
  ];

  // Required fields for each category
  const commonRequiredFields = [
    "fullName",
    "email",
    "address",
    "category",
  ];

  const categoryRequiredFields = {
    "School Student": [
      "schoolName",
      "schoolBoard",
      "classLevel",
      "academicYear",
    ],

    "Undergraduate Student": [
      "college",
      "department",
      "course",
      "semester",
      "academicYear",
    ],

    "Postgraduate Student": [
      "college",
      "department",
      "course",
      "semester",
      "academicYear",
    ],

    "Diploma Student": [
      "institutionName",
      "programName",
      "studyYear",
      "academicYear",
    ],

    "Research Scholar": [
      "college",
      "department",
      "researchProgram",
      "researchArea",
      "academicYear",
    ],

    Other: [
      "institutionName",
      "programName",
      "currentStudyLevel",
      "academicYear",
    ],
  };

  const requiredFields = [
    ...commonRequiredFields,
    ...(categoryRequiredFields[profile.category] || []),
  ];

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;

    if (name === "category") {
      setProfile((prev) => {
        const updatedProfile = { ...prev, category: value };

        academicFields.forEach((field) => {
          updatedProfile[field] = "";
        });

        return updatedProfile;
      });

      return;
    }

    setProfile((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  // Profile completion
  const completedFields = requiredFields.filter(
    (field) => String(profile[field] || "").trim() !== ""
  ).length;

  const completion = Math.round(
    (completedFields / requiredFields.length) * 100
  );

  // Save profile
  const handleSave = () => {
    const missingFields = requiredFields.filter(
      (field) => !String(profile[field] || "").trim()
    );

    if (missingFields.length > 0) {
      alert("Please complete all mandatory fields.");
      return;
    }

    stopCamera();
    cancelImagePreview();

    setIsEditing(false);

    alert("Profile saved successfully!");

    // Backend database integration will be added later.
  };

  // Cancel editing
  const handleCancel = () => {
    stopCamera();
    cancelImagePreview();
    setIsEditing(false);
  };

  // Render input fields
  const renderInput = (
    label,
    name,
    type = "text",
    required = false
  ) => (
    <div className="profile-field" key={name}>
      <label>
        {label}
        {required && <span className="required">*</span>}
      </label>

      <input
        type={type}
        name={name}
        value={profile[name] || ""}
        onChange={handleChange}
        disabled={!isEditing}
        required={required}
      />
    </div>
  );

  // Render dropdown fields
  const renderSelect = (
    label,
    name,
    options,
    required = false
  ) => (
    <div className="profile-field" key={name}>
      <label>
        {label}
        {required && <span className="required">*</span>}
      </label>

      <select
        name={name}
        value={profile[name] || ""}
        onChange={handleChange}
        disabled={!isEditing}
        required={required}
      >
        <option value="">Select {label}</option>

        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
    </div>
  );

  // Handle image upload
  const handleImageChange = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    if (!file.type.startsWith("image/")) {
      alert("Please select a valid image.");
      e.target.value = "";
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert("Image size must be less than 5 MB.");
      e.target.value = "";
      return;
    }

    const reader = new FileReader();

    reader.onloadend = () => {
      setImagePreview(reader.result);
    };

    reader.readAsDataURL(file);
  };

  // Start camera
  const startCamera = async () => {
    try {
      if (!navigator.mediaDevices?.getUserMedia) {
        alert("Camera access is not supported by this browser.");
        return;
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user" },
        audio: false,
      });

      setCameraStream(stream);
      setShowCamera(true);
    } catch (error) {
      console.error("Camera error:", error);

      if (
        error.name === "NotAllowedError" ||
        error.name === "PermissionDeniedError"
      ) {
        alert("Please allow camera permission in your browser settings.");
      } else if (error.name === "NotFoundError") {
        alert("No camera was found on this device.");
      } else {
        alert("Unable to access the camera.");
      }
    }
  };

  // Attach camera stream
  useEffect(() => {
    if (showCamera && videoRef.current && cameraStream) {
      videoRef.current.srcObject = cameraStream;
    }
  }, [showCamera, cameraStream]);

  // Stop camera when component unmounts
  useEffect(() => {
    return () => {
      if (cameraStream) {
        cameraStream.getTracks().forEach((track) => track.stop());
      }
    };
  }, [cameraStream]);

  // Stop camera
  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach((track) => track.stop());
    }

    setCameraStream(null);
    setShowCamera(false);
  };

  // Capture photo
  const capturePhoto = () => {
    const video = videoRef.current;

    if (!video || !video.videoWidth) {
      alert("Camera is not ready yet. Please try again.");
      return;
    }

    const canvas = document.createElement("canvas");

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const context = canvas.getContext("2d");

    context.drawImage(
      video,
      0,
      0,
      canvas.width,
      canvas.height
    );

    setImagePreview(canvas.toDataURL("image/jpeg", 0.9));

    stopCamera();
  };

  // Confirm picture
  const confirmProfileImage = () => {
    if (!imagePreview) return;

    setProfileImage(imagePreview);
    setImagePreview(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // Remove profile picture
  const removeProfileImage = () => {
    setProfileImage(null);
    setImagePreview(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // Cancel picture preview
  const cancelImagePreview = () => {
    setImagePreview(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  // Display academic subtitle
  const getAcademicSubtitle = () => {
    switch (profile.category) {
      case "School Student":
        return profile.classLevel || "School Student";

      case "Undergraduate Student":
      case "Postgraduate Student":
        return profile.course || profile.category;

      case "Diploma Student":
        return profile.programName || profile.category;

      case "Research Scholar":
        return profile.researchProgram || profile.category;

      case "Other":
        return profile.programName || "Student";

      default:
        return "Student";
    }
  };

  return (
    <div className="profile-page">

      {/* Page Header */}
      <div className="profile-header">
        <div>
          <h1>My Profile</h1>
          <p>Manage your personal and academic information.</p>
        </div>

        <button
          className="profile-edit-btn"
          onClick={() => {
            if (isEditing) {
              handleCancel();
            } else {
              setIsEditing(true);
            }
          }}
        >
          {isEditing ? "Cancel" : "Edit Profile"}
        </button>
      </div>

      <div className="profile-layout">

        {/* Profile Sidebar */}
        <div className="profile-card profile-sidebar">

          {/* Profile Picture */}
          <div className="profile-picture-section">

            <div className="profile-avatar">
              {imagePreview || profileImage ? (
                <img
                  src={imagePreview || profileImage}
                  alt="Profile"
                />
              ) : (
                <span>
                  {profile.fullName
                    ? profile.fullName.charAt(0).toUpperCase()
                    : "S"}
                </span>
              )}
            </div>

            {isEditing && !imagePreview && !showCamera && (
              <div className="picture-options">

                <button
                  type="button"
                  className="picture-option-btn"
                  onClick={() => fileInputRef.current?.click()}
                >
                  Upload Picture
                </button>

                <button
                  type="button"
                  className="picture-option-btn"
                  onClick={startCamera}
                >
                  Take Photo
                </button>

                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                  hidden
                />

              </div>
            )}

            {/* Picture Preview */}
            {imagePreview && (
              <div className="image-preview-controls">
                <p>Picture Preview</p>

                <button
                  type="button"
                  className="profile-save-btn"
                  onClick={confirmProfileImage}
                >
                  Use This Picture
                </button>

                <button
                  type="button"
                  className="profile-cancel-btn"
                  onClick={cancelImagePreview}
                >
                  Cancel
                </button>
              </div>
            )}

            {/* Remove Existing Profile Picture */}
            {isEditing && profileImage && !imagePreview && !showCamera && (
              <button
                type="button"
                className="profile-cancel-btn"
                onClick={removeProfileImage}
              >
                Remove Picture
              </button>
            )}

            {/* Camera */}
            {showCamera && (
              <div className="camera-container">
                <h3>Take Your Profile Picture</h3>

                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="camera-video"
                />

                <div className="camera-actions">
                  <button
                    type="button"
                    className="profile-save-btn"
                    onClick={capturePhoto}
                  >
                    Capture Photo
                  </button>

                  <button
                    type="button"
                    className="profile-cancel-btn"
                    onClick={stopCamera}
                  >
                    Close Camera
                  </button>
                </div>
              </div>
            )}

          </div>

          <h2>{profile.fullName || "Student Name"}</h2>
          <p>{getAcademicSubtitle()}</p>

          {/* Completion */}
          <div className="profile-progress">
            <div className="progress-heading">
              <span>Profile Completion</span>
              <strong>{completion}%</strong>
            </div>

            <div className="progress-track">
              <div
                className="progress-fill"
                style={{ width: `${completion}%` }}
              />
            </div>
          </div>

          {/* Account Status */}
          <div className="profile-status">
            <span className="status-dot" />
            Account Active
          </div>

        </div>

        {/* Main Profile Information */}
        <div className="profile-main">

          {/* Personal Information */}
          <section className="profile-card">
            <h2>Personal Information</h2>

            <div className="profile-grid">

              {renderInput("Full Name", "fullName", "text", true)}

              {renderInput("Email Address", "email", "email", true)}

              {renderInput("Phone Number", "phone", "tel")}

              {renderInput("Date of Birth", "dob", "date")}

              {renderSelect(
                "Gender",
                "gender",
                ["Male", "Female", "Other", "Prefer not to say"]
              )}

              {renderInput("Address", "address", "text", true)}

            </div>
          </section>

          {/* Academic Information */}
          <section className="profile-card">
            <h2>Academic Information</h2>

            <div className="profile-grid">

              {renderSelect(
                "Student Category",
                "category",
                [
                  "School Student",
                  "Undergraduate Student",
                  "Postgraduate Student",
                  "Diploma Student",
                  "Research Scholar",
                  "Other",
                ],
                true
              )}

              {/* School Student */}
              {profile.category === "School Student" && (
                <>
                  {renderInput("School Name", "schoolName", "text", true)}

                  {renderSelect(
                    "Education Board",
                    "schoolBoard",
                    ["CBSE", "ICSE", "State Board", "Other"],
                    true
                  )}

                  {renderSelect(
                    "Class",
                    "classLevel",
                    [
                      "Class 1", "Class 2", "Class 3", "Class 4",
                      "Class 5", "Class 6", "Class 7", "Class 8",
                      "Class 9", "Class 10", "Class 11", "Class 12",
                      "Other",
                    ],
                    true
                  )}
                </>
              )}

              {/* Undergraduate and Postgraduate */}
              {(profile.category === "Undergraduate Student" ||
                profile.category === "Postgraduate Student") && (
                <>
                  {renderInput(
                    "College / University",
                    "college",
                    "text",
                    true
                  )}

                  {renderInput("Department", "department", "text", true)}

                  {renderInput("Course / Degree", "course", "text", true)}

                  {renderSelect(
                    "Current Semester",
                    "semester",
                    [
                      "1st Semester",
                      "2nd Semester",
                      "3rd Semester",
                      "4th Semester",
                      "5th Semester",
                      "6th Semester",
                      "7th Semester",
                      "8th Semester",
                      "9th Semester",
                      "10th Semester",
                    ],
                    true
                  )}
                </>
              )}

              {/* Diploma Student */}
              {profile.category === "Diploma Student" && (
                <>
                  {renderInput(
                    "Institution Name",
                    "institutionName",
                    "text",
                    true
                  )}

                  {renderInput(
                    "Diploma Programme",
                    "programName",
                    "text",
                    true
                  )}

                  {renderSelect(
                    "Current Year",
                    "studyYear",
                    ["1st Year", "2nd Year", "3rd Year", "4th Year"],
                    true
                  )}
                </>
              )}

              {/* Research Scholar */}
              {profile.category === "Research Scholar" && (
                <>
                  {renderInput(
                    "University / Institution",
                    "college",
                    "text",
                    true
                  )}

                  {renderInput("Department", "department", "text", true)}

                  {renderInput(
                    "Research Programme",
                    "researchProgram",
                    "text",
                    true
                  )}

                  {renderInput(
                    "Research Area",
                    "researchArea",
                    "text",
                    true
                  )}

                  {renderInput(
                    "Supervisor Name",
                    "supervisorName"
                  )}
                </>
              )}

              {/* Other */}
              {profile.category === "Other" && (
                <>
                  {renderInput(
                    "Institution Name",
                    "institutionName",
                    "text",
                    true
                  )}

                  {renderInput(
                    "Programme",
                    "programName",
                    "text",
                    true
                  )}

                  {renderInput(
                    "Current Study Level",
                    "currentStudyLevel",
                    "text",
                    true
                  )}
                </>
              )}

              {/* Academic Year */}
              {profile.category && renderInput(
                "Academic Year",
                "academicYear",
                "text",
                true
              )}

              {/* Roll Number */}
              {profile.category && renderInput(
                "Roll Number / Student ID",
                "rollNumber"
              )}

            </div>
          </section>

          {/* Save Buttons */}
          {isEditing && (
            <div className="profile-actions">

              <button
                type="button"
                className="profile-cancel-btn"
                onClick={handleCancel}
              >
                Cancel
              </button>

              <button
                type="button"
                className="profile-save-btn"
                onClick={handleSave}
              >
                Save Changes
              </button>

            </div>
          )}

        </div>
      </div>
    </div>
  );
}

export default ProfilePage;