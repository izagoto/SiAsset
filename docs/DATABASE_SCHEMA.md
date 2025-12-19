# Database Schema

Dokumentasi lengkap schema database untuk Cyber Asset Management System.

---

## Table: roles

```sql
Table roles {
  id uuid [pk, default: `uuid_generate_v4()`]
  name varchar(50) [unique, not null]
  description text [null]
  created_at timestamp with time zone [default: `now()`, not null]
}
```

**Indexes:**
- Primary Key: `id`
- Unique: `name`
- Index: `id`, `name`

**Relationships:**
- One-to-Many: `roles.id` → `users.role_id`

---

## Table: users

```sql
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
```

**Indexes:**
- Primary Key: `id`
- Unique: `username`, `email`
- Index: `username`, `email`, `role_id`

**Relationships:**
- Many-to-One: `users.role_id` → `roles.id`
- One-to-Many: `users.id` → `asset_loans.user_id`
- One-to-Many: `users.id` → `asset_loans.approved_by`
- One-to-Many: `users.id` → `assets.pic_user_id`
- One-to-Many: `users.id` → `audit_logs.user_id`

---

## Table: asset_categories

```sql
Table asset_categories {
  id uuid [pk, default: `uuid_generate_v4()`]
  name varchar(100) [unique, not null]
  description text [null]
  created_at timestamp with time zone [default: `now()`, not null]
}
```

**Indexes:**
- Primary Key: `id`
- Unique: `name`

**Relationships:**
- One-to-Many: `asset_categories.id` → `assets.category_id`

---

## Table: assets

```sql
Table assets {
  id uuid [pk, default: `uuid_generate_v4()`]
  asset_code varchar(100) [unique, not null]
  name varchar(150) [not null]
  serial_number varchar(150) [unique, not null]
  category_id uuid [ref: > asset_categories.id, not null]
  current_status varchar(50) [default: 'active', not null]
  asset_condition varchar(50) [null]
  description text [null]
  pic_user_id uuid [ref: > users.id, null]
  created_at timestamp with time zone [default: `now()`, not null]
  updated_at timestamp with time zone [default: `now()`, on update: `now()`, not null]
}
```

**Indexes:**
- Primary Key: `id`
- Unique: `asset_code`, `serial_number`
- Index: `asset_code`, `serial_number`, `category_id`, `current_status`, `pic_user_id`

**Relationships:**
- Many-to-One: `assets.category_id` → `asset_categories.id`
- Many-to-One: `assets.pic_user_id` → `users.id`
- One-to-Many: `assets.id` → `asset_loans.asset_id`

**Status Values:**
- `active` - Aktif
- `inactive` - Tidak aktif
- `maintenance` - Sedang maintenance
- `decommissioned` - Didekomisioner

---

## Table: asset_loans

```sql
Table asset_loans {
  id uuid [pk, default: `uuid_generate_v4()`]
  asset_id uuid [ref: > assets.id, not null]
  user_id uuid [ref: > users.id, not null]
  requested_at timestamp with time zone [default: `now()`, not null]
  borrowed_at timestamp with time zone [null]
  due_date timestamp with time zone [null]
  returned_at timestamp with time zone [null]
  loan_status varchar(50) [default: 'pending', not null]
  notes text [null]
  approved_by uuid [ref: > users.id, null]
  status_changed_at timestamp with time zone [null]
  created_at timestamp with time zone [default: `now()`, not null]
  updated_at timestamp with time zone [default: `now()`, on update: `now()`, not null]
}
```

**Indexes:**
- Primary Key: `id`
- Index: `asset_id`, `user_id`, `loan_status`

**Relationships:**
- Many-to-One: `asset_loans.asset_id` → `assets.id`
- Many-to-One: `asset_loans.user_id` → `users.id`
- Many-to-One: `asset_loans.approved_by` → `users.id`

**Status Values:**
- `pending` - Menunggu persetujuan
- `approved` - Disetujui
- `rejected` - Ditolak
- `borrowed` - Sedang dipinjam
- `returned` - Sudah dikembalikan
- `overdue` - Melewati batas waktu

**Status Transition Rules:**
- `pending` → `approved` | `rejected`
- `approved` → `borrowed` | `rejected`
- `rejected` → (terminal state)
- `borrowed` → `returned` | `overdue`
- `returned` → (terminal state)
- `overdue` → `returned`

**Notes:**
- `due_date` dapat NULL untuk open-ended loans
- `approved_by` diisi ketika status berubah menjadi `approved` atau `rejected`
- `status_changed_at` diisi setiap kali `loan_status` berubah
- `borrowed_at` diisi ketika status berubah menjadi `borrowed`
- `returned_at` diisi ketika status berubah menjadi `returned`

---

## Table: audit_logs

```sql
Table audit_logs {
  id uuid [pk, default: `uuid_generate_v4()`]
  user_id uuid [ref: > users.id, null]
  action varchar(50) [not null]
  entity varchar(50) [not null]
  entity_id uuid [not null]
  ip_address varchar(45) [null]
  created_at timestamp with time zone [default: `now()`, not null]
}
```

**Indexes:**
- Primary Key: `id`
- Index: `user_id`

**Relationships:**
- Many-to-One: `audit_logs.user_id` → `users.id`

**Entity Types:**
- `user` - User operations
- `asset` - Asset operations
- `loan` - Loan operations
- `category` - Category operations
- `role` - Role operations

**Action Types:**
- `create` - Create operation
- `update` - Update operation
- `delete` - Delete operation
- `activate` - Activate operation
- `deactivate` - Deactivate operation
- `approve` - Approve operation
- `reject` - Reject operation
- `start_borrowing` - Start borrowing
- `return` - Return operation

**Notes:**
- `user_id` dapat NULL untuk system actions
- `ip_address` menggunakan format IPv4 atau IPv6 (max 45 karakter)
- `entity_id` adalah UUID dari entity yang di-audit

---

## Entity Relationship Diagram (ERD)

```
roles
├── id (PK)
└── users (1:N)
    ├── role_id (FK)

users
├── id (PK)
├── role_id (FK → roles.id)
├── asset_loans (1:N)
│   ├── user_id (FK)
│   └── approved_by (FK)
├── assets (1:N)
│   └── pic_user_id (FK)
└── audit_logs (1:N)
    └── user_id (FK)

asset_categories
├── id (PK)
└── assets (1:N)
    └── category_id (FK)

assets
├── id (PK)
├── category_id (FK → asset_categories.id)
├── pic_user_id (FK → users.id)
└── asset_loans (1:N)
    └── asset_id (FK)

asset_loans
├── id (PK)
├── asset_id (FK → assets.id)
├── user_id (FK → users.id)
└── approved_by (FK → users.id)

audit_logs
├── id (PK)
└── user_id (FK → users.id)
```

---

## Database Constraints

### Foreign Key Constraints

1. **users.role_id** → **roles.id**
   - ON DELETE: RESTRICT
   - ON UPDATE: CASCADE

2. **assets.category_id** → **asset_categories.id**
   - ON DELETE: RESTRICT
   - ON UPDATE: CASCADE

3. **assets.pic_user_id** → **users.id**
   - ON DELETE: SET NULL
   - ON UPDATE: CASCADE

4. **asset_loans.asset_id** → **assets.id**
   - ON DELETE: RESTRICT
   - ON UPDATE: CASCADE

5. **asset_loans.user_id** → **users.id**
   - ON DELETE: RESTRICT
   - ON UPDATE: CASCADE

6. **asset_loans.approved_by** → **users.id**
   - ON DELETE: SET NULL
   - ON UPDATE: CASCADE

7. **audit_logs.user_id** → **users.id**
   - ON DELETE: SET NULL
   - ON UPDATE: CASCADE

### Unique Constraints

1. **roles.name** - Unique
2. **users.username** - Unique
3. **users.email** - Unique
4. **asset_categories.name** - Unique
5. **assets.asset_code** - Unique
6. **assets.serial_number** - Unique

### Check Constraints

1. **users.is_active** - Boolean (true/false)
2. **assets.current_status** - Must be one of: 'active', 'inactive', 'maintenance', 'decommissioned'
3. **asset_loans.loan_status** - Must be one of: 'pending', 'approved', 'rejected', 'borrowed', 'returned', 'overdue'

---

## Indexes Summary

### Primary Keys
- `roles.id`
- `users.id`
- `asset_categories.id`
- `assets.id`
- `asset_loans.id`
- `audit_logs.id`

### Unique Indexes
- `roles.name`
- `users.username`
- `users.email`
- `asset_categories.name`
- `assets.asset_code`
- `assets.serial_number`

### Regular Indexes
- `users.role_id`
- `assets.category_id`
- `assets.current_status`
- `assets.pic_user_id`
- `asset_loans.asset_id`
- `asset_loans.user_id`
- `asset_loans.loan_status`
- `audit_logs.user_id`

---

## Data Types

- **UUID**: PostgreSQL UUID type (36 characters)
- **VARCHAR(n)**: Variable-length string with max length n
- **TEXT**: Unlimited length string
- **BOOLEAN**: true/false
- **TIMESTAMP WITH TIME ZONE**: Date and time with timezone information (ISO 8601 format)

---

## Default Values

- **UUID fields**: Auto-generated using `uuid_generate_v4()`
- **created_at**: Current timestamp (`now()`)
- **updated_at**: Current timestamp, auto-updated on row update
- **is_active**: `true`
- **current_status**: `'active'`
- **loan_status**: `'pending'`

---

## Notes

1. **Timezones**: Semua timestamp menggunakan `timestamp with time zone` untuk konsistensi
2. **UUID**: Semua primary key dan foreign key menggunakan UUID untuk distribusi dan keamanan
3. **Soft Delete**: Tidak ada soft delete, menggunakan hard delete dengan audit log
4. **Audit Trail**: Semua operasi penting dicatat di `audit_logs`
5. **Open-ended Loans**: `due_date` dapat NULL untuk peminjaman tanpa batas waktu
6. **Status Management**: Status changes dicatat dengan `status_changed_at` timestamp

---

**Last Updated:** 2025-12-17

