# Cyber Asset Management

## Daftar Isi

- [Overview](#overview)
- [Features](#features)
- [Access Control](#access-control)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database & Migration](#database--migration)
- [Running the Application](#running-the-application)
- [Documentation](#documentation)

---

## Overview

Aplikasi manajemen aset untuk Divisi Cyber dengan sistem pencatatan, pengelompokan, pelacakan, dan pengelolaan aset secara terstruktur. Sistem mendukung proses peminjaman dan pengembalian aset dengan audit trail lengkap.

Setiap aset wajib memiliki kode unik (asset_code) yang bersifat permanen sebagai identitas utama untuk menjamin konsistensi dan integritas data. Sistem mampu melakukan pencatatan, pengelompokan, pelacakan, serta pengelolaan status aset secara terstruktur dan terkontrol.

## Features

- ✅ **Manajemen Aset**: Pencatatan aset dengan kode unik permanen (asset_code)
- ✅ **Kategori Aset**: Pengelompokan aset berdasarkan kategori
- ✅ **Peminjaman & Pengembalian**: Sistem peminjaman dan pengembalian aset dengan pencatatan lengkap
- ✅ **Pelacakan Status**: Pelacakan status aset secara real-time (available, borrowed, maintenance, dll)
- ✅ **Person In Charge (PIC)**: Penetapan PIC untuk setiap aset
- ✅ **Role-Based Access Control (RBAC)**: Kontrol akses berbasis role (Super Admin & User)
- ✅ **Audit Logging**: Pencatatan semua aktivitas untuk monitoring dan keamanan
- ✅ **JWT Authentication**: Sistem autentikasi menggunakan JWT tokens
- ✅ **Data Privacy**: Data peminjaman bersifat privat, hanya owner dan Super Admin yang dapat mengakses

## Access Control

Sistem menggunakan **Role-Based Access Control (RBAC)** dengan dua tingkat akses:

### Super Admin (Full Access)

Memiliki akses penuh terhadap seluruh fitur sistem:

- ✅ **User Management**: Create, update, delete, dan nonaktifkan users
- ✅ **Role Management**: Manage roles
- ✅ **Asset Management**: Create, update, delete assets
- ✅ **Category Management**: Manage asset categories
- ✅ **Loan Management**: View semua loans, manage any loan
- ✅ **Audit Logs**: View semua audit logs dan riwayat aktivitas

**Hanya Super Admin yang diperbolehkan:**
- Menambahkan, mengubah, atau menonaktifkan pengguna lain
- Mengakses data peminjaman milik pengguna lain
- Melihat audit logs

### User (Limited Access)

Memiliki akses terbatas:

- ✅ **View Assets**: Melihat daftar aset
- ✅ **View Categories**: Melihat kategori aset
- ✅ **Create Loan**: Melakukan peminjaman aset
- ✅ **Return Loan**: Mengembalikan aset
- ✅ **View Own Loans**: Melihat riwayat peminjaman sendiri

**User TIDAK diperbolehkan:**
- ❌ Menambahkan atau mengelola pengguna lain
- ❌ Mengubah data aset
- ❌ Melihat data peminjaman milik pengguna lain
- ❌ Mengakses audit logs

### Data Privacy

Data peminjaman bersifat privat:
- Hanya pemilik data peminjaman dan Super Admin yang dapat mengaksesnya
- User hanya dapat melihat dan mengelola peminjaman miliknya sendiri

Untuk dokumentasi lengkap tentang authorization, lihat [docs/AUTHORIZATION.md](docs/AUTHORIZATION.md)

## Tech Stack

- **Framework**: FastAPI 0.120.4
- **Database**: PostgreSQL 12+
- **ORM**: SQLAlchemy 2.0.44
- **Migration**: Alembic 1.17.1
- **Authentication**: JWT (python-jose 3.5.0)
- **Password Hashing**: bcrypt (passlib 1.7.4)
- **Validation**: Pydantic 2.12.3
- **Server**: Uvicorn 0.38.0

## Installation

### Prerequisites

- Python 3.10+
- PostgreSQL 12+
- pip atau poetry

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd cyber-asset-management
```

### Step 2: Create Virtual Environment

```bash
# Menggunakan venv
python -m venv venv

# Aktifkan virtual environment
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables

Buat file `.env` di root project dengan konfigurasi berikut:

```env
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/dbmu

# JWT Configuration
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

**Catatan Penting:**
- Ganti `username`, `password`, dan `cyber_asset_db` dengan konfigurasi database Anda
- Generate `SECRET_KEY` yang kuat untuk production (minimal 32 karakter)
- Jangan commit file `.env` ke repository

### Generate Secret Key

```bash
# Menggunakan OpenSSL
openssl rand -hex 32

# Atau menggunakan Python
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Database & Migration

### Step 1: Create Database

```bash
# Login ke PostgreSQL
psql -U postgres

# Buat database
CREATE DATABASE cyber_asset_db;

# Buat user (optional)
CREATE USER your_username WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE cyber_asset_db TO your_username;
\q
```

### Step 2: Run Migrations

```bash
# Generate migration (jika ada perubahan model)
alembic revision --autogenerate -m "description"

# Jalankan migration
alembic upgrade head
```

### Step 3: Grant Database Permissions

Setelah migration, berikan permissions ke database user:

```bash
# Login sebagai superuser (postgres)
psql -U postgres -d cyber_asset_db -f scripts/grant_permissions.sql
```

Atau secara manual di pgAdmin/psql:

```sql
-- Ganti 'your_username' dengan username database Anda
GRANT USAGE ON SCHEMA public TO your_username;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_username;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO your_username;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO your_username;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO your_username;
```

### Step 4: Seed Database

Jalankan seeder untuk membuat roles dan users default:

```bash
python scripts/seed_db.py
```

Atau:

```bash
python -m app.db.seeders.run_seeder
```

**Data yang dibuat:**
- **Roles**: 
  - `super_admin` - Super Administrator dengan full access
  - `user` - Regular user dengan limited access
- **Users**:
  - `superadmin` / `admin123` (Super Admin)
  - `user` / `user123` (Regular User)

## Running the Application

### Development Mode

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Aplikasi akan berjalan di: `http://localhost:8000`

**Fitur `--reload`:**
- Auto-reload saat ada perubahan kode
- Cocok untuk development

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Rekomendasi Production:**
- Gunakan reverse proxy (Nginx)
- Setup HTTPS/SSL
- Gunakan process manager (systemd, supervisor, dll)
- Setup monitoring dan logging

## Documentation

### API Documentation

Setelah aplikasi berjalan, akses dokumentasi interaktif:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Additional Documentation

- **[Authorization Guide](docs/AUTHORIZATION.md)**: Panduan lengkap tentang sistem kontrol akses dan permissions

### Troubleshooting

#### Database Connection Error

```bash
# Pastikan PostgreSQL berjalan
# macOS
brew services start postgresql

# Linux
sudo systemctl start postgresql

# Windows
# Start PostgreSQL service dari Services
```

#### Permission Denied Error

Pastikan user database memiliki permissions yang cukup. Jalankan:

```bash
psql -U postgres -d cyber_asset_db -f scripts/grant_permissions.sql
```

#### Migration Error

```bash
# Reset migration (HATI-HATI: akan menghapus data)
alembic downgrade base
alembic upgrade head
```

#### Port Already in Use

```bash
# Gunakan port lain
uvicorn app.main:app --reload --port 8001
```

#### Module Not Found Error

Pastikan virtual environment sudah diaktifkan dan dependencies sudah diinstall:

```bash
source venv/bin/activate  # atau venv\Scripts\activate di Windows
pip install -r requirements.txt
```

### Development

#### Menjalankan Linter

```bash
flake8 app/
```

#### Membuat Migration Baru

```bash
# Setelah mengubah model
alembic revision --autogenerate -m "description"
alembic upgrade head
```

#### Menjalankan Seeder

```bash
python scripts/seed_db.py
```

### Production Deployment

#### Checklist

1. ✅ **Environment Variables**: Pastikan semua environment variables sudah di-set dengan benar
2. ✅ **SECRET_KEY**: Generate secret key yang kuat (minimal 32 karakter)
3. ✅ **Database**: Gunakan database production yang aman dengan backup
4. ✅ **HTTPS**: Gunakan HTTPS untuk production
5. ✅ **CORS**: Konfigurasi CORS sesuai kebutuhan frontend
6. ✅ **Rate Limiting**: Aktifkan rate limiting untuk mencegah abuse
7. ✅ **Monitoring**: Setup monitoring dan logging (Sentry, DataDog, dll)
8. ✅ **Backup**: Setup automated backup untuk database
9. ✅ **Security**: Review security best practices

#### Recommended Production Setup

- **Process Manager**: systemd, supervisor, atau PM2
- **Reverse Proxy**: Nginx atau Traefik
- **SSL/TLS**: Let's Encrypt atau certificate lainnya
- **Monitoring**: Prometheus, Grafana, atau service monitoring lainnya
- **Logging**: Centralized logging (ELK stack, CloudWatch, dll)

