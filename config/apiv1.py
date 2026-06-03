from ninja import NinjaAPI
from ninja.errors import HttpError
from ninja_simple_jwt.auth.views.api import mobile_auth_router
from ninja_simple_jwt.auth.ninja_auth import HttpJwtAuth
from django.core.cache import cache

from django.contrib.auth import get_user_model
from django.db.models import Q

from typing import List, Optional

from lms.models import Course
from lms.schemas import (
    CourseIn,
    CourseOut,
    RegisterSchema,
    UserOut,
)

from lms.helpers import get_object_or_404

from ninja import (
    Schema,
    File,
    UploadedFile,
    Query,
    FilterSchema,
    Field
)

from ninja.pagination import paginate, PageNumberPagination

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

    cache_key = "courses_list"

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

    qs = Course.objects.select_related("teacher").all()

    qs = filters.filter(qs)

    qs = qs.order_by(ordering)

    data = list(qs)

    cache.set(cache_key, data, timeout=300)

    return data


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

    if data.price < 0:
        raise HttpError(400, "Harga tidak boleh negatif")

    user = User.objects.get(id=request.user.id)

    course = Course.objects.create(
        name=data.name,
        description=data.description,
        price=data.price,
        teacher=user,
    )

    cache.delete("courses_list")

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

    cache.delete("courses_list")
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

    cache.delete("courses_list")
    cache.delete(f"course_detail:{id}")

    return {
        "message": "Course berhasil diupdate"
    }


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

    return {
        "message": "Image uploaded",
        "filename": file.name
    }


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

    course.delete()

    cache.delete("courses_list")
    cache.delete(f"course_detail:{id}")

    return 204, None