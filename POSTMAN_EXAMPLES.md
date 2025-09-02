# 🧪 Postman Examples for Product API (Add Product + Variations)

## 🚀 Add Product (Grouped-by-Size)

Use this when your admin UI collects size blocks with per-size price and stock. Colors can be names or IDs; `size_id` is optional (size name will be created if missing).

**Endpoint:** `POST {{base_url}}/api/products/`

**Headers:**
- Authorization: Bearer {{jwt_token}}
- Content-Type: application/json

**Body (raw JSON):**
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
    "Small": {
      "size_id": 1,
      "colors": ["Red", "Blue", "Green"],
      "price": 40.00,
      "stock_quantity": 100
    },
    "Medium": {
      "size_id": 2,
      "colors": ["Red", "Black", "White"],
      "price": 45.00,
      "stock_quantity": 150
    },
    "Large": {
      "size_id": 3,
      "colors": ["Blue", "Black", "White"],
      "price": 50.00,
      "stock_quantity": 120
    }
  }
}
```

**Expected Response (201):**
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
  "is_featured": false,
  "product_details": ["100% cotton", "Regular fit"],
  "variations": {
    "Small": {
      "size_id": 1,
      "colors": ["Red", "Blue", "Green"],
      "price": 40.0,
      "stock_quantity": 100
    },
    "Medium": {
      "size_id": 2,
      "colors": ["Red", "Black", "White"],
      "price": 45.0,
      "stock_quantity": 150
    },
    "Large": {
      "size_id": 3,
      "colors": ["Blue", "Black", "White"],
      "price": 50.0,
      "stock_quantity": 120
    }
  }
}
```

Notes:
- Per-size `price_adjustment` is computed internally as `variation.price - product.price`.
- Sizes/colors are created by name if they don’t exist.
- SKU auto-generates if omitted.

---

## ➕ Add Product (Array-Based Variations)

Use this if you prefer explicit size/color relations.

**Endpoint:** `POST {{base_url}}/api/products/`

**Headers:** same as above

**Body (raw JSON):**
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
  "variations": [
    {
      "variation_type": "size",
      "variation": "Small",
      "price_adjustment": 15.00,
      "stock_quantity": 100,
      "size_ids": [1],
      "color_ids": [5, 8, 9],
      "is_default": false
    },
    {
      "variation_type": "size",
      "variation": "Medium",
      "price_adjustment": 20.00,
      "stock_quantity": 150,
      "size_ids": [2],
      "color_ids": [5, 10, 11]
    }
  ]
}
```

---

# 🧪 Postman Examples for Product Variations API

## 🔑 Authentication Setup

**Headers Required:**
```
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json
```

## 📋 Test Collection

### 1. **Get Grouped Variations by Size**

**Request:**
- **Method:** GET
- **URL:** `{{base_url}}/api/product-variations/grouped_by_size/?product_id=1`
- **Headers:** 
  - Authorization: Bearer {{jwt_token}}
- **Body:** None

**Expected Response:**
```json
{
  "product_id": 1,
  "product_name": "Classic T-Shirt",
  "product_sku": "TSH-001",
  "variations": {
    "Small": {
      "size_id": 1,
      "colors": ["Red", "Blue", "Green"],
      "price": 40.00,
      "stock_quantity": 100
    }
  }
}
```

---

### 2. **Add New Size Variant**

**Request:**
- **Method:** POST
- **URL:** `{{base_url}}/api/product-variations/add_size_variant/`
- **Headers:** 
  - Authorization: Bearer {{jwt_token}}
  - Content-Type: application/json
- **Body (raw JSON):**
```json
{
  "product_id": 1,
  "size": "Medium",
  "colors": ["Red", "Black", "White"],
  "price": 45.00,
  "stock_quantity": 150
}
```

**Expected Response:**
```json
{
  "message": "Size variant \"Medium\" added successfully",
  "variation_id": 124,
  "size": "Medium",
  "colors": ["Red", "Black", "White"],
  "price": 45.00,
  "stock_quantity": 150
}
```

---

### 3. **Update Existing Size Variant**

**Request:**
- **Method:** PUT
- **URL:** `{{base_url}}/api/product-variations/update_size_variant/`
- **Headers:** 
  - Authorization: Bearer {{jwt_token}}
  - Content-Type: application/json
- **Body (raw JSON):**
```json
{
  "product_id": 1,
  "size": "Small",
  "colors": ["Red", "Blue", "Green", "Yellow"],
  "price": 42.00,
  "stock_quantity": 120
}
```

**Expected Response:**
```json
{"variations": {
    "Small": {
      "size_id": 1,
      "colors": ["Red", "Blue", "Green"],
      "price": 40.00,
      "stock_quantity": 100
    },
    "Medium": {
      "size_id": 2,
      "colors": ["Red", "Black", "White"],
      "price": 45.00,
      "stock_quantity": 150
    },
    "Large": {
      "size_id": 3,
      "colors": ["Blue", "Black", "White"],
      "price": 50.00,
      "stock_quantity": 120
    }
  }

  "message": "Size variant \"Small\" updated successfully",
  "size": "Small",
  "colors": ["Red", "Blue", "Green", "Yellow"],
  "price": 42.00,
  "stock_quantity": 120
}
```

---

### 4. **Remove Size Variant**

**Request:**
- **Method:** DELETE
- **URL:** `{{base_url}}/api/product-variations/remove_size_variant/`
- **Headers:** 
  - Authorization: Bearer {{jwt_token}}
  - Content-Type: application/json
- **Body (raw JSON):**
```json
{
  "product_id": 1,
  "size": "Medium"
}
```

**Expected Response:**
```json
{
  "message": "Size variant \"Medium\" removed successfully"
}
```

---

## 🔧 Postman Environment Variables

**Set these variables in your Postman environment:**

```
base_url: http://127.0.0.1:8000
jwt_token: YOUR_ACTUAL_JWT_TOKEN
```

**To get a JWT token:**
1. Login to your Django admin or use the authentication endpoint
2. Copy the token from the response
3. Set it as the `jwt_token` environment variable

---

## 📱 Complete Workflow Test

### Endpoints reference (Products)
- POST `/api/products/` (create) — supports grouped or array variations
- GET `/api/products/` (list), GET `/api/products/{id}/` (detail)
- POST `/api/products/{id}/upload-image` (multipart: image, type=main|additional)
- POST `/api/products/{id}/upload-images` (multipart: images[])
- DELETE `/api/products/{id}/remove-image/{image_id}` (main or index)
- DELETE `/api/products/{id}/remove-images` (JSON: { "image_urls": [] })
- GET `/api/products/categories`, GET `/api/products/tags`, GET `/api/products/sizes`, GET `/api/products/colors`
- GET `/api/products/check_sku_uniqueness?sku=XYZ`
- POST `/api/products/regenerate_skus`, POST `/api/products/{id}/regenerate_sku`, POST `/api/products/{id}/regenerate_variation_skus`

### **Step 1: Check Current Variations**
```
GET {{base_url}}/api/product-variations/grouped_by_size/?product_id=1
```

### **Step 2: Add Small Size Variant**
```
POST {{base_url}}/api/product-variations/add_size_variant/
Body: {
  "product_id": 1,
  "size": "Small",
  "colors": ["Red", "Blue", "Green"],
  "price": 40.00,
  "stock_quantity": 100
}
```

### **Step 3: Add Medium Size Variant**
```
POST {{base_url}}/api/product-variations/add_size_variant/
Body: {
  "product_id": 1,
  "size": "Medium",
  "colors": ["Red", "Black", "White"],
  "price": 45.00,
  "stock_quantity": 150
}
```

### **Step 4: Verify Both Variants**
```
GET {{base_url}}/api/product-variations/grouped_by_size/?product_id=1
```

### **Step 5: Update Small Variant**
```
PUT {{base_url}}/api/product-variations/update_size_variant/
Body: {
  "product_id": 1,
  "size": "Small",
  "colors": ["Red", "Blue", "Green", "Yellow"],
  "price": 42.00,
  "stock_quantity": 120
}
```

### **Step 6: Remove Medium Variant**
```
DELETE {{base_url}}/api/product-variations/remove_size_variant/
Body: {
  "product_id": 1,
  "size": "Medium"
}
```

### **Step 7: Final Verification**
```
GET {{base_url}}/api/product-variations/grouped_by_size/?product_id=1
```

---

## 🚨 Error Testing

### **Test Missing Fields**
```
POST {{base_url}}/api/product-variations/add_size_variant/
Body: {
  "product_id": 1,
  "size": "Small"
  // Missing colors, price
}
```

**Expected Error:**
```json
{
  "error": "product_id, size, colors, and price are required"
}
```

### **Test Invalid Product ID**
```
GET {{base_url}}/api/product-variations/grouped_by_size/?product_id=999999
```

**Expected Error:**
```json
{
  "error": "Product not found"
}
```

### **Test Invalid Size for Update**
```
PUT {{base_url}}/api/product-variations/update_size_variant/
Body: {
  "product_id": 1,
  "size": "NonExistentSize",
  "colors": ["Red"],
  "price": 40.00
}
```

**Expected Error:**
```json
{
  "error": "Size \"NonExistentSize\" not found"
}
```

---

## 💡 Tips for Testing

1. **Start with a fresh product** that has no existing variations
2. **Test the complete CRUD cycle** (Create, Read, Update, Delete)
3. **Verify the grouped response** after each operation
4. **Test error conditions** to ensure proper validation
5. **Check Django Admin** to see how variations are stored
6. **Use different product IDs** to test multiple products

---

## 🔍 Debugging

If you encounter issues:

1. **Check Django logs** for detailed error messages
2. **Verify JWT token** is valid and not expired
3. **Ensure product exists** in the database
4. **Check permissions** - user must have admin access
5. **Verify database connection** and migrations

---

*Happy testing! 🚀*
