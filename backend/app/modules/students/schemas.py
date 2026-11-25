from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class StudentCreate(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    daily_study_minutes: int = Field(default=180, gt=0, le=1440)
    timezone: str = Field(default="Asia/Kolkata", min_length=1)


class StudentRead(StudentCreate):
    id: int


class StudentProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    phone: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    category: Optional[str] = None

    school_name: Optional[str] = None
    school_board: Optional[str] = None
    class_level: Optional[str] = None

    college: Optional[str] = None
    department: Optional[str] = None
    course: Optional[str] = None
    semester: Optional[str] = None

    institution_name: Optional[str] = None
    program_name: Optional[str] = None
    study_year: Optional[str] = None

    research_program: Optional[str] = None
    research_area: Optional[str] = None
    supervisor_name: Optional[str] = None

    current_study_level: Optional[str] = None
    academic_year: Optional[str] = None
    roll_number: Optional[str] = None
    profile_picture_url: Optional[str] = None


class StudentProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    full_name: str
    email: EmailStr

    phone: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    profile_picture_url: Optional[str] = None

    category: Optional[str] = None

    school_name: Optional[str] = None
    school_board: Optional[str] = None
    class_level: Optional[str] = None

    college: Optional[str] = None
    department: Optional[str] = None
    course: Optional[str] = None
    semester: Optional[str] = None

    institution_name: Optional[str] = None
    program_name: Optional[str] = None
    study_year: Optional[str] = None

    research_program: Optional[str] = None
    research_area: Optional[str] = None
    supervisor_name: Optional[str] = None

    current_study_level: Optional[str] = None
    academic_year: Optional[str] = None
    roll_number: Optional[str] = None