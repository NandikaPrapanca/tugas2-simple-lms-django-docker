from ninja import NinjaAPI
from ninja.errors import HttpError
from ninja_simple_jwt.auth.views.api import mobile_auth_router
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth

from django.contrib.auth import get_user_model
from typing import List

from lms.models import Course
from lms.schemas import (
    CourseIn,
    CourseOut,
    RegisterSchema,
    UserOut,
)

from lms.helpers import get_object_or_404

User = get_user_model()

api = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
)

# JWT ROUTER
api.add_router("/auth/", mobile_auth_router)

# JWT AUTH
apiAuth = HttpJwtAuth()


# ================= AUTH =================

@api.post("/register/", response=UserOut, tags=["Auth"])
def register(request, data: RegisterSchema):

    if User.objects.filter(username=data.username).exists():
        raise HttpError(400, "Username sudah digunakan")

    if User.objects.filter(email=data.email).exists():
        raise HttpError(400, "Email sudah digunakan")

    user = User.objects.create_user(
        username=data.username,
        password=data.password,
        email=data.email,
        first_name=data.first_name,
        last_name=data.last_name,
        role="student"
    )

    return user


# ================= COURSE =================

@api.get("/courses/", auth=apiAuth, response=List[CourseOut], tags=["Courses"])
def list_courses(
    request,
    search: str = None,
):
    qs = Course.objects.select_related("teacher").all()

    if search:
        qs = qs.filter(name__icontains=search)

    return qs


@api.get("/courses/{id}", auth=apiAuth, response=CourseOut, tags=["Courses"])
def detail_course(request, id: int):

    return get_object_or_404(
        Course,
        pk=id,
    )


@api.post("/courses/", auth=apiAuth, response={201: CourseOut}, tags=["Courses"])
def create_course(request, data: CourseIn):

    if data.price < 0:
        raise HttpError(400, "Harga tidak boleh negatif")

    course = Course.objects.create(
        name=data.name,
        description=data.description,
        price=data.price,
        teacher=request.user,
    )

    return 201, course


@api.put("/courses/{id}", auth=apiAuth, response=CourseOut, tags=["Courses"])
def update_course(request, id: int, data: CourseIn):

    course = get_object_or_404(Course, pk=id)

    # authorization
    if course.teacher != request.user:
        raise HttpError(403, "Hanya pemilik course yang dapat mengedit")

    course.name = data.name
    course.description = data.description
    course.price = data.price

    course.save()

    return course


@api.delete("/courses/{id}", auth=apiAuth, response={204: None}, tags=["Courses"])
def delete_course(request, id: int):

    course = get_object_or_404(Course, pk=id)

    # authorization
    if course.teacher != request.user and not request.user.is_superuser:
        raise HttpError(403, "Anda tidak memiliki izin")

    course.delete()

    return 204, None