# Sistem Kontrol Akses (Authorization)

Aplikasi menggunakan **Role-Based Access Control (RBAC)** dengan dua tingkat utama akses.

## Roles dan Permissions

### 1. Super Admin (Full Access)
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

### 2. User (Limited Access)
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

## Data Privacy

**Data peminjaman bersifat privat:**
- Hanya pemilik data peminjaman dan Super Admin yang dapat mengaksesnya
- User hanya dapat melihat dan mengelola peminjaman miliknya sendiri

## Cara Menggunakan Permission System

### 1. Import Dependencies

```python
from app.api.deps import (
    get_current_active_user,
    get_super_admin,
    require_permission_dependency,
)
from app.core.permissions import Permission
from app.models.user import User
```

### 2. Super Admin Only Endpoint

```python
@router.post("/users", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_super_admin),  # Hanya Super Admin
    db: Session = Depends(get_db),
):
    # Hanya Super Admin yang bisa create user
    ...
```

### 3. Permission-Based Endpoint

```python
@router.get("/assets", response_model=List[AssetResponse])
def list_assets(
    current_user: User = Depends(
        require_permission_dependency(Permission.VIEW_ASSETS)
    ),
    db: Session = Depends(get_db),
):
    # User dengan VIEW_ASSETS permission bisa akses
    ...
```

### 4. Owner or Admin Check (untuk Data Privat)

```python
from app.core.permissions import require_owner_or_admin

@router.get("/loans/{loan_id}", response_model=LoanResponse)
def get_loan(
    loan_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    loan = db.query(Borrow).filter(Borrow.id == loan_id).first()
    if not loan:
        raise NotFoundException("Loan")
    
    # Cek apakah user adalah owner atau Super Admin
    require_owner_or_admin(current_user, str(loan.user_id))
    
    return loan
```

### 5. Audit Logging

```python
from app.utils.audit import log_asset_action, get_client_ip
from fastapi import Request

@router.post("/assets", response_model=AssetResponse)
def create_asset(
    asset_data: AssetCreate,
    request: Request,
    current_user: User = Depends(
        require_permission_dependency(Permission.MANAGE_ASSETS)
    ),
    db: Session = Depends(get_db),
):
    # Create asset
    asset = create_asset_service(db, asset_data)
    
    # Log audit
    log_asset_action(
        db=db,
        user=current_user,
        action="create",
        asset_id=asset.id,
        ip_address=get_client_ip(request),
    )
    
    return asset
```

## Permission List

| Permission | Super Admin | User | Description |
|------------|-------------|------|-------------|
| `MANAGE_USERS` | ✅ | ❌ | Create, update, delete users |
| `VIEW_USERS` | ✅ | ❌ | View users list |
| `MANAGE_ROLES` | ✅ | ❌ | Manage roles |
| `VIEW_ROLES` | ✅ | ❌ | View roles |
| `MANAGE_ASSETS` | ✅ | ❌ | Create, update, delete assets |
| `VIEW_ASSETS` | ✅ | ✅ | View assets list |
| `MANAGE_CATEGORIES` | ✅ | ❌ | Manage categories |
| `VIEW_CATEGORIES` | ✅ | ✅ | View categories |
| `MANAGE_LOANS` | ✅ | ❌ | View all loans, manage any loan |
| `VIEW_OWN_LOANS` | ✅ | ✅ | View own loans only |
| `CREATE_LOAN` | ✅ | ✅ | Create new loan |
| `RETURN_LOAN` | ✅ | ✅ | Return loan |
| `VIEW_AUDIT_LOGS` | ✅ | ❌ | View audit logs |

## Best Practices

1. **Selalu gunakan `get_current_active_user`** untuk memastikan user aktif
2. **Gunakan `get_super_admin`** untuk endpoint yang hanya boleh diakses Super Admin
3. **Gunakan `require_owner_or_admin`** untuk data privat (seperti loans)
4. **Selalu log aktivitas penting** menggunakan audit logging utility
5. **Jangan hardcode role name**, gunakan permission system

## Error Handling

Sistem akan mengembalikan error dengan format:

```json
{
    "status": 403,
    "message": "You don't have permission to manage_users",
    "data": null
}
```

Error code: `PERMISSION_DENIED`

