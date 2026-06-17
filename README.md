# Simple LMS API

Simple LMS adalah aplikasi Learning Management System (LMS) sederhana yang dibangun menggunakan Django dan Django Ninja. Project ini digunakan untuk mempelajari pengembangan backend modern menggunakan PostgreSQL, Redis, MongoDB, Docker, JWT Authentication, dan REST API.

---

## Features

### Authentication & Authorization

* User Registration
* JWT Authentication
* Access Token & Refresh Token
* Protected API Endpoint

### Course Management

* Create Course
* Read Course
* Update Course
* Partial Update (PATCH)
* Delete Course
* Upload Course Image

### Advanced API Features

* Filtering
* Searching
* Ordering
* Pagination

### Database

* PostgreSQL sebagai database utama
* Django ORM
* Query Optimization menggunakan:

  * select_related()
  * prefetch_related()

### Redis

* Redis Cache
* Redis Session Storage

### MongoDB

* Activity Logging
* Log Create Course
* Log Update Course
* Log Delete Course

---

# Technology Stack

| Technology    | Description             |
| ------------- | ----------------------- |
| Django 5      | Backend Framework       |
| Django Ninja  | REST API Framework      |
| PostgreSQL 15 | Relational Database     |
| Redis 7       | Cache & Session Storage |
| MongoDB 7     | Activity Logging        |
| Docker        | Containerization        |
| JWT           | Authentication          |

---

# Project Structure

```text
simple-lms/
│
├── analytics/
│   ├── mongo.py
│   └── services.py
│
├── lms/
│   ├── models.py
│   ├── schemas.py
│   ├── admin.py
│   └── helpers.py
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── apiv1.py
│
├── media/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# Installation

## 1. Clone Repository

```bash
git clone https://github.com/NandikaPrapanca/tugas2-simple-lms-django-docker.git
cd tugas2-simple-lms-django-docker
```

## 2. Build Docker Image

```bash
docker compose build
```

## 3. Run Container

```bash
docker compose up -d
```

## 4. Run Migration

```bash
docker compose exec web python manage.py migrate
```

## 5. Create Superuser

```bash
docker compose exec web python manage.py createsuperuser
```

---

# API Documentation

Swagger UI:

```text
http://localhost:8000/api/v1/docs
```

Admin Panel:

```text
http://localhost:8000/admin
```

---

# Authentication

Login endpoint:

```http
POST /api/v1/auth/pair
```

Request:

```json
{
  "username": "nandika",
  "password": "yourpassword"
}
```

Response:

```json
{
  "access": "jwt_access_token",
  "refresh": "jwt_refresh_token"
}
```

Gunakan access token pada tombol Authorize Swagger:

```text
Bearer <access_token>
```

---

# Redis Caching

Redis digunakan untuk:

* Cache Course Detail
* Session Storage

Verifikasi Redis:

```bash
docker compose exec redis redis-cli
```

```redis
SELECT 1
KEYS *
```

Contoh hasil:

```text
simple_lms:1:course_detail:3
simple_lms:1:django.contrib.sessions.cachexxxx
```

---

# MongoDB Activity Logging

MongoDB digunakan untuk menyimpan aktivitas pengguna.

Contoh log:

```json
{
  "user_id": 2,
  "username": "nandika",
  "action": "CREATE_COURSE",
  "metadata": {
    "course_id": 4,
    "course_name": "IPS"
  }
}
```

Verifikasi MongoDB:

```bash
docker compose exec mongodb mongosh -u admin -p password123
```

```javascript
use lms_analytics

db.activity_logs.find().pretty()
```

---

# Environment Variables

Contoh file .env.example

```env
POSTGRES_DB=lms_db
POSTGRES_USER=Nandika
POSTGRES_PASSWORD=lms_password
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

---

# Learning Chapters Implemented

* Chapter 1 – Backend Development Introduction
* Chapter 2 – Docker Basics
* Chapter 3 – Docker Multi Container & Compose
* Chapter 4 – Django ORM & Models
* Chapter 5 – Database Optimization
* Chapter 6 – REST API with Django Ninja
* Chapter 7 – Authentication & Authorization
* Chapter 8 – Advanced API Features
* Chapter 10 – Redis
* Chapter 11 – MongoDB

---

# Author

Nandika Rizki Prapanca

A11.2023.15179

Universitas Dian Nuswantoro
