# Simple LMS API

Simple LMS adalah aplikasi Learning Management System (LMS) sederhana yang dibangun menggunakan Django dan Django Ninja. Project ini digunakan untuk mempelajari pengembangan backend modern menggunakan PostgreSQL, Redis, MongoDB, Docker, JWT Authentication, dan REST API.

---

## Features

- JWT Authentication
- CRUD Course
- Course Filtering & Pagination
- Course Image Upload
- Redis Cache
- MongoDB Activity Logging
- RabbitMQ Message Broker
- Celery Async Task Processing
- Asynchronous Course Report Generation
- Flower Monitoring

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
| RabbitMQ      | Message Broker          |
| Celery        | Async Task Queue        |
| Flower        | Celery Monitoring       |
| Docker        | Containerization        |
| JWT           | Authentication          |

---
# Project Structure

```text
analytics/  -> MongoDB logging & Celery async tasks
config/     -> Django settings, API routes, Celery configuration
lms/        -> Core LMS application
media/      -> Uploaded course images
screenshot/ -> Documentation screenshots
```

```text
simple-lms/
├── analytics/
├── config/
├── lms/
├── media/
├── screenshot/
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
└── README.md
```

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

Flower Monitoring:

http://localhost:5555


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

## MongoDB Activity Logging

Aplikasi menggunakan MongoDB untuk menyimpan aktivitas pengguna.

Aktivitas yang dicatat:

- CREATE_COURSE
- UPDATE_COURSE
- DELETE_COURSE

Data disimpan pada collection:

analytics_logs

Contoh data:

{
  "user_id": 2,
  "username": "nandika",
  "action": "CREATE_COURSE",
  "metadata": {
    "course_id": 4,
    "course_name": "IPSSS"
  },
  "created_at": "2026-06-17T11:20:00Z"
}

## Async Task Processing

Project menggunakan:

- RabbitMQ sebagai Message Broker
- Celery sebagai Task Queue
- Redis sebagai Result Backend
- Flower untuk monitoring task

Service yang berjalan:

- web
- db
- redis
- mongodb
- rabbitmq
- celery_worker
- celery_beat
- flower

## Generate Course Report

Generate report secara asynchronous menggunakan Celery.

### Generate Report

POST

/api/v1/reports/generate/{course_id}

Response:

{
  "task_id": "296daed6-1854-47d7-b454-c564ab26f30a",
  "status": "processing",
  "course": "IPSSS"
}

### Check Report Status

GET

/api/v1/reports/status/{task_id}

Response:

{
  "task_id": "296daed6-1854-47d7-b454-c564ab26f30a",
  "status": "SUCCESS",
  "result": {
    "course_id": 4,
    "course_name": "IPSSS",
    "price": 6,
    "teacher": "nandika"
  }
}

## Docker Services

| Service | Port |
|----------|--------|
| Django | 8000 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| MongoDB | 27017 |
| RabbitMQ | 5672 |
| RabbitMQ Management | 15672 |
| Flower | 5555 |

## Verification

### MongoDB Logging

1. Create / Update / Delete Course
2. Open MongoDB shell
3. Check analytics_logs collection

### Celery Async Task

1. Generate report:
POST /api/v1/reports/generate/{course_id}

2. Copy task_id

3. Check status:
GET /api/v1/reports/status/{task_id}

4. Status SUCCESS menandakan task berhasil diproses oleh Celery Worker.

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
* Chapter 12 – Message Brokers & Async Tasks (RabbitMQ + Celery)

---

# Author

Nandika Rizki Prapanca

A11.2023.15179

Universitas Dian Nuswantoro
