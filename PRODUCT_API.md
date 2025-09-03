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
- Legend: [required], [optional], [auto]
```json
{
  "name": "Classic Tee",                 // [required]
  "description": "Soft cotton tee",       // [optional]
  "category": 3,                          // [required] category ID
  "price": 25.00,                         // [optional]
  "status": "draft",                      // [optional] default: draft
  "stock_quantity": 100,                  // [optional]
  "is_featured": false,                   // [optional]
  "is_physical_product": true,            // [optional]
  "weight": 0.35,                          // [optional]
  "height": 2.0,                           // [optional]
  "length": 30.0,                          // [optional]
  "width": 25.0,                           // [optional]
  "discount_type": "percentage",          // [optional] percentage|fixed
  "discount_value": 10.00,                // [optional]
  "vat_amount": 0.00,                     // [optional]
  "barcode": "1234567890123",            // [optional]
  "sku": "",                               // [auto] leave empty or omit to auto-generate
  "tags": ["summer", "tops"],            // [optional] array of names or IDs
  "product_details": ["100% cotton", "Regular fit"], // [required] at least one detail
  "variations": {                          // [recommended] grouped-by-size map
    "Small":   { "size_id": 1, "colors": ["Red","Blue"], "price": 40.00, "stock_quantity": 100 },
    "Medium":  { "size_id": 2, "colors": ["Black","White"], "price": 45.00, "stock_quantity": 150 },
    "Large":   { "size_id": 3, "colors": ["Blue","Black"], "price": 50.00, "stock_quantity": 120 }
  }
}
```

Request (multipart form-data)
- Use when sending initial images inline.
- Fields (text): same as JSON above, but `tags`, `product_details`, and `variations` must be JSON-encoded strings (product_details is [required])
- Files:
  - `main_image_file` (single file) — optional; sets primary image
  - `image_files` (multiple) — optional; additional gallery images

One-call create with images (multipart example)
```bash
curl -X POST "{{base_url}}/api/products/" \
  -H "Authorization: Bearer {{jwt_token}}" \
  -H "Content-Type: multipart/form-data" \
  -F "name=Classic Tee" \
  -F "description=Soft cotton tee" \
  -F "category=3" \
  -F "price=25.00" \
  -F "status=draft" \
  -F "stock_quantity=100" \
  -F "is_featured=false" \
  -F "is_physical_product=true" \
  -F "weight=0.35" -F "height=2.0" -F "length=30.0" -F "width=25.0" \
  -F "discount_type=percentage" -F "discount_value=10.00" -F "vat_amount=0.00" \
  -F "barcode=1234567890123" -F "sku=" \
  -F "tags=[\"summer\",\"tops\"]" \
  -F "product_details=[\"100% cotton\",\"Regular fit\"]" \
  -F "variations={\"Small\":{\"size_id\":1,\"colors\":[\"Red\",\"Blue\"],\"price\":40.0,\"stock_quantity\":100},\"Medium\":{\"size_id\":2,\"colors\":[\"Black\",\"White\"],\"price\":45.0,\"stock_quantity\":150},\"Large\":{\"size_id\":3,\"colors\":[\"Blue\",\"Black\"],\"price\":50.0,\"stock_quantity\":120}}" \
  -F "main_image_file=@/path/to/main.jpg" \
  -F "image_files=@/path/to/1.jpg" \
  -F "image_files=@/path/to/2.jpg"
```

Response (201)
```json
{
  "id": 42,
  "name": "Classic Tee",
  "slug": "classic-tee",
  "description": "Soft cotton tee",
  "product_details": ["100% cotton", "Regular fit"],
  "category": 3,
  "category_name": "Tops",
  "tags_display": ["summer", "tops"],
  "status": "draft",
  "status_display": "Draft",
  "main_image": "https://.../main.jpg",
  "images": ["https://.../1.jpg", "https://.../2.jpg"],
  "all_images": { "main_image": "https://.../main.jpg", "gallery": ["https://.../1.jpg","https://.../2.jpg"] },
  "is_featured": false,
  "is_liked": false,
  "variations": {
    "Small":  { "size_id": 1, "colors": ["Red","Blue"], "price": 40.0, "stock_quantity": 100 },
    "Medium": { "size_id": 2, "colors": ["Black","White"], "price": 45.0, "stock_quantity": 150 },
    "Large":  { "size_id": 3, "colors": ["Blue","Black"], "price": 50.0, "stock_quantity": 120 }
  },
  "price": 25.0,
  "discount_type": "percentage",
  "discount_value": 10.0,
  "vat_amount": 0.0,
  "sku": "AUTO-CLAS-00123",
  "barcode": "1234567890123",
  "stock_quantity": 100,
  "is_physical_product": true,
  "weight": 0.35,
  "height": 2.0,
  "length": 30.0,
  "width": 25.0,
  "created_at": "2025-09-02T13:45:21Z",
  "added_date_formatted": "Sep 2, 2025",
  "variants_count": 3
}
```

Notes
- `price_adjustment` is computed internally as `variation.price - product.price`.
- Sizes and colors are created by name if not found.
- SKU auto-generates if omitted or left blank.
- Slug auto-generates server-side and is included in the response; the frontend can link using `/products/{slug}` or keep the `id`.
- `image_files` (multipart) appends to gallery. Set main image via `main_image_file` in creation or `upload-image` endpoint later.
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
