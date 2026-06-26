from ninja import Schema
from datetime import datetime
from typing import Any

class ApiResponseSchema(Schema):
    success: bool
    message: str
    data: Any


# ================= USER =================

class UserOut(Schema):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str


class RegisterSchema(Schema):
    username: str
    password: str
    email: str
    first_name: str
    last_name: str


# ================= COURSE =================

class CourseIn(Schema):
    name: str
    description: str
    price: int


class CourseOut(Schema):
    id: int
    name: str
    description: str
    price: int
    teacher: UserOut
    created_at: datetime
    updated_at: datetime


# ================= Announcement =================
class AnnouncementCreateSchema(Schema):
    title: str
    content: str


class AnnouncementResponseSchema(Schema):
    id: int
    title: str
    content: str
    created_at: datetime

class StudentDashboardSchema(Schema):
    username: str
    total_courses: int
    enrolled_courses: int
    completed_courses: int
    ongoing_courses: int

class InstructorDashboardSchema(Schema):
    username: str
    total_courses: int
    total_students: int
    total_announcements: int