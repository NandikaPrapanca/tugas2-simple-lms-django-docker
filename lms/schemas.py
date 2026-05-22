from ninja import Schema
from datetime import datetime
from typing import Optional


class UserOut(Schema):
    id: int
    username: str
    first_name: str
    last_name: str
    email: str


class CourseIn(Schema):
    name: str
    description: str = "-"
    price: int = 10000


class CourseOut(Schema):
    id: int
    name: str
    description: str
    price: int
    teacher: UserOut
    created_at: datetime
    updated_at: datetime


class CourseContentIn(Schema):
    name: str
    course_id: int


class CourseContentOut(Schema):
    id: int
    title: str
    order: int
    course_id: int