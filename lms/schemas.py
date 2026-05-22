from ninja import Schema
from datetime import datetime


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