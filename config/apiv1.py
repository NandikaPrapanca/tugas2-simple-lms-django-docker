from ninja import NinjaAPI
from ninja.errors import HttpError
from lms.models import User
from typing import List

from lms.models import Course, Lesson

from lms.schemas import (
    CourseIn,
    CourseOut,
    CourseContentIn,
    CourseContentOut,
)

from lms.helpers import get_object_or_404


api = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
    description="REST API Simple LMS menggunakan Django Ninja"
)

# =================================================
# COURSE
# =================================================

@api.get(
    "/courses/",
    response=List[CourseOut],
    tags=["Courses"]
)
def list_courses(
    request,
    search: str = None,
):
    """
    Mengambil daftar semua course.
    """

    qs = Course.objects.select_related(
        "teacher"
    ).all()

    if search:
        qs = qs.filter(name__icontains=search)

    return qs


@api.get(
    "/courses/{id}",
    response=CourseOut,
    tags=["Courses"]
)
def detail_course(request, id: int):
    """
    Mengambil detail course.
    """

    return get_object_or_404(
        Course,
        pk=id
    )


@api.post(
    "/courses/",
    response={201: CourseOut},
    tags=["Courses"]
)
def create_course(request, data: CourseIn):
    """
    Membuat course baru.
    """

    if data.price < 0:
        raise HttpError(
            400,
            "Harga tidak boleh negatif"
        )

    teacher = User.objects.first()

    if not teacher:
        raise HttpError(
            400,
            "Teacher tidak ditemukan"
        )

    course = Course.objects.create(
        **data.dict(),
        teacher=teacher
    )

    return 201, course


@api.put(
    "/courses/{id}",
    response=CourseOut,
    tags=["Courses"]
)
def update_course(request, id: int, data: CourseIn):
    """
    Mengupdate course.
    """

    course = get_object_or_404(
        Course,
        pk=id
    )

    for attr, value in data.dict().items():
        setattr(course, attr, value)

    course.save()

    return course


@api.delete(
    "/courses/{id}",
    response={204: None},
    tags=["Courses"]
)
def delete_course(request, id: int):
    """
    Menghapus course.
    """

    course = get_object_or_404(
        Course,
        pk=id
    )

    course.delete()

    return 204, None


# =================================================
# CONTENT / LESSON
# =================================================

@api.get(
    "/contents/",
    response=List[CourseContentOut],
    tags=["Contents"]
)
def list_contents(
    request,
    course_id: int = None,
):
    """
    Mengambil semua content.
    """

    qs = Lesson.objects.select_related(
        "course"
    ).all()

    if course_id:
        qs = qs.filter(course_id=course_id)

    return qs


@api.get(
    "/contents/{id}",
    response=CourseContentOut,
    tags=["Contents"]
)
def detail_content(request, id: int):
    """
    Mengambil detail content.
    """

    return get_object_or_404(
        Lesson,
        pk=id
    )


@api.post(
    "/contents/",
    response={201: CourseContentOut},
    tags=["Contents"]
)
def create_content(request, data: CourseContentIn):
    """
    Membuat content baru.
    """

    course = get_object_or_404(
        Course,
        pk=data.course_id
    )

    content = Lesson.objects.create(
        title=data.name,
        course=course,
        order=1,
    )

    return 201, content


@api.put(
    "/contents/{id}",
    response=CourseContentOut,
    tags=["Contents"]
)
def update_content(request, id: int, data: CourseContentIn):
    """
    Mengupdate content.
    """

    content = get_object_or_404(
        Lesson,
        pk=id
    )

    course = get_object_or_404(
        Course,
        pk=data.course_id
    )

    content.title = data.name
    content.course = course

    content.save()

    return content


@api.delete(
    "/contents/{id}",
    response={204: None},
    tags=["Contents"]
)
def delete_content(request, id: int):
    """
    Menghapus content.
    """

    content = get_object_or_404(
        Lesson,
        pk=id
    )

    content.delete()

    return 204, None