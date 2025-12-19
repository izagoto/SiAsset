# API Request Examples

## Create Asset

### Endpoint
```
POST /api/v1/assets/create_asset
```

### Headers
```
Content-Type: application/json
Authorization: Bearer <your_access_token>
```

### Request Body (Minimal - Required Fields Only)
```json
{
  "asset_code": "AST-001",
  "name": "Laptop Dell XPS 15",
  "serial_number": "SN-DELL-2024-001",
  "category_id": "00000000-0000-0000-0000-000000000001"
}
```

### Request Body (Complete - All Fields)
```json
{
  "asset_code": "AST-001",
  "name": "Laptop Dell XPS 15",
  "serial_number": "SN-DELL-2024-001",
  "category_id": "00000000-0000-0000-0000-000000000001",
  "current_status": "active",
  "asset_condition": "excellent",
  "description": "Laptop untuk development dengan spesifikasi tinggi",
  "pic_user_id": "00000000-0000-0000-0000-000000000010"
}
```

### Field Descriptions
- **asset_code** (required): Kode unik aset, harus unik, max 100 karakter
- **name** (required): Nama aset, max 150 karakter
- **serial_number** (required): Nomor seri aset, harus unik, max 150 karakter
- **category_id** (required): UUID kategori aset
- **current_status** (optional): Status aset, default "active". Nilai yang valid: "active", "inactive", "maintenance", "decommissioned"
- **asset_condition** (optional): Kondisi aset, max 50 karakter. Contoh: "excellent", "good", "fair", "poor"
- **description** (optional): Deskripsi aset
- **pic_user_id** (optional): UUID user yang bertanggung jawab atas aset

### Example using cURL
```bash
curl -X POST "http://localhost:8000/api/v1/assets/create_asset" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "asset_code": "AST-001",
    "name": "Laptop Dell XPS 15",
    "serial_number": "SN-DELL-2024-001",
    "category_id": "00000000-0000-0000-0000-000000000001",
    "current_status": "active",
    "asset_condition": "excellent",
    "description": "Laptop untuk development dengan spesifikasi tinggi",
    "pic_user_id": "00000000-0000-0000-0000-000000000010"
  }'
```

### Success Response (201 Created)
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
    "description": "Laptop untuk development dengan spesifikasi tinggi",
    "pic_user_id": "00000000-0000-0000-0000-000000000010",
    "created_at": "2025-12-17T18:30:00.000000+07:00",
    "updated_at": "2025-12-17T18:30:00.000000+07:00"
  }
}
```

### Error Responses

#### 401 Unauthorized
```json
{
  "status": 401,
  "message": "Invalid credentials",
  "data": null
}
```

#### 403 Forbidden (No Permission)
```json
{
  "status": 403,
  "message": "You don't have permission to manage_assets",
  "data": null
}
```

#### 422 Validation Error
```json
{
  "status": 422,
  "message": "Asset code already exists",
  "data": null
}
```

### Notes
- Endpoint ini memerlukan permission `MANAGE_ASSETS` (hanya Super Admin)
- `asset_code` dan `serial_number` harus unik
- `category_id` harus valid UUID dari tabel `asset_categories`
- `pic_user_id` harus valid UUID dari tabel `users` (jika diisi)
- Semua aktivitas akan dicatat di audit log

