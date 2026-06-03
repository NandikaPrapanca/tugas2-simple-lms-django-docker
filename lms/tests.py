from django.test import TestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from lms.models import (
    Course,
    Enrollment,
    Category
)

User = get_user_model()


class CourseModelTest(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher",
            password="123456",
            role="instructor"
        )

    def test_create_course(self):
        course = Course.objects.create(
            name="Django",
            description="Belajar Django",
            price=100000,
            teacher=self.teacher
        )

        self.assertEqual(course.name, "Django")
        self.assertEqual(course.price, 100000)
        self.assertEqual(course.teacher, self.teacher)

    def test_default_price(self):
        course = Course.objects.create(
            name="Free Course",
            teacher=self.teacher
        )

        # sesuai model.py
        self.assertEqual(course.price, 10000)

    def test_default_description(self):
        course = Course.objects.create(
            name="Python Course",
            teacher=self.teacher
        )

        self.assertEqual(course.description, "-")

    def test_teacher_relationship(self):
        Course.objects.create(
            name="Course 1",
            teacher=self.teacher
        )

        Course.objects.create(
            name="Course 2",
            teacher=self.teacher
        )

        self.assertEqual(
            self.teacher.courses.count(),
            2
        )


class EnrollmentModelTest(TestCase):

    def setUp(self):
        self.teacher = User.objects.create_user(
            username="teacher",
            password="123456",
            role="instructor"
        )

        self.student = User.objects.create_user(
            username="student",
            password="123456",
            role="student"
        )

        self.course = Course.objects.create(
            name="Django",
            teacher=self.teacher
        )

    def test_create_enrollment(self):
        enrollment = Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.course, self.course)

    def test_unique_enrollment(self):
        Enrollment.objects.create(
            student=self.student,
            course=self.course
        )

        with self.assertRaises(IntegrityError):
            Enrollment.objects.create(
                student=self.student,
                course=self.course
            )


class CategoryModelTest(TestCase):

    def test_create_category(self):
        category = Category.objects.create(
            name="Programming"
        )

        self.assertEqual(category.name, "Programming")

    def test_parent_category(self):
        parent = Category.objects.create(
            name="Programming"
        )

        child = Category.objects.create(
            name="Python",
            parent=parent
        )

        self.assertEqual(child.parent, parent)

    def test_category_str(self):
        category = Category.objects.create(
            name="Django"
        )

        self.assertEqual(str(category), "Django")