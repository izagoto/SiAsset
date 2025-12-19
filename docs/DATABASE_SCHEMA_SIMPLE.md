# Database Schema (Simple Format)

Schema database untuk Cyber Asset Management System dalam format sederhana.

```sql
Table roles {
  id uuid [pk, default: `uuid_generate_v4()`]
  name varchar(50) [unique, not null]
  description text
  created_at timestamp with time zone [default: `now()`, not null]
}

Table users {
  id uuid [pk, default: `uuid_generate_v4()`]
  username varchar(100) [unique, not null]
  email varchar(255) [unique, not null]
  password_hash varchar(255) [not null]
  role_id uuid [ref: > roles.id, not null]
  is_active boolean [default: true, not null]
  created_at timestamp with time zone [default: `now()`, not null]
  updated_at timestamp with time zone [default: `now()`, on update: `now()`, not null]
}

Table asset_categories {
  id uuid [pk, default: `uuid_generate_v4()`]
  name varchar(100) [unique, not null]
  description text
  created_at timestamp with time zone [default: `now()`, not null]
}

Table assets {
  id uuid [pk, default: `uuid_generate_v4()`]
  asset_code varchar(100) [unique, not null]
  name varchar(150) [not null]
  serial_number varchar(150) [unique, not null]
  category_id uuid [ref: > asset_categories.id, not null]
  current_status varchar(50) [default: 'active', not null]
  asset_condition varchar(50)
  description text
  pic_user_id uuid [ref: > users.id]
  created_at timestamp with time zone [default: `now()`, not null]
  updated_at timestamp with time zone [default: `now()`, on update: `now()`, not null]
}

Table asset_loans {
  id uuid [pk, default: `uuid_generate_v4()`]
  asset_id uuid [ref: > assets.id, not null]
  user_id uuid [ref: > users.id, not null]
  requested_at timestamp with time zone [default: `now()`, not null]
  borrowed_at timestamp with time zone
  due_date timestamp with time zone
  returned_at timestamp with time zone
  loan_status varchar(50) [default: 'pending', not null]
  notes text
  approved_by uuid [ref: > users.id]
  status_changed_at timestamp with time zone
  created_at timestamp with time zone [default: `now()`, not null]
  updated_at timestamp with time zone [default: `now()`, on update: `now()`, not null]
}

Table audit_logs {
  id uuid [pk, default: `uuid_generate_v4()`]
  user_id uuid [ref: > users.id]
  action varchar(50) [not null]
  entity varchar(50) [not null]
  entity_id uuid [not null]
  ip_address varchar(45)
  created_at timestamp with time zone [default: `now()`, not null]
}

Ref: users.role_id > roles.id
Ref: assets.category_id > asset_categories.id
Ref: assets.pic_user_id > users.id
Ref: asset_loans.asset_id > assets.id
Ref: asset_loans.user_id > users.id
Ref: asset_loans.approved_by > users.id
Ref: audit_logs.user_id > users.id
```

---

## Perubahan dari Schema Sebelumnya

### Table: roles
- ✅ `name` sekarang `varchar(50)` dengan constraint unique
- ✅ `created_at` menggunakan `timestamp with time zone`

### Table: users
- ✅ `username` sekarang `varchar(100)` dengan constraint unique
- ✅ `email` sekarang `varchar(255)` dengan constraint unique
- ✅ `password_hash` sekarang `varchar(255)` (bukan text)
- ✅ `created_at` dan `updated_at` menggunakan `timestamp with time zone`
- ✅ `updated_at` memiliki auto-update on update

### Table: asset_categories
- ✅ `name` sekarang `varchar(100)` dengan constraint unique
- ✅ `created_at` menggunakan `timestamp with time zone`

### Table: assets
- ✅ `asset_code` sekarang `varchar(100)` dengan constraint unique
- ✅ `name` sekarang `varchar(150)`
- ✅ `serial_number` sekarang `varchar(150)` dengan constraint unique
- ✅ `current_status` sekarang `varchar(50)` dengan default 'active'
- ✅ `asset_condition` sekarang `varchar(50)` (nullable)
- ✅ `created_at` dan `updated_at` menggunakan `timestamp with time zone`
- ✅ `updated_at` memiliki auto-update on update

### Table: asset_loans
- ✅ **Ditambahkan:** `requested_at` timestamp with time zone (NOT NULL)
- ✅ `borrowed_at`, `due_date`, `returned_at` menggunakan `timestamp with time zone` (nullable)
- ✅ `loan_status` sekarang `varchar(50)` dengan default 'pending' (NOT NULL)
- ✅ **Ditambahkan:** `approved_by` uuid (nullable, FK ke users.id)
- ✅ **Ditambahkan:** `status_changed_at` timestamp with time zone (nullable)
- ✅ **Ditambahkan:** `created_at` timestamp with time zone (NOT NULL)
- ✅ **Ditambahkan:** `updated_at` timestamp with time zone dengan auto-update (NOT NULL)

### Table: audit_logs
- ✅ `user_id` sekarang nullable (bisa NULL)
- ✅ `action` sekarang `varchar(50)` (NOT NULL)
- ✅ `entity` sekarang `varchar(50)` (NOT NULL)
- ✅ `entity_id` sekarang NOT NULL
- ✅ `ip_address` sekarang `varchar(45)` (nullable)
- ✅ `created_at` menggunakan `timestamp with time zone`

---

## Field yang Ditambahkan

### asset_loans
1. **requested_at** - Waktu request dibuat (NOT NULL, default: now())
2. **approved_by** - User yang approve/reject loan (nullable, FK ke users.id)
3. **status_changed_at** - Waktu terakhir status berubah (nullable)
4. **created_at** - Waktu record dibuat (NOT NULL, default: now())
5. **updated_at** - Waktu record terakhir diupdate (NOT NULL, auto-update)

---

## Constraints dan Indexes

### Unique Constraints
- `roles.name`
- `users.username`
- `users.email`
- `asset_categories.name`
- `assets.asset_code`
- `assets.serial_number`

### Foreign Key Constraints
- `users.role_id` → `roles.id`
- `assets.category_id` → `asset_categories.id`
- `assets.pic_user_id` → `users.id`
- `asset_loans.asset_id` → `assets.id`
- `asset_loans.user_id` → `users.id`
- `asset_loans.approved_by` → `users.id`
- `audit_logs.user_id` → `users.id`

### Default Values
- `users.is_active` = `true`
- `assets.current_status` = `'active'`
- `asset_loans.loan_status` = `'pending'`
- Semua `created_at` = `now()`
- Semua `updated_at` = `now()` (auto-update on update)

---

**Last Updated:** 2025-12-17

