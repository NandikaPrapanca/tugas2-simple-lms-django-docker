# Simple LMS - Django Docker Setup

Project ini merupakan setup environment development untuk aplikasi **Django Simple LMS** menggunakan **Docker** dan **PostgreSQL** sebagai database.

## Cara Menjalankan Project

1. Build docker image

```bash
docker compose build
```

2. Jalankan container

```bash
docker compose up
```

3. Jalankan migration database

Buka terminal baru lalu jalankan:

```bash
docker compose exec web python manage.py migrate
```

4. Akses aplikasi

Buka browser dan masuk ke:

```
http://localhost:8000
```

Jika berhasil maka halaman Django akan tampil.

---

## Environment Variables Explanation

Project ini menggunakan environment variables untuk konfigurasi database PostgreSQL.

Contoh isi file `.env.example`:

```
POSTGRES_DB=lmsdb
POSTGRES_USER=lmsuser
POSTGRES_PASSWORD=lmspassword
POSTGRES_HOST=db
POSTGRES_PORT=5432
```

Penjelasan:

| Variable | Fungsi |
|--------|--------|
| POSTGRES_DB | Nama database PostgreSQL |
| POSTGRES_USER | Username database |
| POSTGRES_PASSWORD | Password database |
| POSTGRES_HOST | Host database (container db) |
| POSTGRES_PORT | Port PostgreSQL |

Environment variables ini digunakan oleh Django untuk melakukan koneksi ke database PostgreSQL yang berjalan di dalam container Docker.

---

## Screenshot Django Welcome Page

Berikut adalah tampilan halaman awal Django setelah container berhasil dijalankan.

![Django Welcome Page](screenshot-django.png)

Halaman ini dapat diakses melalui:
http://localhost:8000

Jika halaman ini muncul, berarti:

- Docker container berjalan dengan baik
- Django berhasil dijalankan
- Koneksi ke PostgreSQL berhasil

---

## 📊 Data Models

Project ini mengimplementasikan beberapa model utama:

- **User**
  - Role: admin, instructor, student

- **Category**
  - Mendukung hierarchical (self-referencing)

- **Course**
  - Relasi ke instructor (User)
  - Relasi ke category

- **Lesson**
  - Memiliki urutan (ordering)

- **Enrollment**
  - Relasi student ke course
  - Unique constraint (tidak bisa enroll course yang sama dua kali)

- **Progress**
  - Tracking penyelesaian lesson oleh student

---

## ⚡ Query Optimization

Untuk meningkatkan performa query, digunakan:

### 🔴 Sebelum (N+1 Problem)
Query count: 3

### 🟢 Setelah Optimasi
Query count: 1

### Teknik yang digunakan:
- `select_related()` → untuk relasi ForeignKey
- `prefetch_related()` → untuk relasi banyak data

Optimasi ini mengurangi jumlah query secara signifikan dan meningkatkan performa aplikasi.

---

## 🛠️ Django Admin Features

- List display yang informatif
- Search dan filter
- Inline Lesson pada Course
- Manajemen data User, Course, Enrollment, dan Progress

---

## 👨‍💻 Author

Nandika Rizki Prapanca