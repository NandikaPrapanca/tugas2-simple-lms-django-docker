from ninja import NinjaAPI
from ninja.errors import HttpError
from ninja_simple_jwt.auth.views.api import mobile_auth_router
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.db.models import Q
from analytics.logger import log_activity
from typing import List, Optional
from lms.models import Course, Announcement, Enrollment, Progress, Lesson
from lms.schemas import (
    CourseIn,
    CourseOut,
    RegisterSchema,
    UserOut,
    AnnouncementCreateSchema,
    AnnouncementResponseSchema,
    StudentDashboardSchema,
    InstructorDashboardSchema,
    ApiResponseSchema
)
from lms.helpers import get_object_or_404, success_response, error_response
from ninja import (
    Schema,
    File,
    UploadedFile,
    Query,
    FilterSchema,
    Field
)
from ninja.pagination import paginate, PageNumberPagination
from analytics.tasks import (
    generate_course_report,
    cleanup_logs,
)
from celery.result import AsyncResult

User = get_user_model()

# ================= API =================

api = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
)

# JWT ROUTER
api.add_router("/auth/", mobile_auth_router)

# JWT AUTH
apiAuth = HttpJwtAuth()

# ================= FILTER =================

class CourseFilter(FilterSchema):

    search: Optional[str] = Field(
        None,
        q=['name__icontains', 'description__icontains']
    )

    price: Optional[int] = None

    def filter_price(self, value: int) -> Q:
        return Q(price__gt=value)


# ================= PATCH SCHEMA =================

class CourseUpdate(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[int] = None


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

@api.get(
    "/courses/",
    auth=apiAuth,
    response=List[CourseOut],
    tags=["Courses"],
)
@paginate(PageNumberPagination, page_size=10)
def list_courses(
    request,
    filters: CourseFilter = Query(...),
    ordering: str = "-created_at",
):

    user = User.objects.get(id=request.user.id)

    # Cache berbeda untuk setiap user
    cache_key = f"courses_list_{user.id}_{user.role}_{ordering}"

    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    allowed_fields = [
        "name",
        "-name",
        "price",
        "-price",
        "created_at",
        "-created_at",
    ]

    if ordering not in allowed_fields:
        ordering = "-created_at"

    # ==========================
    # Permission & Ownership
    # ==========================

    if user.is_superuser:
        qs = Course.objects.select_related("teacher").all()

    elif user.role == "teacher":
        qs = Course.objects.select_related("teacher").filter(
            teacher=user
        )

    else:  # student
        qs = Course.objects.select_related("teacher").all()

    qs = filters.filter(qs)
    qs = qs.order_by(ordering)

    data = list(qs)

    cache.set(cache_key, data, timeout=300)

    return data

@api.post(
    "/courses/{course_id}/enroll/",
    auth=apiAuth,
    tags=["Enrollment"]
)
def enroll_course(request, course_id: int):

    user = User.objects.get(id=request.user.id)

    # hanya student
    if user.role != "student":
        raise HttpError(
            403,
            "Hanya student yang dapat enroll course"
        )

    course = get_object_or_404(
        Course,
        pk=course_id
    )

    # cek sudah enroll atau belum
    if Enrollment.objects.filter(
        student=user,
        course=course
    ).exists():

        raise HttpError(
            400,
            "Anda sudah enroll pada course ini"
        )

    Enrollment.objects.create(
        student=user,
        course=course
    )

    return {
        "message": "Enroll berhasil",
        "course": course.name
    }

@api.get(
    "/courses/{id}",
    auth=apiAuth,
    response=CourseOut,
    tags=["Courses"],
)
def detail_course(request, id: int):

    cache_key = f"course_detail:{id}"

    cached_data = cache.get(cache_key)

    if cached_data:
        return cached_data

    course = get_object_or_404(
        Course,
        pk=id,
    )

    cache.set(cache_key, course, timeout=300)

    return course


@api.post(
    "/courses/",
    auth=apiAuth,
    response={201: CourseOut},
    tags=["Courses"]
)
def create_course(request, data: CourseIn):

    user = User.objects.get(id=request.user.id)

    # --- PENEMPATAN DI SINI ---
    if user.role != "teacher" and not user.is_superuser:
        raise HttpError(
            403,
            "Hanya teacher yang dapat membuat course"
        )
    
    if data.price < 0:
        raise HttpError(400, "Harga tidak boleh negatif")

    course = Course.objects.create(
        name=data.name,
        description=data.description,
        price=data.price,
        teacher=user,
    )
    log_activity(
    user,
    "CREATE_COURSE",
    {
        "course_id": course.id,
        "course_name": course.name
    }
)

    cache.clear()

    return 201, course


@api.put(
    "/courses/{id}",
    auth=apiAuth,
    response=CourseOut,
    tags=["Courses"]
)
def update_course(request, id: int, data: CourseIn):

    course = get_object_or_404(Course, pk=id)

    user = User.objects.get(id=request.user.id)

    if course.teacher != user:
        raise HttpError(403, "Hanya pemilik course yang dapat mengedit")

    course.name = data.name
    course.description = data.description
    course.price = data.price

    course.save()
    log_activity(
    user,
    "UPDATE_COURSE",
    {
        "course_id": course.id,
        "course_name": course.name
    }
)
    cache.clear()
    cache.delete(f"course_detail:{id}")

    return course


# ================= PATCH COURSE =================

@api.patch(
    "/courses/{id}",
    auth=apiAuth,
    tags=["Courses"]
)
def patch_course(request, id: int, data: CourseUpdate):

    course = get_object_or_404(Course, pk=id)

    user = User.objects.get(id=request.user.id)

    if course.teacher != user:
        raise HttpError(403, "Hanya pemilik course yang dapat mengedit")

    for attr, value in data.dict(exclude_unset=True).items():
        setattr(course, attr, value)

    course.save()

    cache.clear()
    cache.delete(f"course_detail:{id}")

    return success_response(
    "Course berhasil diupdate"
    )


# ================= UPLOAD IMAGE =================

@api.post(
    "/courses/{id}/upload-image/",
    auth=apiAuth,
    tags=["Courses"],
)
def upload_course_image(
    request,
    id: int,
    file: UploadedFile = File(...)
):

    course = get_object_or_404(Course, pk=id)

    user = User.objects.get(id=request.user.id)

    if user.role != "teacher" and not user.is_superuser:
        raise HttpError(
            403,
            "Hanya teacher yang dapat upload image"
        )
    
    if course.teacher != user:
        raise HttpError(403, "Bukan pemilik course")

    if file.size > 2 * 1024 * 1024:
        raise HttpError(400, "Ukuran file maksimal 2MB")

    allowed_types = [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]

    if file.content_type not in allowed_types:
        raise HttpError(400, "File harus JPG/PNG/WebP")

    course.image = file
    course.save()

    return success_response(
    "Image berhasil diupload",
    {
        "filename": file.name
    }
    )


@api.delete(
    "/courses/{id}",
    auth=apiAuth,
    response={204: None},
    tags=["Courses"]
)
def delete_course(request, id: int):

    course = get_object_or_404(Course, pk=id)

    user = User.objects.get(id=request.user.id)

    if course.teacher != user and not user.is_superuser:
        raise HttpError(403, "Anda tidak memiliki izin")
    log_activity(
    user,
    "DELETE_COURSE",
    {
        "course_id": course.id,
        "course_name": course.name
    }
)
    course.delete()

    cache.clear()
    cache.delete(f"course_detail:{id}")

    return 204, None

@api.post(
    "/reports/generate/{course_id}",
    auth=apiAuth,
    tags=["Reports"]
)
def generate_report(request, course_id: int):

    user = User.objects.get(id=request.user.id)

    if user.role != "teacher" and not user.is_superuser:
        raise HttpError(
            403,
            "Hanya teacher yang dapat generate report"
        )
    
    course = get_object_or_404(
        Course,
        pk=course_id
    )

    task = generate_course_report.delay(
        course.id
    )

    return {
        "task_id": task.id,
        "status": "processing",
        "course": course.name
    }


@api.get(
    "/reports/status/{task_id}",
    auth=apiAuth,
    tags=["Reports"]
)
def report_status(request, task_id: str):

    result = AsyncResult(task_id)

    response = {
        "task_id": task_id,
        "status": result.status,
    }

    if result.ready():
        response["result"] = result.result

    return response


@api.post(
    "/courses/{course_id}/announcements/",
    auth=apiAuth,
    response=ApiResponseSchema,
    tags=["Announcements"]
)
def create_announcement(
    request,
    course_id: int,
    data: AnnouncementCreateSchema
):
    user = User.objects.get(id=request.user.id)

    if user.role != "teacher" and not user.is_superuser:
        raise HttpError(
            403,
            "Hanya teacher yang dapat membuat announcement"
        )

    course = get_object_or_404(
        Course,
        pk=course_id
    )

    if course.teacher != user and not user.is_superuser:
        raise HttpError(
            403,
            "Bukan pemilik course"
        )

    announcement = Announcement.objects.create(
        course=course,
        title=data.title,
        content=data.content,
    )

    return success_response(
    "Announcement berhasil dibuat",
    AnnouncementResponseSchema.from_orm(
        announcement
    ).dict()
)

@api.get(
    "/courses/{course_id}/announcements/",
    auth=apiAuth,
    response=ApiResponseSchema,
    tags=["Announcements"]
)
def list_announcements(request, course_id: int):

    course = get_object_or_404(
        Course,
        pk=course_id
    )

    announcements = Announcement.objects.filter(
    course=course
    ).order_by("-created_at")

    data = [
        AnnouncementResponseSchema.from_orm(a).dict()
        for a in announcements
    ]

    return success_response(
        "Daftar announcement berhasil diambil",
        data
    )

@api.get(
    "/student/dashboard/",
    auth=apiAuth,
    tags=["Student"]
)
def student_dashboard(request):

    user = User.objects.get(id=request.user.id)

    if user.role != "student":
        raise HttpError(403, "Hanya student yang dapat mengakses dashboard")

    total_courses = Course.objects.count()

    enrolled_courses = Enrollment.objects.filter(
        student=user
    ).count()

    completed_courses = Enrollment.objects.filter(
        student=user,
        progress__completed=True
    ).distinct().count()

    ongoing_courses = enrolled_courses - completed_courses

    return success_response(
        "Dashboard berhasil diambil",
        {
            "username": user.username,
            "total_courses": total_courses,
            "enrolled_courses": enrolled_courses,
            "completed_courses": completed_courses,
            "ongoing_courses": ongoing_courses,
        }
    )

@api.get(
    "/teacher/dashboard/",
    auth=apiAuth,
    response=ApiResponseSchema,
    tags=["Dashboard"]
)
def teacher_dashboard(request):

    user = User.objects.get(id=request.user.id)

    if user.role != "teacher" and not user.is_superuser:
        raise HttpError(
            403,
            "Hanya teacher yang dapat mengakses dashboard"
        )

    courses = Course.objects.filter(
        teacher=user
    )

    total_courses = courses.count()

    total_students = Enrollment.objects.filter(
        course__teacher=user
    ).count()

    total_announcements = Announcement.objects.filter(
        course__teacher=user
    ).count()

    return success_response(
    "Dashboard berhasil diambil",
    {
        "username": user.username,
        "total_courses": total_courses,
        "total_students": total_students,
        "total_announcements": total_announcements,
    }
    )