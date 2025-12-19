# API Contract Documentation

Dokumentasi lengkap kontrak API untuk Cyber Asset Management System.

**Base URL:** `http://localhost:8000/api/v1`

**API Version:** 1.0.0

---

## Table of Contents

1. [Authentication](#authentication)
2. [Users](#users)
3. [Assets](#assets)
4. [Loans](#loans)
5. [Error Responses](#error-responses)
6. [Data Models](#data-models)

---

## Authentication

### POST /auth/login

Login untuk mendapatkan access token dan refresh token.

**Request:**
```json
{
  "email": "string (EmailStr)",
  "password": "string"
}
```

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "Login successful",
  "data": {
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "bearer"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials
- `403 Forbidden` - User account is inactive
- `422 Unprocessable Entity` - Validation error

---

### POST /auth/refresh

Refresh access token menggunakan refresh token.

**Request:**
```json
{
  "refresh_token": "string"
}
```

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "Token refreshed successfully",
  "data": {
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "bearer"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid refresh token
- `403 Forbidden` - User account is inactive

---

### GET /auth/me

Mendapatkan profil user yang sedang login.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "User profile retrieved successfully",
  "data": {
    "id": "uuid",
    "role_id": "uuid",
    "username": "string",
    "email": "string (EmailStr)",
    "is_active": "boolean",
    "created_at": "datetime (ISO 8601)",
    "updated_at": "datetime (ISO 8601)"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - User not found

---

### POST /auth/logout

Logout user (opsional, token tetap valid sampai expired).

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "Logout successful",
  "data": null
}
```

---

## Users

**Base Path:** `/users`

**Required Permission:** `MANAGE_USERS` (Super Admin only, kecuali GET /users/{user_id} dan PUT /users/{user_id} untuk own profile)

---

### GET /users

Mendapatkan daftar semua users.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (integer, default: 0, min: 0) - Number of records to skip
- `limit` (integer, default: 100, min: 1, max: 100) - Number of records to return
- `is_active` (boolean, optional) - Filter by active status
- `role_id` (uuid, optional) - Filter by role ID
- `search` (string, optional) - Search by username or email

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "Users retrieved successfully",
  "data": {
    "items": [
      {
        "id": "uuid",
        "role_id": "uuid",
        "username": "string",
        "email": "string",
        "is_active": "boolean",
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ],
    "total": "integer",
    "skip": "integer",
    "limit": "integer"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Permission denied
- `404 Not Found` - No users found

---

### POST /users

Membuat user baru.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "username": "string (min: 3, max: 100)",
  "email": "string (EmailStr)",
  "password": "string (min: 6)",
  "role_id": "uuid"
}
```

**Response (201 Created):**
```json
{
  "status": 201,
  "message": "User created successfully",
  "data": {
    "id": "uuid",
    "role_id": "uuid",
    "username": "string",
    "email": "string",
    "is_active": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Permission denied
- `404 Not Found` - Role not found
- `422 Unprocessable Entity` - Validation error (username/email already exists)

---

### GET /users/{user_id}

Mendapatkan detail user by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (uuid, required) - User ID

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "User retrieved successfully",
  "data": {
    "id": "uuid",
    "role_id": "uuid",
    "username": "string",
    "email": "string",
    "is_active": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Can only access own data (for regular users)
- `404 Not Found` - User not found

---

### PUT /users/{user_id}

Update user. Super Admin dapat update semua user, User hanya dapat update sendiri.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Path Parameters:**
- `user_id` (uuid, required) - User ID

**Request:**
```json
{
  "username": "string (optional, min: 3, max: 100)",
  "email": "string (optional, EmailStr)",
  "password": "string (optional, min: 6)",
  "role_id": "uuid (optional)",
  "is_active": "boolean (optional)"
}
```

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "User updated successfully",
  "data": {
    "id": "uuid",
    "role_id": "uuid",
    "username": "string",
    "email": "string",
    "is_active": "boolean",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Permission denied
- `404 Not Found` - User or Role not found
- `422 Unprocessable Entity` - Validation error

---

### DELETE /users/{user_id}

Menghapus user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (uuid, required) - User ID

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "User deleted successfully",
  "data": null
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Permission denied
- `404 Not Found` - User not found

---

### POST /users/{user_id}/activate

Mengaktifkan user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (uuid, required) - User ID

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "User activated successfully",
  "data": {
    "id": "uuid",
    "role_id": "uuid",
    "username": "string",
    "email": "string",
    "is_active": true,
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

---

### POST /users/{user_id}/deactivate

Menonaktifkan user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `user_id` (uuid, required) - User ID

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "User deactivated successfully",
  "data": {
    "id": "uuid",
    "role_id": "uuid",
    "username": "string",
    "email": "string",
    "is_active": false,
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

---

## Assets

**Base Path:** `/assets`

**Required Permission:** 
- `VIEW_ASSETS` - Untuk melihat assets (semua authenticated users)
- `MANAGE_ASSETS` - Untuk create/update/delete assets (Super Admin only)

---

### GET /assets/list_assets

Mendapatkan daftar semua assets.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip` (integer, default: 0, min: 0) - Number of records to skip
- `limit` (integer, default: 100, min: 1, max: 100) - Number of records to return
- `status` (string, optional) - Filter by asset status
- `category_id` (uuid, optional) - Filter by category ID
- `search` (string, optional) - Search by name, code, or serial number

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "Assets retrieved successfully",
  "data": {
    "items": [
      {
        "id": "uuid",
        "asset_code": "string",
        "name": "string",
        "serial_number": "string",
        "category_id": "uuid",
        "current_status": "string",
        "asset_condition": "string (nullable)",
        "description": "string (nullable)",
        "pic_user_id": "uuid (nullable)",
        "created_at": "datetime",
        "updated_at": "datetime"
      }
    ],
    "total": "integer",
    "skip": "integer",
    "limit": "integer"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Permission denied
- `404 Not Found` - No assets found

---

### POST /assets/create_asset

Membuat asset baru.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "asset_code": "string (required, min: 1, max: 100, unique)",
  "name": "string (required, min: 1, max: 150)",
  "serial_number": "string (required, min: 1, max: 150, unique)",
  "category_id": "uuid (required)",
  "current_status": "string (optional, default: 'active', max: 50)",
  "asset_condition": "string (optional, max: 50)",
  "description": "string (optional)",
  "pic_user_id": "uuid (optional)"
}
```

**Response (201 Created):**
```json
{
  "status": 201,
  "message": "Asset created successfully",
  "data": {
    "id": "uuid",
    "asset_code": "string",
    "name": "string",
    "serial_number": "string",
    "category_id": "uuid",
    "current_status": "string",
    "asset_condition": "string",
    "description": "string",
    "pic_user_id": "uuid",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Permission denied
- `404 Not Found` - Asset Category not found
- `422 Unprocessable Entity` - Validation error (asset_code/serial_number already exists)

---

### GET /assets/{asset_id}/get_asset

Mendapatkan detail asset by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `asset_id` (uuid, required) - Asset ID

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "Asset retrieved successfully",
  "data": {
    "id": "uuid",
    "asset_code": "string",
    "name": "string",
    "serial_number": "string",
    "category_id": "uuid",
    "current_status": "string",
    "asset_condition": "string",
    "description": "string",
    "pic_user_id": "uuid",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Permission denied
- `404 Not Found` - Asset not found

---

### PUT /assets/{asset_id}/update_asset

Update asset.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Path Parameters:**
- `asset_id` (uuid, required) - Asset ID

**Request:**
```json
{
  "name": "string (optional, min: 1, max: 150)",
  "serial_number": "string (optional, min: 1, max: 150)",
  "category_id": "uuid (optional)",
  "current_status": "string (optional, max: 50)",
  "asset_condition": "string (optional, max: 50)",
  "description": "string (optional)",
  "pic_user_id": "uuid (optional)"
}
```

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "Asset updated successfully",
  "data": {
    "id": "uuid",
    "asset_code": "string",
    "name": "string",
    "serial_number": "string",
    "category_id": "uuid",
    "current_status": "string",
    "asset_condition": "string",
    "description": "string",
    "pic_user_id": "uuid",
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Permission denied
- `404 Not Found` - Asset or Category not found
- `422 Unprocessable Entity` - Validation error

---

### DELETE /assets/{asset_id}/delete_asset

Menghapus asset.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `asset_id` (uuid, required) - Asset ID

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "Asset deleted successfully",
  "data": null
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Permission denied
- `404 Not Found` - Asset not found

---

## Loans

**Base Path:** `/loans`

**Required Permission:**
- `VIEW_OWN_LOANS` - Untuk melihat loan sendiri (User)
- `MANAGE_LOANS` - Untuk melihat semua loans dan approve/reject (Super Admin)
- `CREATE_LOAN` - Untuk membuat loan request (semua authenticated users)
- `RETURN_LOAN` - Untuk return asset (Owner atau Super Admin)

---

### GET /loans

Mendapatkan daftar loans. User melihat loan sendiri, Super Admin melihat semua loans.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status_filter` (string, optional) - Filter by loan status

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "Loans retrieved successfully",
  "data": [
    {
      "id": "uuid",
      "asset_id": "uuid",
      "user_id": "uuid",
      "requested_at": "datetime",
      "borrowed_at": "datetime (nullable)",
      "due_date": "datetime (nullable)",
      "returned_at": "datetime (nullable)",
      "loan_status": "string",
      "notes": "string (nullable)",
      "approved_by": "uuid (nullable)",
      "status_changed_at": "datetime (nullable)",
      "created_at": "datetime",
      "updated_at": "datetime"
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `404 Not Found` - No loans found

---

### POST /loans

Membuat loan request baru (status: PENDING).

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Request:**
```json
{
  "asset_id": "uuid (required)",
  "due_date": "datetime (optional, ISO 8601, nullable for open-ended loan)",
  "notes": "string (optional)"
}
```

**Response (201 Created):**
```json
{
  "status": 201,
  "message": "Loan request created successfully",
  "data": {
    "id": "uuid",
    "asset_id": "uuid",
    "user_id": "uuid",
    "requested_at": "datetime",
    "borrowed_at": null,
    "due_date": "datetime (nullable)",
    "returned_at": null,
    "loan_status": "pending",
    "notes": "string",
    "approved_by": null,
    "status_changed_at": null,
    "created_at": "datetime",
    "updated_at": "datetime"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Permission denied
- `404 Not Found` - Asset not found
- `422 Unprocessable Entity` - Validation error (asset not available, invalid status transition)

---

### GET /loans/{loan_id}

Mendapatkan detail loan by ID.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `loan_id` (uuid, required) - Loan ID

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "Loan retrieved successfully",
  "data": {
    "id": "uuid",
    "asset_id": "uuid",
    "user_id": "uuid",
    "requested_at": "datetime",
    "borrowed_at": "datetime",
    "due_date": "datetime",
    "returned_at": "datetime",
    "loan_status": "string",
    "notes": "string",
    "approved_by": "uuid",
    "status_changed_at": "datetime",
    "created_at": "datetime",
    "updated_at": "datetime",
    "asset": {
      "id": "uuid",
      "asset_code": "string",
      "name": "string",
      "serial_number": "string"
    }
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Can only access own loans (for regular users)
- `404 Not Found` - Loan not found

---

### POST /loans/{loan_id}/approve

Approve loan request (PENDING → APPROVED). Hanya Super Admin.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Path Parameters:**
- `loan_id` (uuid, required) - Loan ID

**Request:**
```json
{
  "notes": "string (optional)"
}
```

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "Loan approved successfully",
  "data": {
    "id": "uuid",
    "loan_status": "approved",
    "approved_by": "uuid",
    "status_changed_at": "datetime"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Permission denied
- `404 Not Found` - Loan not found
- `422 Unprocessable Entity` - Invalid status transition

---

### POST /loans/{loan_id}/reject

Reject loan request (PENDING → REJECTED). Hanya Super Admin.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Path Parameters:**
- `loan_id` (uuid, required) - Loan ID

**Request:**
```json
{
  "notes": "string (optional)"
}
```

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "Loan rejected successfully",
  "data": {
    "id": "uuid",
    "loan_status": "rejected",
    "approved_by": "uuid",
    "status_changed_at": "datetime"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Permission denied
- `404 Not Found` - Loan not found
- `422 Unprocessable Entity` - Invalid status transition

---

### POST /loans/{loan_id}/start

Start borrowing (APPROVED → BORROWED). Hanya owner loan.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `loan_id` (uuid, required) - Loan ID

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "Borrowing started successfully",
  "data": {
    "id": "uuid",
    "loan_status": "borrowed",
    "borrowed_at": "datetime",
    "status_changed_at": "datetime"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Can only start own loans
- `404 Not Found` - Loan not found
- `422 Unprocessable Entity` - Invalid status transition

---

### POST /loans/{loan_id}/return

Return asset (BORROWED/OVERDUE → RETURNED). Owner atau Super Admin.

**Headers:**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**Path Parameters:**
- `loan_id` (uuid, required) - Loan ID

**Request:**
```json
{
  "notes": "string (optional)"
}
```

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "Asset returned successfully",
  "data": {
    "id": "uuid",
    "loan_status": "returned",
    "returned_at": "datetime",
    "status_changed_at": "datetime"
  }
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Permission denied
- `404 Not Found` - Loan not found
- `422 Unprocessable Entity` - Invalid status transition

---

### POST /loans/check-overdue

Check dan update overdue loans. Hanya Super Admin.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "status": 200,
  "message": "Found {count} overdue loans",
  "data": [
    {
      "id": "uuid",
      "loan_status": "overdue",
      "status_changed_at": "datetime"
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Permission denied

---

## Error Responses

Semua error mengikuti format konsisten:

### Standard Error Format
```json
{
  "status": "integer (HTTP status code)",
  "message": "string (error message)",
  "data": null,
  "errors": {
    "field_name": "error message"
  }
}
```

### HTTP Status Codes

- `200 OK` - Request berhasil
- `201 Created` - Resource berhasil dibuat
- `400 Bad Request` - Request tidak valid
- `401 Unauthorized` - Tidak terautentikasi atau token invalid
- `403 Forbidden` - Tidak memiliki permission
- `404 Not Found` - Resource tidak ditemukan
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

### Common Error Messages

#### 401 Unauthorized
```json
{
  "status": 401,
  "message": "Invalid credentials",
  "data": null
}
```

#### 403 Forbidden
```json
{
  "status": 403,
  "message": "You don't have permission to perform this action",
  "data": null
}
```

#### 404 Not Found
```json
{
  "status": 404,
  "message": "{Resource} not found",
  "data": null
}
```

#### 422 Validation Error
```json
{
  "status": 422,
  "message": "Validation error",
  "data": null,
  "errors": {
    "field_name": "error message"
  }
}
```

#### 500 Internal Server Error
```json
{
  "status": 500,
  "message": "Internal server error",
  "data": null
}
```

---

## Data Models

### User Model
```json
{
  "id": "uuid",
  "role_id": "uuid",
  "username": "string (min: 3, max: 100)",
  "email": "string (EmailStr)",
  "is_active": "boolean",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

### Asset Model
```json
{
  "id": "uuid",
  "asset_code": "string (unique, min: 1, max: 100)",
  "name": "string (min: 1, max: 150)",
  "serial_number": "string (unique, min: 1, max: 150)",
  "category_id": "uuid",
  "current_status": "string (max: 50)",
  "asset_condition": "string (nullable, max: 50)",
  "description": "string (nullable)",
  "pic_user_id": "uuid (nullable)",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

### Loan Model
```json
{
  "id": "uuid",
  "asset_id": "uuid",
  "user_id": "uuid",
  "requested_at": "datetime (ISO 8601)",
  "borrowed_at": "datetime (nullable, ISO 8601)",
  "due_date": "datetime (nullable, ISO 8601)",
  "returned_at": "datetime (nullable, ISO 8601)",
  "loan_status": "string",
  "notes": "string (nullable)",
  "approved_by": "uuid (nullable)",
  "status_changed_at": "datetime (nullable, ISO 8601)",
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

### Loan Status Values
- `pending` - Menunggu persetujuan
- `approved` - Disetujui
- `rejected` - Ditolak
- `borrowed` - Sedang dipinjam
- `returned` - Sudah dikembalikan
- `overdue` - Melewati batas waktu

### Asset Status Values
- `active` - Aktif
- `inactive` - Tidak aktif
- `maintenance` - Sedang maintenance
- `decommissioned` - Didekomisioner

---

## Authentication

Semua endpoint (kecuali `/auth/login`) memerlukan authentication menggunakan Bearer Token.

**Header Format:**
```
Authorization: Bearer <access_token>
```

**Token Expiration:**
- Access Token: 30 menit (default)
- Refresh Token: 7 hari (default)

**Token Refresh:**
Jika access token expired, gunakan refresh token untuk mendapatkan token baru melalui endpoint `/auth/refresh`.

---

## Rate Limiting

Saat ini tidak ada rate limiting yang diterapkan.

---

## Pagination

Endpoint yang mengembalikan list data menggunakan query parameters:
- `skip` - Number of records to skip (default: 0)
- `limit` - Number of records to return (default: 100, max: 100)

Response format:
```json
{
  "items": [...],
  "total": "integer",
  "skip": "integer",
  "limit": "integer"
}
```

---

## Date/Time Format

Semua datetime menggunakan format ISO 8601 dengan timezone:
```
2025-12-17T18:30:00+07:00
```

---

## UUID Format

Semua UUID menggunakan format standar:
```
550e8400-e29b-41d4-a716-446655440000
```

---

## Versioning

API menggunakan versioning di path:
- Current version: `/api/v1`

---

## Changelog

### Version 1.0.0 (2025-12-17)
- Initial API release
- Authentication endpoints
- User management endpoints
- Asset management endpoints
- Loan management endpoints

---

**Last Updated:** 2025-12-17

