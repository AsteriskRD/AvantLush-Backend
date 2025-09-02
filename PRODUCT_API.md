# Product API Documentation

## Authentication
- Authorization: Bearer <JWT>
- Admin required for create/update/delete

## Base URL
- Local: `http://127.0.0.1:8000`

---

## Create Product (Grouped-by-Size)
- Method: POST
- URL: `/api/products/`
- Content-Type: `application/json` or `multipart/form-data`
- Canonical payload uses grouped-by-size variations. Colors can be names or IDs. `size_id` optional; size name will be created if missing.

Request (JSON)
```json
{
  "name": "Classic Tee",
  "description": "Soft cotton tee",
  "category": 3,
  "price": 25.00,
  "status": "draft",
  "stock_quantity": 100,
  "tags": ["summer", "tops"],
  "product_details": ["100% cotton", "Regular fit"],
  "variations": {
    "Small":   { "size_id": 1, "colors": ["Red","Blue","Green"], "price": 40.00, "stock_quantity": 100 },
    "Medium":  { "size_id": 2, "colors": ["Red","Black","White"], "price": 45.00, "stock_quantity": 150 },
    "Large":   { "size_id": 3, "colors": ["Blue","Black","White"], "price": 50.00, "stock_quantity": 120 }
  }
}
```

Request (multipart form-data)
- Use when sending initial images inline.
- Fields (text): `name`, `description`, `category`, `price`, `status`, `stock_quantity`, `tags` (JSON text), `product_details` (JSON text), `variations` (JSON text as above)
- Files:
  - `main_image_file` (single file) — optional; sets primary image
  - `image_files` (multiple) — optional; additional gallery images

Response (201)
```json
{
  "id": 42,
  "name": "Classic Tee",
  "sku": "CLAS-TE-ABC123",
  "price": 25.0,
  "status": "draft",
  "category": 3,
  "stock_quantity": 100,
  "images": [],
  "main_image": null,
  "all_images": { "main_image": null, "gallery": [] },
  "is_featured": false,
  "product_details": ["100% cotton", "Regular fit"],
  "variations": {
    "Small":  { "size_id": 1, "colors": ["Red","Blue","Green"], "price": 40.0, "stock_quantity": 100 },
    "Medium": { "size_id": 2, "colors": ["Red","Black","White"], "price": 45.0, "stock_quantity": 150 },
    "Large":  { "size_id": 3, "colors": ["Blue","Black","White"], "price": 50.0, "stock_quantity": 120 }
  }
}
```

Notes
- `price_adjustment` is computed internally as `variation.price - product.price`.
- Sizes and colors are created by name if not found.
- SKU auto-generates if omitted.
- `image_files` (multipart) appends to gallery. Set main image via `upload-image`.
- Response image fields:
  - `main_image`: URL or null
  - `images`: array of gallery URLs
  - `all_images`: `{ main_image, gallery }` convenience structure

---

## Product Images

Important
- Always include the trailing slash `/` at the end of these URLs.
- Both hyphen and underscore routes are available for compatibility.

Upload single image (primary or additional)
- Method: POST
- URLs (either works):
  - `/api/products/{id}/upload-image/`
  - `/api/products/{id}/upload_image/`
- Content-Type: `multipart/form-data`
- Fields:
  - `image`: file (required)
  - `type`: `main` | `additional` (default: `main`)

Upload multiple images (gallery)
- Method: POST
- URLs (either works):
  - `/api/products/{id}/upload-images/`
  - `/api/products/{id}/upload_images/`
- Content-Type: `multipart/form-data`
- Files:
  - `images`: file (repeat this key for each file)

Remove one image
- Method: DELETE
- URL: `/api/products/{id}/remove-image/{image_id}/`
- `image_id` = `main` or gallery index (0-based)

Remove multiple images
- Method: DELETE
- URL: `/api/products/{id}/remove-images`
- Body: `{ "image_urls": ["https://...", "https://..."] }`

---

## Product Management

List products
- GET `/api/products/`

Retrieve product
- GET `/api/products/{id}/`

Update product
- PUT/PATCH `/api/products/{id}/`

Delete product
- DELETE `/api/products/{id}/`

Bulk status update
- POST `/api/products/bulk_update_status`
- Body: `{ "product_ids": [1,2,3], "status": "published" }`

Update single product status
- PATCH `/api/products/{id}/update_status`
- Body: `{ "status": "draft" }`

Export CSV
- GET `/api/products/export`

Counts for tabs
- GET `/api/products/tab_counts`

---

## Lookups & SKU Tools

- GET `/api/products/categories`
- GET `/api/products/tags`
- GET `/api/products/sizes`
- GET `/api/products/colors`
- GET `/api/products/check_sku_uniqueness?sku=XYZ`
- POST `/api/products/regenerate_skus`
- POST `/api/products/{id}/regenerate_sku`
- POST `/api/products/{id}/regenerate_variation_skus`

---

## Variation Utilities (Grouped View)

- GET `/api/product-variations/grouped_by_size/?product_id={id}`
- POST `/api/product-variations/add_size_variant/`
  - Body: `{ "product_id": 1, "size": "Small", "colors": ["Red","Blue"], "price": 40.00, "stock_quantity": 100 }`
- PUT `/api/product-variations/update_size_variant/`
  - Body: `{ "product_id": 1, "size": "Small", "colors": ["Red","Blue","Yellow"], "price": 42.00, "stock_quantity": 120 }`
- DELETE `/api/product-variations/remove_size_variant/`
  - Body: `{ "product_id": 1, "size": "Small" }`

---

## Curl Examples

Create product (grouped JSON)
```bash
curl -X POST "{{base_url}}/api/products/" \
  -H "Authorization: Bearer {{jwt_token}}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Classic Tee",
    "description": "Soft cotton tee",
    "category": 3,
    "price": 25.00,
    "status": "draft",
    "stock_quantity": 100,
    "tags": ["summer","tops"],
    "product_details": ["100% cotton","Regular fit"],
    "variations": {
      "Small":  {"size_id":1, "colors":["Red","Blue","Green"], "price":40.00, "stock_quantity":100},
      "Medium": {"size_id":2, "colors":["Red","Black","White"], "price":45.00, "stock_quantity":150}
    }
  }'
```

Upload main image
```bash
curl -X POST "{{base_url}}/api/products/{id}/upload_image/" \
  -H "Authorization: Bearer {{jwt_token}}" \
  -F "image=@/path/to/main.jpg" \
  -F "type=main"
```

Upload multiple images
```bash
curl -X POST "{{base_url}}/api/products/{id}/upload_images/" \
  -H "Authorization: Bearer {{jwt_token}}" \
  -F "images=@/path/to/1.jpg" \
  -F "images=@/path/to/2.jpg"
```

Remove one image (index 0)
```bash
curl -X DELETE "{{base_url}}/api/products/{id}/remove-image/0" \
  -H "Authorization: Bearer {{jwt_token}}"
```
