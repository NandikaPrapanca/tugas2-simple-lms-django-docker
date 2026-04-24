from ninja import NinjaAPI
from lms.models import Course
from lms.schemas import CourseIn, CourseOut
from typing import List
from ninja.errors import HttpError
from django.contrib.auth import get_user_model

User = get_user_model()

api = NinjaAPI()

@api.get("hello/")
def hello(request):
    return {"message": "API jalan 🚀"}

@api.get("courses/", response=List[CourseOut], tags=["Courses"])
def list_courses(request):
    return Course.objects.select_related("teacher").all()

@api.get("courses/{id}", response=CourseOut, tags=["Courses"])
def detail_course(request, id: int):
    try:
        return Course.objects.select_related("teacher").get(pk=id)
    except Course.DoesNotExist:
        raise HttpError(404, "Course tidak ditemukan")
    
@api.post("courses/", response=CourseOut, tags=["Courses"])
def create_course(request, data: CourseIn):
    teacher = User.objects.first()

    if not teacher:
        raise HttpError(400, "Belum ada user")

    return Course.objects.create(**data.dict(), teacher=teacher)

@api.put("courses/{id}", response=CourseOut, tags=["Courses"])
def update_course(request, id: int, data: CourseIn):
    try:
        course = Course.objects.get(pk=id)
    except Course.DoesNotExist:
        raise HttpError(404, "Course tidak ditemukan")

    for attr, value in data.dict().items():
        setattr(course, attr, value)

    course.save()
    return course

@api.delete("courses/{id}", tags=["Courses"])
def delete_course(request, id: int):
    try:
        course = Course.objects.get(pk=id)
    except Course.DoesNotExist:
        raise HttpError(404, "Course tidak ditemukan")

    course.delete()
    return {"success": True}