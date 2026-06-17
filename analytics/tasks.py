from celery import shared_task
from lms.models import Course
import time


@shared_task
def send_enrollment_notification(
    username,
    course_name
):

    time.sleep(3)

    print(
        f"[EMAIL] User {username} berhasil enroll ke course {course_name}"
    )

    return {
        "user": username,
        "course": course_name,
        "status": "sent"
    }


@shared_task
def generate_course_report(course_id):

    course = Course.objects.get(id=course_id)

    return {
        "course_id": course.id,
        "course_name": course.name,
        "price": course.price,
        "teacher": course.teacher.username
    }


@shared_task
def cleanup_logs():

    print("Cleaning old logs...")

    return {
        "status": "success",
        "message": "Old logs cleaned"
    }