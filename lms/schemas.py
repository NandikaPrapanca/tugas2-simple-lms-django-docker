from ninja import Schema
from typing import Optional
from datetime import datetime

class UserOut(Schema):
    id: int
    username: str
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