# Sistem Peminjaman Aset

Dokumentasi lengkap tentang sistem peminjaman aset dengan siklus status yang terstruktur.

## Siklus Status Peminjaman

Sistem menggunakan 6 status utama dengan alur transisi yang terkontrol:

```
PENDING → APPROVED → BORROWED → RETURNED
   ↓         ↓           ↓
REJECTED  REJECTED    OVERDUE → RETURNED
```

### Status dan Deskripsi

1. **PENDING** - Pengajuan peminjaman menunggu persetujuan
2. **APPROVED** - Pengajuan disetujui, siap untuk dipinjam
3. **REJECTED** - Pengajuan ditolak (terminal state)
4. **BORROWED** - Aset sedang digunakan
5. **RETURNED** - Aset telah dikembalikan (terminal state)
6. **OVERDUE** - Melewati batas waktu pengembalian (hanya untuk loans dengan due_date)

### Valid Transitions

| From Status | To Status | Keterangan |
|------------|-----------|------------|
| PENDING | APPROVED | Super Admin approve |
| PENDING | REJECTED | Super Admin reject |
| APPROVED | BORROWED | User mulai menggunakan |
| APPROVED | REJECTED | Super Admin cancel |
| BORROWED | RETURNED | User/Admin return |
| BORROWED | OVERDUE | Auto (jika due_date lewat) |
| OVERDUE | RETURNED | User/Admin return |

## Fitur Utama

### 1. Open-Ended Loans

Sistem mendukung peminjaman dengan durasi terbuka:
- `due_date` dapat dikosongkan (NULL)
- Status tetap `BORROWED` hingga dikembalikan
- Status `OVERDUE` hanya berlaku untuk loans dengan `due_date`

### 2. Status Tracking

Setiap perubahan status dicatat:
- `approved_by`: User yang melakukan approval/rejection
- `status_changed_at`: Waktu perubahan status
- `requested_at`: Waktu pengajuan
- `borrowed_at`: Waktu mulai menggunakan
- `returned_at`: Waktu pengembalian

### 3. Asset Status Management

Status aset otomatis diupdate:
- Saat loan `APPROVED` atau `BORROWED`: asset status = "borrowed"
- Saat loan `REJECTED` atau `RETURNED`: asset status = "available"

## API Endpoints

### 1. Create Loan Request

**POST** `/api/v1/loans`

Membuat pengajuan peminjaman (status: PENDING)

**Request:**
```json
{
  "asset_id": "uuid",
  "due_date": "2024-12-31T23:59:59Z",  // Optional (NULL untuk open-ended)
  "notes": "Optional notes"
}
```

**Response:**
```json
{
  "status": 201,
  "message": "Loan request created successfully",
  "data": {
    "id": "uuid",
    "asset_id": "uuid",
    "user_id": "uuid",
    "loan_status": "pending",
    "requested_at": "2024-01-01T00:00:00Z",
    "due_date": "2024-12-31T23:59:59Z",
    ...
  }
}
```

**Permission:** `CREATE_LOAN` (User & Super Admin)

### 2. List Loans

**GET** `/api/v1/loans?status=pending`

Mendapatkan daftar loans:
- User: hanya loans milik sendiri
- Super Admin: semua loans

**Query Parameters:**
- `status` (optional): Filter by status (pending, approved, borrowed, returned, overdue, rejected)

**Permission:** 
- User: `VIEW_OWN_LOANS`
- Super Admin: `MANAGE_LOANS`

### 3. Get Loan by ID

**GET** `/api/v1/loans/{loan_id}`

Mendapatkan detail loan:
- User: hanya bisa akses loans milik sendiri
- Super Admin: bisa akses semua loans

**Permission:** Owner atau Super Admin

### 4. Approve Loan

**POST** `/api/v1/loans/{loan_id}/approve`

Approve loan request (PENDING → APPROVED)

**Request:**
```json
{
  "notes": "Optional approval notes"
}
```

**Permission:** `MANAGE_LOANS` (Super Admin only)

### 5. Reject Loan

**POST** `/api/v1/loans/{loan_id}/reject`

Reject loan request (PENDING/APPROVED → REJECTED)

**Request:**
```json
{
  "notes": "Optional rejection notes"
}
```

**Permission:** `MANAGE_LOANS` (Super Admin only)

### 6. Start Borrowing

**POST** `/api/v1/loans/{loan_id}/start`

Start borrowing (APPROVED → BORROWED)
- Hanya owner yang bisa start borrowing
- Update asset status ke "borrowed"

**Permission:** Owner only

### 7. Return Loan

**POST** `/api/v1/loans/{loan_id}/return`

Return loan (BORROWED/OVERDUE → RETURNED)
- Owner atau Super Admin bisa return
- Update asset status ke "available"

**Request:**
```json
{
  "notes": "Optional return notes"
}
```

**Permission:** Owner atau Super Admin

### 8. Check Overdue

**POST** `/api/v1/loans/check-overdue`

Check dan update loans yang sudah overdue
- Otomatis update status BORROWED → OVERDUE jika due_date sudah lewat
- Hanya untuk loans dengan due_date (tidak untuk open-ended)

**Permission:** `MANAGE_LOANS` (Super Admin only)

## Business Rules

### 1. Loan Creation
- User tidak bisa membuat loan jika sudah ada loan aktif (PENDING/APPROVED/BORROWED) untuk asset yang sama
- Asset harus dalam status "available" atau "maintenance"
- `due_date` optional (NULL untuk open-ended loan)

### 2. Status Transitions
- Semua transitions harus valid sesuai dengan state machine
- Invalid transition akan raise `LoanStatusTransitionError`

### 3. Overdue Detection
- Status `OVERDUE` hanya untuk loans dengan `due_date`
- Open-ended loans (due_date = NULL) tidak bisa menjadi OVERDUE
- Overdue check harus dijalankan manual atau via scheduled task

### 4. Asset Status
- Asset status otomatis diupdate saat loan status berubah
- Asset dengan status "borrowed" tidak bisa dipinjam lagi

### 5. Data Privacy
- User hanya bisa melihat dan mengelola loans milik sendiri
- Super Admin bisa melihat dan mengelola semua loans

## Audit Logging

Semua aktivitas loan dicatat dalam audit log:
- `create`: Saat membuat loan request
- `approve`: Saat approve loan
- `reject`: Saat reject loan
- `start_borrowing`: Saat mulai menggunakan
- `return`: Saat mengembalikan

Setiap log mencatat:
- User yang melakukan action
- Action yang dilakukan
- Loan ID
- IP address
- Timestamp

## Contoh Alur Peminjaman

### Alur Normal (dengan due_date)

1. User membuat loan request → Status: PENDING
2. Super Admin approve → Status: APPROVED
3. User start borrowing → Status: BORROWED, Asset status: "borrowed"
4. (Optional) Check overdue → Status: OVERDUE (jika due_date lewat)
5. User return → Status: RETURNED, Asset status: "available"

### Alur Open-Ended (tanpa due_date)

1. User membuat loan request (due_date = NULL) → Status: PENDING
2. Super Admin approve → Status: APPROVED
3. User start borrowing → Status: BORROWED
4. User return → Status: RETURNED, Asset status: "available"

### Alur Rejection

1. User membuat loan request → Status: PENDING
2. Super Admin reject → Status: REJECTED, Asset status: "available"

## Error Handling

### Invalid Status Transition

```json
{
  "status": 422,
  "message": "Invalid status transition from approved to pending",
  "data": null
}
```

### Asset Not Available

```json
{
  "status": 422,
  "message": "Asset is not available for borrowing",
  "data": null
}
```

### Duplicate Active Loan

```json
{
  "status": 422,
  "message": "You already have an active loan request for this asset",
  "data": null
}
```

## Best Practices

1. **Selalu check asset availability** sebelum membuat loan request
2. **Gunakan due_date** untuk loans dengan batas waktu
3. **Gunakan NULL due_date** untuk open-ended loans
4. **Jalankan check_overdue** secara berkala (cron job)
5. **Monitor audit logs** untuk tracking semua aktivitas
6. **Validasi permissions** sebelum setiap operasi

