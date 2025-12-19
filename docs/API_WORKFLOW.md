# API Workflow Guide

Dokumentasi ini menjelaskan urutan penggunaan endpoint dari awal sampai akhir untuk **Super Admin** dan **User**.

---

## 📋 Daftar Isi
1. [Login (Semua User)](#1-login-semua-user)
2. [Workflow Super Admin](#2-workflow-super-admin)
3. [Workflow User](#3-workflow-user)
4. [Endpoint Reference](#endpoint-reference)

---

## 1. Login (Semua User)

### Langkah 1: Login
**Endpoint:** `POST /api/v1/auth/login`

**Request:**
```json
{
  "email": "superadmin@example.com",
  "password": "admin123"
}
```

**Response:**
```json
{
  "status": 200,
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

**Simpan `access_token` untuk digunakan di request berikutnya.**

---

## 2. Workflow Super Admin

Super Admin memiliki akses penuh terhadap semua fitur sistem.

### 2.1. Manajemen User

#### Langkah 1: Melihat Daftar User
**Endpoint:** `GET /api/v1/users?skip=0&limit=100`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response:**
```json
{
  "status": 200,
  "message": "Users retrieved successfully",
  "data": {
    "items": [
      {
    "id": "00000000-0000-0000-0000-000000000010",
    "role_id": "00000000-0000-0000-0000-000000000001",
    "username": "superadmin",
    "email": "superadmin@example.com",
    "is_active": true,
        "created_at": "2025-12-17T10:00:00+07:00",
        "updated_at": "2025-12-17T10:00:00+07:00"
      }
    ],
    "total": 2,
    "skip": 0,
    "limit": 100
  }
}
```

#### Langkah 2: Membuat User Baru
**Endpoint:** `POST /api/v1/users`

**Request:**
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123",
  "role_id": "00000000-0000-0000-0000-000000000002"
}
```

**Response:**
```json
{
  "status": 201,
  "message": "User created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "role_id": "00000000-0000-0000-0000-000000000002",
    "username": "newuser",
    "email": "newuser@example.com",
    "is_active": true,
    "created_at": "2025-12-17T18:30:00+07:00",
    "updated_at": "2025-12-17T18:30:00+07:00"
  }
}
```

#### Langkah 3: Update User (Opsional)
**Endpoint:** `PUT /api/v1/users/{user_id}`

**Request:**
```json
{
  "username": "updateduser",
  "is_active": true
}
```

#### Langkah 4: Deactivate/Activate User (Opsional)
**Endpoint:** `POST /api/v1/users/{user_id}/deactivate` atau `/activate`

---

### 2.2. Manajemen Asset

#### Langkah 1: Melihat Daftar Asset
**Endpoint:** `GET /api/v1/assets/list_assets?skip=0&limit=100`

**Response:**
```json
{
  "status": 200,
  "message": "Assets retrieved successfully",
  "data": {
    "items": [...],
    "total": 10,
    "skip": 0,
    "limit": 100
  }
}
```

#### Langkah 2: Membuat Asset Baru
**Endpoint:** `POST /api/v1/assets/create_asset`

**Request:**
```json
{
  "asset_code": "AST-001",
  "name": "Laptop Dell XPS 15",
  "serial_number": "SN-DELL-2024-001",
  "category_id": "00000000-0000-0000-0000-000000000001",
  "current_status": "active",
  "asset_condition": "excellent",
  "description": "Laptop untuk development",
  "pic_user_id": "00000000-0000-0000-0000-000000000010"
}
```

**Response:**
```json
{
  "status": 201,
  "message": "Asset created successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "asset_code": "AST-001",
    "name": "Laptop Dell XPS 15",
    "serial_number": "SN-DELL-2024-001",
    "category_id": "00000000-0000-0000-0000-000000000001",
    "current_status": "active",
    "asset_condition": "excellent",
    "description": "Laptop untuk development",
    "pic_user_id": "00000000-0000-0000-0000-000000000010",
    "created_at": "2025-12-17T18:30:00+07:00",
    "updated_at": "2025-12-17T18:30:00+07:00"
  }
}
```

#### Langkah 3: Update Asset (Opsional)
**Endpoint:** `PUT /api/v1/assets/{asset_id}/update_asset`

**Request:**
```json
{
  "current_status": "maintenance",
  "asset_condition": "good"
}
```

#### Langkah 4: Hapus Asset (Opsional)
**Endpoint:** `DELETE /api/v1/assets/{asset_id}/delete_asset`

---

### 2.3. Manajemen Loan (Peminjaman)

#### Langkah 1: Melihat Semua Loan
**Endpoint:** `GET /api/v1/loans`

**Response:**
```json
{
  "status": 200,
  "message": "Loans retrieved successfully",
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "asset_id": "660e8400-e29b-41d4-a716-446655440000",
      "user_id": "00000000-0000-0000-0000-000000000011",
      "loan_status": "pending",
      "requested_at": "2025-12-17T18:00:00+07:00",
      "due_date": "2025-12-24T18:00:00+07:00",
      "notes": "Untuk keperluan project"
    }
  ]
}
```

#### Langkah 2: Approve Loan Request
**Endpoint:** `POST /api/v1/loans/{loan_id}/approve`

**Request:**
```json
{
  "notes": "Disetujui untuk peminjaman"
}
```

**Response:**
```json
{
  "status": 200,
  "message": "Loan approved successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "loan_status": "approved",
    "approved_by": "00000000-0000-0000-0000-000000000010",
    "status_changed_at": "2025-12-17T18:30:00+07:00"
  }
}
```

#### Langkah 3: Reject Loan Request (Opsional)
**Endpoint:** `POST /api/v1/loans/{loan_id}/reject`

**Request:**
```json
{
  "notes": "Asset sedang digunakan"
}
```

#### Langkah 4: Check Overdue Loans
**Endpoint:** `POST /api/v1/loans/check-overdue`

**Response:**
```json
{
  "status": 200,
  "message": "Found 2 overdue loans",
  "data": [...]
}
```

---

### 2.4. Melihat Profile Sendiri

#### Langkah: Get Current User Profile
**Endpoint:** `GET /api/v1/auth/me`

**Response:**
```json
{
  "status": 200,
  "message": "User profile retrieved successfully",
  "data": {
    "id": "00000000-0000-0000-0000-000000000010",
    "role_id": "00000000-0000-0000-0000-000000000001",
    "username": "superadmin",
    "email": "superadmin@example.com",
    "is_active": true,
    "created_at": "2025-12-17T10:00:00+07:00",
    "updated_at": "2025-12-17T10:00:00+07:00"
  }
}
```

---

## 3. Workflow User

User memiliki akses terbatas, hanya dapat melihat asset, membuat loan request, dan melihat loan sendiri.

### 3.1. Melihat Daftar Asset

#### Langkah 1: List Assets
**Endpoint:** `GET /api/v1/assets/list_assets?skip=0&limit=100`

**Response:**
```json
{
  "status": 200,
  "message": "Assets retrieved successfully",
  "data": {
    "items": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "asset_code": "AST-001",
        "name": "Laptop Dell XPS 15",
        "serial_number": "SN-DELL-2024-001",
        "current_status": "active",
        "asset_condition": "excellent"
      }
    ],
    "total": 10,
    "skip": 0,
    "limit": 100
  }
}
```

#### Langkah 2: Get Asset Detail
**Endpoint:** `GET /api/v1/assets/{asset_id}/get_asset`

---

### 3.2. Manajemen Loan (Peminjaman)

#### Langkah 1: Membuat Loan Request
**Endpoint:** `POST /api/v1/loans`

**Request:**
```json
{
  "asset_id": "550e8400-e29b-41d4-a716-446655440000",
  "due_date": "2025-12-24T18:00:00+07:00",
  "notes": "Untuk keperluan project development"
}
```

**Note:** Untuk open-ended loan, `due_date` bisa dikosongkan (null).

**Response:**
```json
{
  "status": 201,
  "message": "Loan request created successfully",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440000",
    "asset_id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "00000000-0000-0000-0000-000000000011",
    "loan_status": "pending",
    "requested_at": "2025-12-17T18:00:00+07:00",
    "due_date": "2025-12-24T18:00:00+07:00",
    "notes": "Untuk keperluan project development"
  }
}
```

#### Langkah 2: Melihat Loan Sendiri
**Endpoint:** `GET /api/v1/loans`

**Response:**
```json
{
  "status": 200,
  "message": "Loans retrieved successfully",
  "data": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "asset_id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "00000000-0000-0000-0000-000000000011",
      "loan_status": "approved",
      "requested_at": "2025-12-17T18:00:00+07:00",
      "due_date": "2025-12-24T18:00:00+07:00"
    }
  ]
}
```

#### Langkah 3: Get Loan Detail
**Endpoint:** `GET /api/v1/loans/{loan_id}`

#### Langkah 4: Start Borrowing (Setelah Approved)
**Endpoint:** `POST /api/v1/loans/{loan_id}/start`

**Response:**
```json
{
  "status": 200,
  "message": "Borrowing started successfully",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440000",
    "loan_status": "borrowed",
    "borrowed_at": "2025-12-17T19:00:00+07:00",
    "status_changed_at": "2025-12-17T19:00:00+07:00"
  }
}
```

#### Langkah 5: Return Asset
**Endpoint:** `POST /api/v1/loans/{loan_id}/return`

**Request (Opsional):**
```json
{
  "notes": "Asset dikembalikan dalam kondisi baik"
}
```

**Response:**
```json
{
  "status": 200,
  "message": "Asset returned successfully",
  "data": {
    "id": "770e8400-e29b-41d4-a716-446655440000",
    "loan_status": "returned",
    "returned_at": "2025-12-20T18:00:00+07:00",
    "status_changed_at": "2025-12-20T18:00:00+07:00"
  }
}
```

---

### 3.3. Melihat Profile Sendiri

#### Langkah: Get Current User Profile
**Endpoint:** `GET /api/v1/auth/me`

---

## 4. Refresh Token (Opsional)

Jika access token expired, gunakan refresh token untuk mendapatkan token baru.

**Endpoint:** `POST /api/v1/auth/refresh`

**Request:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response:**
```json
{
  "status": 200,
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

---

## 5. Logout (Opsional)

**Endpoint:** `POST /api/v1/auth/logout`

**Response:**
```json
{
  "status": 200,
  "message": "Logout successful",
  "data": null
}
```

---

## Endpoint Reference

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user profile
- `POST /api/v1/auth/logout` - Logout

### Users (Super Admin Only)
- `GET /api/v1/users` - List users
- `POST /api/v1/users` - Create user
- `GET /api/v1/users/{user_id}` - Get user by ID
- `PUT /api/v1/users/{user_id}` - Update user
- `DELETE /api/v1/users/{user_id}` - Delete user
- `POST /api/v1/users/{user_id}/activate` - Activate user
- `POST /api/v1/users/{user_id}/deactivate` - Deactivate user

### Assets
- `GET /api/v1/assets/list_assets` - List assets (All users)
- `POST /api/v1/assets/create_asset` - Create asset (Super Admin only)
- `GET /api/v1/assets/{asset_id}/get_asset` - Get asset by ID (All users)
- `PUT /api/v1/assets/{asset_id}/update_asset` - Update asset (Super Admin only)
- `DELETE /api/v1/assets/{asset_id}/delete_asset` - Delete asset (Super Admin only)

### Loans
- `GET /api/v1/loans` - List loans (Own loans for User, All loans for Super Admin)
- `POST /api/v1/loans` - Create loan request (All users)
- `GET /api/v1/loans/{loan_id}` - Get loan by ID
- `POST /api/v1/loans/{loan_id}/approve` - Approve loan (Super Admin only)
- `POST /api/v1/loans/{loan_id}/reject` - Reject loan (Super Admin only)
- `POST /api/v1/loans/{loan_id}/start` - Start borrowing (Owner only)
- `POST /api/v1/loans/{loan_id}/return` - Return asset (Owner or Super Admin)
- `POST /api/v1/loans/check-overdue` - Check overdue loans (Super Admin only)

---

## Flow Diagram

### Super Admin Flow
```
Login → Get Profile → Manage Users → Manage Assets → Manage Loans → Logout
```

### User Flow
```
Login → Get Profile → View Assets → Create Loan Request → Wait Approval → 
Start Borrowing → Use Asset → Return Asset → Logout
```

---

## Catatan Penting

1. **Authentication**: Semua endpoint (kecuali login) memerlukan `Authorization: Bearer <access_token>` di header
2. **Permissions**: 
   - Super Admin memiliki akses penuh
   - User hanya dapat melihat asset, membuat loan request, dan mengelola loan sendiri
3. **Loan Status Flow**:
   - `PENDING` → `APPROVED` / `REJECTED` (by Super Admin)
   - `APPROVED` → `BORROWED` (by Owner)
   - `BORROWED` → `RETURNED` (by Owner or Super Admin)
   - `BORROWED` → `OVERDUE` (automatic jika melewati due_date)
4. **Error Handling**: Semua error mengembalikan format konsisten dengan `status`, `message`, dan `data`
5. **Audit Log**: Semua aktivitas penting (create, update, delete) dicatat di audit log

---

## Contoh Script Lengkap

### Super Admin Workflow
```bash
# 1. Login
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "superadmin@example.com", "password": "admin123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])")

# 2. Get Profile
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"

# 3. List Users
curl -X GET "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer $TOKEN"

# 4. Create Asset
curl -X POST "http://localhost:8000/api/v1/assets/create_asset" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "asset_code": "AST-001",
    "name": "Laptop Dell XPS 15",
    "serial_number": "SN-DELL-2024-001",
    "category_id": "00000000-0000-0000-0000-000000000001"
  }'

# 5. List Loans
curl -X GET "http://localhost:8000/api/v1/loans" \
  -H "Authorization: Bearer $TOKEN"

# 6. Approve Loan
curl -X POST "http://localhost:8000/api/v1/loans/{loan_id}/approve" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"notes": "Disetujui"}'
```

### User Workflow
```bash
# 1. Login
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "user123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['access_token'])")

# 2. List Assets
curl -X GET "http://localhost:8000/api/v1/assets/list_assets" \
  -H "Authorization: Bearer $TOKEN"

# 3. Create Loan Request
curl -X POST "http://localhost:8000/api/v1/loans" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "asset_id": "550e8400-e29b-41d4-a716-446655440000",
    "due_date": "2025-12-24T18:00:00+07:00",
    "notes": "Untuk project"
  }'

# 4. List Own Loans
curl -X GET "http://localhost:8000/api/v1/loans" \
  -H "Authorization: Bearer $TOKEN"

# 5. Start Borrowing (after approved)
curl -X POST "http://localhost:8000/api/v1/loans/{loan_id}/start" \
  -H "Authorization: Bearer $TOKEN"

# 6. Return Asset
curl -X POST "http://localhost:8000/api/v1/loans/{loan_id}/return" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"notes": "Dikembalikan dalam kondisi baik"}'
```

---

**Selamat menggunakan API! 🚀**
