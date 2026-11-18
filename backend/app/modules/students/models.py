from sqlmodel import SQLModel, Field
from typing import Optional


class Student(SQLModel, table=True):
    # Basic student information
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    email: str = Field(index=True, unique=True)

    # Existing study settings
    timezone: str = "Asia/Kolkata"
    daily_study_minutes: int = 180

    # Personal information
    phone: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    profile_picture_url: Optional[str] = None

    # Student category
    category: Optional[str] = None

    # School information
    school_name: Optional[str] = None
    school_board: Optional[str] = None
    class_level: Optional[str] = None

    # Undergraduate / Postgraduate information
    college: Optional[str] = None
    department: Optional[str] = None
    course: Optional[str] = None
    semester: Optional[str] = None

    # Diploma information
    institution_name: Optional[str] = None
    program_name: Optional[str] = None
    study_year: Optional[str] = None

    # Research information
    research_program: Optional[str] = None
    research_area: Optional[str] = None
    supervisor_name: Optional[str] = None

    # Other category
    current_study_level: Optional[str] = None

    # Common academic information
    academic_year: Optional[str] = None
    roll_number: Optional[str] = None