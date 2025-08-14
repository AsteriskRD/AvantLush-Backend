# AvantLush API Documentation

# Base URL
Production: 'https://avantlush-backend-2s6k.onrender.com/api/'
Development: 'http://localhost:8000/api/'
Authentication
Most endpoints require authentication using JWT tokens.
Authentication Header:

Authorization: Bearer <jwt_token>

Global Error Format
All API errors follow this consistent format:

{
    "status": "error",
    "message": "Error description",
    "errors": {} // Validation errors if applicable
}

HTTP Status Codes
200: Successful operation
201: Resource created successfully
400: Bad request / Validation error
401: Unauthorized / Invalid credentials
403: Forbidden / Insufficient permissions
404: Resource not found
409: Conflict (e.g., duplicate entry)
500: Server error
Rate Limiting
Anonymous users: 5 requests per minute
Authenticated endpoints use default throttling rates
Pagination
Default pagination settings:

Page size: 12 items
Query parameters:
page: Page number
page_size: Items per page (optional)
Authentication Endpoints
Register User
URL: /register/
Method: POST
Auth Required: No
Description: Registers a new user
Request Body:
{
  "email": "user@example.com",
  "password": "securepassword",
  "location": "Country"
}


Success Response (201):
{
  "user": {
    "email": "user@example.com",
    "location": "Country",
    "uuid": "a1b2c3d4-e5f6-7890-abcd-1234567890ab"
  },
  "token": "jwt-token"
}

Error Response (400):
{
  "status": "error",
  "message": "Validation error",
  "errors": {
    "email": ["User with this email address already exists."]
  }
}

Login
URL: /auth/login/
Method: POST
Auth Required: No
Description: Authenticates a user and returns a token
Request Body:
{
  "email": "user@example.com",
  "password": "password"
}

Success Response (200):
{
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "user": {
    "email": "user@example.com",
    "location": "Country",
    "uuid": "a1b2c3d4-e5f6-7890-abcd-1234567890ab"
  }
}

Error Response (401):
{
  "status": "error",
  "message": "Invalid credentials",
  "errors": {
    "password": ["Invalid password for this account."]
  }
}


Google Login
URL: /auth/google/
Method: POST
Auth Required: No
Description: Authenticates a user using Google OAuth
Request Body:
{
  "token": "GOOGLE_ACCESS_TOKEN",
  "email": "user@example.com",
  "location": "Nigeria"
}

Success Response (200):
{
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "user": {
    "email": "user@example.com",
    "location": "Nigeria"
  }
}

Error Response (400):
{
  "status": "error",
  "message": "Invalid token"
}

Verify Email
URL: /verify-email/<token>/<uidb64>/
Method: GET
Auth Required: No
Description: Verifies a user's email address
Success Response (200):
{
  "success": true,
  "message": "Email verified successfully",
  "token": "jwt-token"
}


Error Response (400):
{
  "success": false,
  "message": "Invalid verification link"
}

Resend Verification Email
URL: /resend-verification/
Method: POST
Auth Required: No
Description: Resends the verification email
Request Body:
{
  "email": "user@example.com"
}


Success Response (200):
{
  "success": true,
  "message": "Verification email resent successfully"
}

Error Response (404):
{
  "success": false,
  "message": "No unverified user found with this email"
}

Forgot Password
URL: /forgot-password/
Method: POST
Auth Required: No
Description: Sends a password reset link to the user's email
Request Body:
{
  "email": "user@example.com"
}

Success Response (200):
{
  "success": true,
  "message": "Password reset link sent to your email"
}


Error Response (404):
{
  "success": false,
  "message": "No user found with this email address"
}

Reset Password
URL: /reset-password/<uidb64>/<token>/
Method: POST
Auth Required: No
Description: Resets the user's password
Request Body:
{
  "password": "newpassword"
}


Success Response (200):
{
  "success": true,
  "message": "Password reset successful"
}




Error Response (400):
{
  "success": false,
  "message": "Invalid reset link"
}



Validate Token
URL: /auth/validate-token/
Method: POST
Auth Required: Yes
Description: Validates if the current token is still valid
Success Response (200):
{
  "valid": true
}

Error Response (401):
{
  "valid": false,
  "message": "Token is invalid or expired"
}

User Profile Endpoints
Get User Profile
URL: /profile/
Method: GET
Auth Required: Yes
Description: Retrieves the authenticated user's profile
Success Response (200):
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone_number": "+2348012345678",
  "country_code": "+234",
  "formatted_phone_number": "+234 801 234 5678",
  "photo": null,
  "photo_url": null,
  "updated_at": "2023-01-01T12:00:00Z",
  "available_country_codes": {
    "+234": "Nigeria",
    "+1": "United States",
    "+44": "United Kingdom"
  }
}


Error Response (401):
{
  "detail": "Authentication credentials were not provided."
}



Update User Profile
URL: /profile/<id>/
Method: PUT/PATCH
Auth Required: Yes
Description: Updates the authenticated user's profile
Request Body:
{
  "full_name": "John Doe",
  "phone_number": "8012345678",
  "country_code": "+234"
}



Success Response (200):
{
  "id": 1,
  "email": "user@example.com",
  "full_name": "John Doe",
  "phone_number": "+2348012345678",
  "country_code": "+234",
  "formatted_phone_number": "+234 801 234 5678",
  "photo_url": null,
  "updated_at": "2023-01-01T12:00:00Z"
}


Error Response (400):
{
  "status": "error",
  "message": "Validation error",
  "errors": {
    "phone_number": ["Invalid phone number format"]
  }
}


Address Endpoints
List Addresses
URL: /addresses/
Method: GET
Auth Required: Yes
Description: Retrieves all addresses for the authenticated user
Success Response (200):
[
  {
    "id": 1,
    "full_name": "John Doe",
    "email": "user@example.com",
    "phone_number": "+2348012345678",
    "street_address": "123 Main St",
    "city": "Lagos",
    "state": "Lagos",
    "country": "Nigeria",
    "zip_code": "100001",
    "is_default": true,
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z"
  }
]



Create Address
URL: /addresses/
Method: POST
Auth Required: Yes
Description: Creates a new address for the authenticated user
Request Body:
{
  "full_name": "John Doe",
  "email": "user@example.com",
  "phone_number": "+2348012345678",
  "street_address": "123 Main St",
  "city": "Lagos",
  "state": "Lagos",
  "country": "Nigeria",
  "zip_code": "100001",
  "is_default": true
}



Success Response (201):
{
  "id": 1,
  "full_name": "John Doe",
  "email": "user@example.com",
  "phone_number": "+2348012345678",
  "street_address": "123 Main St",
  "city": "Lagos",
  "state": "Lagos",
  "country": "Nigeria",
  "zip_code": "100001",
  "is_default": true,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}



Error Response (400):
{
  "status": "error",
  "message": "Validation error",
  "errors": {
    "street_address": ["This field is required."]
  }
}


Update Address
URL: /addresses/<id>/
Method: PUT/PATCH
Auth Required: Yes
Description: Updates an existing address
Request Body:
{
  "street_address": "456 New St",
  "is_default": true
}


Success Response (200):
{
  "id": 1,
  "full_name": "John Doe",
  "email": "user@example.com",
  "phone_number": "+2348012345678",
  "street_address": "456 New St",
  "city": "Lagos",
  "state": "Lagos",
  "country": "Nigeria",
  "zip_code": "100001",
  "is_default": true,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}

______________________________________
Delete Address
URL: /addresses/<id>/
Method: DELETE
Auth Required: Yes
Description: Deletes an address
Success Response (204): No content
Error Response (404):
{
  "status": "error",
  "message": "Address not found"
}


Product Endpoints
List Products
URL: /products/
Method: GET
Auth Required: No
Description: Retrieves a list of products with optional filtering
Query Parameters:
search: Search term
category: Filter by category ID
min_price: Minimum price
max_price: Maximum price
in_stock: true/false
ordering: price, -price, name, -name, created_at, -created_at
page: Page number (default: 1)
page_size: Items per page (default: 12)
tab: all, published, low_stock, draft
Success Response (200):
{
  "count": 100,
  "next": "http://api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Product Name",
      "slug": "product-name",
      "description": "Product description",
      "price": "99.99",
      "category": 1,
      "category_name": "Category Name",
      "images": ["url1", "url2"],
      "main_image": "main_image_url",
      "stock_quantity": 50,
      "is_featured": true,
      "is_physical_product": true,
      "sku": "PRD001",
      "status": "active",
      "rating": "4.50",
      "num_ratings": 10,
      "is_liked": false,
      "product_details": ["Feature 1", "Feature 2"],
      "created_at": "2024-01-20T10:30:00Z",
      "updated_at": "2024-01-20T10:30:00Z"
    }
  ]
}


Get Product
URL: /products/<id>/
Method: GET
Auth Required: No
Description: Retrieves a specific product by ID
Success Response (200):
{
  "id": 1,
  "name": "Product Name",
  "slug": "product-name",
  "description": "Product description",
  "price": "99.99",
  "category": 1,
  "category_name": "Category Name",
  "images": ["url1", "url2"],
  "main_image": "main_image_url",
  "stock_quantity": 50,
  "is_featured": true,
  "is_physical_product": true,
  "sku": "PRD001",
  "status": "active",
  "rating": "4.50",
  "num_ratings": 10,
  "is_liked": false,
  "product_details": ["Feature 1", "Feature 2"],
  "created_at": "2024-01-20T10:30:00Z",
  "updated_at": "2024-01-20T10:30:00Z"
}


Context
— none fetched
Product Endpoints (continued)
Get Product (continued)
Error Response (404):
{
  "status": "error",
  "message": "Product not found"
}




Create Product (Admin only)
URL: /products/
Method: POST
Auth Required: Yes (Admin)
Description: Creates a new product
Request Body:
{
  "name": "New Product",
  "description": "Product description",
  "product_details": ["Feature 1", "Feature 2"],
  "category": 1,
  "tags": [1, 2],
  "price": "99.99",
  "base_price": "99.99",
  "stock_quantity": 50,
  "sku": "PRD002",
  "status": "draft",
  "is_featured": false,
  "is_physical_product": true,
  "weight": "1.5",
  "height": "10",
  "length": "20",
  "width": "15"
}



Success Response (201):
{
  "id": 2,
  "name": "New Product",
  "description": "Product description",
  "product_details": ["Feature 1", "Feature 2"],
  "category": 1,
  "category_name": "Category Name",
  "tags": [1, 2],
  "status": "draft",
  "status_display": "Draft",
  "main_image": null,
  "images": [],
  "base_price": "99.99",
  "discount_type": null,
  "discount_percentage": null,
  "vat_amount": null,
  "sku": "PRD002",
  "barcode": null,
  "stock_quantity": 50,
  "variations": [],
  "is_featured": false,
  "is_physical_product": true,
  "weight": "1.5",
  "height": "10",
  "length": "20",
  "width": "15",
  "created_at": "2024-01-20T10:30:00Z",
  "variants_count": 0
}


Error Response (400):
{
  "status": "error",
  "message": "Validation error",
  "errors": {
    "sku": ["Product with this SKU already exists."]
  }
}




Update Product (Admin only)
URL: /products/<id>/
Method: PUT/PATCH
Auth Required: Yes (Admin)
Description: Updates an existing product
Request Body:
{
  "name": "Updated Product Name",
  "price": "89.99",
  "status": "published"
}




Success Response (200):
{
  "id": 1,
  "name": "Updated Product Name",
  "description": "Product description",
  "product_details": ["Feature 1", "Feature 2"],
  "category": 1,
  "category_name": "Category Name",
  "tags": [1, 2],
  "status": "published",
  "status_display": "Published",
  "main_image": "main_image_url",
  "images": ["url1", "url2"],
  "base_price": "89.99",
  "discount_type": null,
  "discount_percentage": null,
  "vat_amount": null,
  "sku": "PRD001",
  "barcode": null,
  "stock_quantity": 50,
  "variations": [],
  "is_featured": true,
  "is_physical_product": true,
  "weight": "1.5",
  "height": "10",
  "length": "20",
  "width": "15",
  "created_at": "2024-01-20T10:30:00Z",
  "variants_count": 0
}




Delete Product (Admin only)
URL: /products/<id>/
Method: DELETE
Auth Required: Yes (Admin)
Description: Deletes a product
Success Response (204): No content
Upload Product Image (Admin only)
URL: /products/<id>/upload-image/
Method: POST
Auth Required: Yes (Admin)
Description: Uploads an image for a product
Request Body:
Form data with 'image' file



Success Response (200):
{
  "success": true,
  "image_url": "https://cloudinary.com/image_url.jpg"
}

            


Error Response (400):
{
  "status": "error",
  "message": "Failed to upload image"
}



Remove Product Image (Admin only)
URL: /products/<id>/remove-image/<image_id>/
Method: DELETE
Auth Required: Yes (Admin)
Description: Removes an image from a product
Success Response (200):
{
  "success": true,
  "message": "Image removed successfully"
}



Export Products (Admin only)
URL: /products/export/
Method: GET
Auth Required: Yes (Admin)
Description: Exports products data in CSV format
Success Response (200): CSV file download
Bulk Update Product Status (Admin only)
URL: /products/bulk-update-status/
Method: POST
Auth Required: Yes (Admin)
Description: Updates the status of multiple products
Request Body:
{
  "product_ids": [1, 2, 3],
  "status": "published"
}



Success Response (200):
{
  "success": true,
  "message": "3 products updated successfully"
}


Get Product Tags (Admin only)
URL: /products/tags/
Method: GET
Auth Required: Yes (Admin)
Description: Retrieves all product tags
Success Response (200):
[
  {
    "id": 1,
    "name": "New",
    "slug": "new"
  },
  {
    "id": 2,
    "name": "Featured",
    "slug": "featured"
  }
]


Get Product Categories
URL: /products/categories/
Method: GET
Auth Required: No
Description: Retrieves all product categories
Success Response (200):
[
  {
    "id": 1,
    "name": "Electronics",
    "slug": "electronics",
    "parent": null
  },
  {
    "id": 2,
    "name": "Smartphones",
    "slug": "smartphones",
    "parent": 1
  }
]



Search Products
URL: /products/search/
Method: GET
Auth Required: No
Description: Searches for products
Query Parameters:
q: Search query
category: Filter by category ID
Success Response (200):
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "Product Name",
      "slug": "product-name",
      "description": "Product description",
      "price": "99.99",
      "main_image": "main_image_url",
      "category_name": "Category Name"
    }
  ]
}

            TO BE EDITED

Record Product View
URL: /products/record-view/
Method: POST
Auth Required: Yes
Description: Records a product view for analytics
Request Body:
{
  "product_id": 1
}

Copy


Success Response (201):
{
  "success": true
}

Copy


Get Product Recommendations
URL: /products/<product_id>/recommendations/
Method: GET
Auth Required: No
Description: Gets product recommendations based on a product
Success Response (200):
[
  {
    "id": 2,
    "name": "Related Product",
    "price": "89.99",
    "main_image": "image_url",
    "slug": "related-product",
    "rating": "4.2",
    "stock_quantity": 30
  }
]

Copy


Get Product Recommendations by Type
URL: /products/<product_id>/recommendations/<rec_type>/
Method: GET
Auth Required: No
Description: Gets product recommendations by type (similar, complementary)
Success Response (200):
[
  {
    "id": 2,
    "name": "Related Product",
    "price": "89.99",
    "main_image": "image_url",
    "slug": "related-product",
    "rating": "4.2",
    "stock_quantity": 30
  }
]

Copy


Product Reviews Endpoints
List Product Reviews
URL: /products/<product_id>/reviews/
Method: GET
Auth Required: No
Description: Retrieves reviews for a specific product
Success Response (200):
[
  {
    "id": 1,
    "product": 1,
    "user_email": "user@example.com",
    "rating": 5,
    "content": "This product is amazing!",
    "images": [],
    "tags": [
      {
        "id": 1,
        "name": "High Quality",
        "slug": "high-quality",
        "count": 10
      }
    ],
    "helpful_count": 5,
    "is_helpful": false,
    "variant": null,
    "is_verified_purchase": true,
    "created_at": "2024-01-27T16:00:00Z"
  }
]

Copy


Create Product Review
URL: /products/<product_id>/reviews/
Method: POST
Auth Required: Yes
Description: Creates a review for a product
Request Body:
{
  "rating": 5,
  "content": "This product is amazing!",
  "tag_ids": [1, 2]
}

Copy


Success Response (201):
{
  "id": 1,
  "product": 1,
  "user_email": "user@example.com",
  "rating": 5,
  "content": "This product is amazing!",
  "images": [],
  "tags": [
    {
      "id": 1,
      "name": "High Quality",
      "slug": "high-quality",
      "count": 10
    }
  ],
  "helpful_count": 0,
  "is_helpful": false,
  "variant": null,
  "is_verified_purchase": true,
  "created_at": "2024-01-27T16:00:00Z"
}

Copy


Error Response (400):
{
  "status": "error",
  "message": "You have already reviewed this product"
}

Copy


Mark Review as Helpful
URL: /reviews/<review_id>/mark-helpful/
Method: POST
Auth Required: Yes
Description: Marks a review as helpful
Success Response (200):
{
  "success": true,
  "helpful_count": 6
}

Copy


Cart Endpoints
Get Cart
URL: /cart/
Method: GET
Auth Required: Yes
Description: Retrieves the authenticated user's cart
Success Response (200):
{
  "cart_id": 1,
  "user": 1,
  "items": [
    {
      "cart_item_id": 1,
      "product": 1,
      "quantity": 2,
      "product_name": "Product Name",
      "product_price": "99.99",
      "stock_status": "active",
      "product_image": "image_url"
    }
  ],
  "created_at": "2024-01-20T10:30:00Z",
  "updated_at": "2024-01-20T10:30:00Z"
}

Copy


Get Cart Summary
URL: /cart/summary/
Method: GET
Auth Required: Yes
Description: Retrieves a summary of the cart
Success Response (200):
{
  "total_items": 2,
  "total_price": "199.98",
  "items_count": 1
}

Copy


Add Item to Cart
URL: /cart/add-item/
Method: POST
Auth Required: Yes
Description: Adds an item to the cart
Request Body:
{
  "product_id": 1,
  "quantity": 1
}

Copy


Success Response (201):
{
  "success": true,
  "message": "Item added to cart",
  "cart_item": {
    "cart_item_id": 1,
    "product": 1,
    "quantity": 1,
    "product_name": "Product Name",
    "product_price": "99.99",
    "stock_status": "active",
    "product_image": "image_url"
  }
}

Copy


Error Response (400):
{
  "status": "error",
  "message": "Product is out of stock"
}

Copy


Update Cart Item Quantity
URL: /cart/update-quantity/
Method: POST
Auth Required: Yes
Description: Updates the quantity of an item in the cart
Request Body:
{
  "product_id": 1,
  "quantity": 2
}

Copy


Success Response (200):
{
  "success": true,
  "message": "Quantity updated",
  "cart_item": {
    "cart_item_id": 1,
    "product": 1,
    "quantity": 2,
    "product_name": "Product Name",
    "product_price": "99.99",
    "stock_status": "active",
    "product_image": "image_url"
  }
}

Copy


Remove Item from Cart
URL: /cart/remove-item/
Method: POST
Auth Required: Yes
Description: Removes an item from the cart
Request Body:
{
  "product_id": 1
}

Copy


Success Response (204): No content
Apply Discount to Cart
URL: /cart/apply-discount/
Method: POST
Auth Required: Yes
Description: Applies a promo code to the cart
Request Body:
{
  "code": "SUMMER20"
}

Copy


Success Response (200):
{
  "success

Copy



Copy

continue



Context
— none fetched
Cart Endpoints (continued)
Apply Discount to Cart (continued)
Success Response (200):
{
  "success": true,
  "message": "Discount applied successfully",
  "discount_percentage": "20.00",
  "total_before_discount": "199.98",
  "total_after_discount": "159.98"
}

Copy


Error Response (400):
{
  "status": "error",
  "message": "Invalid promo code"
}

Copy


Clear Cart
URL: /cart/clear/
Method: POST
Auth Required: Yes
Description: Removes all items from the cart
Success Response (200):
{
  "success": true,
  "message": "Cart cleared successfully"
}

Copy


Wishlist Endpoints
Get Wishlist
URL: /wishlist/
Method: GET
Auth Required: Yes
Description: Retrieves the authenticated user's wishlist
Success Response (200):
{
  "id": 1,
  "user": 1,
  "products": [
    {
      "id": 1,
      "name": "Product Name",
      "description": "Product description",
      "main_image": "image_url",
      "images": ["url1", "url2"],
      "price": "99.99",
      "is_liked": true,
      "status": "active",
      "added_at": "2024-01-20T10:30:00Z"
    }
  ],
  "products_count": 1
}

Copy


Add Item to Wishlist
URL: /wishlist-items/
Method: POST
Auth Required: Yes
Description: Adds a product to the wishlist
Request Body:
{
  "product": 1
}

Copy


Success Response (201):
{
  "id": 1,
  "wishlist": 1,
  "product": 1,
  "added_at": "2024-01-20T10:30:00Z",
  "product_details": {
    "id": 1,
    "name": "Product Name",
    "description": "Product description",
    "main_image": "image_url",
    "images": ["url1", "url2"],
    "price": "99.99",
    "status": "active",
    "is_liked": true
  }
}

Copy


Remove Item from Wishlist
URL: /wishlist-items/<id>/
Method: DELETE
Auth Required: Yes
Description: Removes an item from the wishlist
Success Response (204): No content
Remove Item from Wishlist by Product ID
URL: /wishlist-items/<product_id>/remove/
Method: DELETE
Auth Required: Yes
Description: Removes an item from the wishlist by product ID
Success Response (204): No content
Move Item to Cart
URL: /wishlist/move-to-cart/<pk>/
Method: POST
Auth Required: Yes
Description: Moves a wishlist item to the cart
Request Body:
{
  "wishlist_item_id": 1,
  "quantity": 1
}

Copy


Success Response (201):
{
  "success": true,
  "message": "Item moved to cart successfully"
}

Copy


Error Response (400):
{
  "status": "error",
  "message": "Invalid wishlist item or quantity"
}

Copy


Bulk Delete Wishlist Items
URL: /wishlist/bulk-delete/
Method: POST
Auth Required: Yes
Description: Deletes multiple wishlist items
Request Body:
{
  "wishlist_item_ids": [1, 2, 3]
}

Copy


Success Response (204): No content
Get Stock Notifications
URL: /wishlist/stock-notifications/
Method: GET
Auth Required: Yes
Description: Retrieves stock notifications for wishlist items
Success Response (200):
[
  {
    "id": 1,
    "notification_type": "BACK_IN_STOCK",
    "message": "Product Name is back in stock!",
    "is_read": false,
    "created_at": "2024-01-20T10:30:00Z"
  }
]

Copy


Order Endpoints
List Orders
URL: /orders/
Method: GET
Auth Required: Yes
Description: Retrieves all orders for the authenticated user
Query Parameters:
status: PENDING/PROCESSING/SHIPPED/DELIVERED/CANCELLED
start_date: Filter by start date
end_date: Filter by end date
Success Response (200):
[
  {
    "id": 1,
    "order_number": "ORD-20240120-0001",
    "customer_email": "user@example.com",
    "customer_name": "John Doe",
    "items": [
      {
        "id": 1,
        "product": 1,
        "product_name": "Product Name",
        "product_sku": "PRD001",
        "quantity": 2,
        "unit_price": "99.99",
        "total_price": "199.98",
        "variants": {}
      }
    ],
    "total": "204.97",
    "status": "PENDING",
    "status_display": "Pending",
    "payment": {
      "id": 1,
      "method": "CREDIT",
      "amount": "204.97",
      "status": "PENDING",
      "created_at": "2024-01-20T10:30:00Z"
    },
    "payments": [
      {
        "id": 1,
        "method": "CREDIT",
        "amount": "204.97",
        "status": "PENDING",
        "created_at": "2024-01-20T10:30:00Z"
      }
    ],
    "shipping_address": "123 Main St, Lagos, Nigeria",
    "created_at": "2024-01-20T10:30:00Z",
    "updated_at": "2024-01-20T10:30:00Z",
    "note": "",
    "payment_type": "CREDIT",
    "order_type": "STANDARD",
    "order_date": "2024-01-20",
    "order_time": "10:30:00"
  }
]

Copy


Get Order
URL: /orders/<id>/
Method: GET
Auth Required: Yes
Description: Retrieves a specific order
Success Response (200):
{
  "id": 1,
  "order_number": "ORD-20240120-0001",
  "customer_email": "user@example.com",
  "customer_name": "John Doe",
  "items": [
    {
      "id": 1,
      "product": 1,
      "product_name": "Product Name",
      "product_sku": "PRD001",
      "quantity": 2,
      "unit_price": "99.99",
      "total_price": "199.98",
      "variants": {}
    }
  ],
  "total": "204.97",
  "status": "PENDING",
  "status_display": "Pending",
  "payment": {
    "id": 1,
    "method": "CREDIT",
    "amount": "204.97",
    "status": "PENDING",
    "created_at": "2024-01-20T10:30:00Z"
  },
  "payments": [
    {
      "id": 1,
      "method": "CREDIT",
      "amount": "204.97",
      "status": "PENDING",
      "created_at": "2024-01-20T10:30:00Z"
    }
  ],
  "shipping_address": "123 Main St, Lagos, Nigeria",
  "created_at": "2024-01-20T10:30:00Z",
  "updated_at": "2024-01-20T10:30:00Z",
  "note": "",
  "payment_type": "CREDIT",
  "order_type": "STANDARD",
  "order_date": "2024-01-20",
  "order_time": "10:30:00"
}

Copy


Error Response (404):
{
  "status": "error",
  "message": "Order not found"
}

Copy


Create Order
URL: /orders/
Method: POST
Auth Required: Yes
Description: Creates a new order
Request Body:
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "variants": {}
    }
  ],
  "payment_method": "CREDIT",
  "shipping_address": "123 Main St, Lagos, Nigeria",
  "billing_address": "123 Main St, Lagos, Nigeria",
  "note": "Please deliver to the front door",
  "payment_type": "CREDIT",
  "order_type": "STANDARD"
}

Copy


Success Response (201):
{
  "status": "success",
  "message": "Order created successfully",
  "order_id": 1,
  "total": "204.97"
}

Copy


Error Response (400):
{
  "status": "error",
  "message": "Cart is empty"
}

Copy


Get Order Tracking
URL: /orders/<id>/tracking/
Method: GET
Auth Required: Yes
Description: Retrieves tracking information for an order
Success Response (200):
[
  {
    "id": 1,
    "status": "PROCESSING",
    "location": "Lagos Sorting Center",
    "description": "Package is being processed",
    "timestamp": "2024-01-20T10:30:00Z"
  }
]

Copy


Add Tracking Event
URL: /orders/<id>/tracking/add/
Method: POST
Auth Required: Yes (Admin)
Description: Adds a tracking event to an order
Request Body:
{
  "status": "SHIPPED",
  "location": "Lagos Distribution Center",
  "description": "Package has left the warehouse"
}

Copy


Success Response (200):
{
  "id": 2,
  "status": "SHIPPED",
  "location": "Lagos Distribution Center",
  "description": "Package has left the warehouse",
  "timestamp": "2024-01-20T11:30:00Z"
}

Copy


Update Order Status
URL: /orders/<id>/update_status/
Method: PATCH
Auth Required: Yes (Admin)
Description: Updates the status of an order
Request Body:
{
  "status": "SHIPPED"
}

Copy


Success Response (200):
{
  "id": 1,
  "status": "SHIPPED",
  "updated_at": "2024-01-20T11:30:00Z"
}

Copy


Filter Orders by Date
URL: /orders/filter-by-date/
Method: GET
Auth Required: Yes
Description: Filters orders by date range
Query Parameters:
start_date: Start date (YYYY-MM-DD)
end_date: End date (YYYY-MM-DD)
Success Response (200):
[
  {
    "id": 1,
    "order_number": "ORD-20240120-0001",
    "customer_email": "user@example.com",
    "customer_name": "John Doe",
    "total": "204.97",
    "status": "PENDING",
    "created_at": "2024-01-20T10:30:00Z"
  }
]

Copy


Shipping Method Endpoints
List Shipping Methods
URL: /shipping-methods/
Method: GET
Auth Required: No
Description: Retrieves all available shipping methods
Success Response (200):
[
  {
    "id": 1,
    "name": "Standard Shipping",
    "price": "4.99",
    "estimated_days": 5,
    "description": "Delivery within 3-7 business days",
    "delivery_date": "2024-01-25T10:30:00Z"
  }
]

Copy


Create Shipping Method (Admin only)
URL: /shipping-methods/
Method: POST
Auth Required: Yes (Admin)
Description: Creates a new shipping method
Request Body:
{
  "name": "Express Shipping",
  "price": "10.00",
  "estimated_days": 2,
  "description": "Delivery within 1-3 business days"
}

Copy


Success Response (201):
{
  "id": 2,
  "name": "Express Shipping",
  "price": "10.00",
  "estimated_days": 2,
  "description": "Delivery within 1-3 business days",
  "delivery_date": "2024-01-22T10:30:00Z"
}

Copy


Error Response (403):
{
  "status": "error",
  "message": "You do not have permission to perform this action"
}

Copy


Get Shipping Method
URL: /shipping-methods/<id>/
Method: GET
Auth Required: No
Description: Retrieves a specific shipping method
Success Response (200):
{
  "id": 1,
  "name": "Standard Shipping",
  "price": "4.99",
  "estimated_days": 5,
  "description": "Delivery within 3-7 business days",
  "delivery_date": "2024-01-25T10:30:00Z"
}

Copy


Error Response (404):
{
  "status": "error",
  "message": "Shipping method not found"
}

Copy


Update Shipping Method (Admin only)
URL: /shipping-methods/<id>/
Method: PUT/PATCH
Auth Required: Yes (Admin)
Description: Updates a shipping method
Request Body:
{
  "price": "5.99"
}

Copy


Success Response (200):
{
  "id": 1,
  "name": "Standard Shipping",
  "price": "5.99",
  "estimated_days": 5,
  "description": "Delivery within 3-7 business days",
  "delivery_

Copy



Copy

continue



Context
— none fetched
Shipping Method Endpoints (continued)
Update Shipping Method (Admin only) (continued)
Success Response (200):
{
  "id": 1,
  "name": "Standard Shipping",
  "price": "5.99",
  "estimated_days": 5,
  "description": "Delivery within 3-7 business days",
  "delivery_date": "2024-01-25T10:30:00Z"
}

Copy


Delete Shipping Method (Admin only)
URL: /shipping-methods/<id>/
Method: DELETE
Auth Required: Yes (Admin)
Description: Deletes a shipping method
Success Response (204): No content
Checkout Endpoints
Initiate Checkout
URL: /checkout/initiate/
Method: POST
Auth Required: Yes
Description: Initiates the checkout process
Request Body:
{
  "shipping_method_id": 1,
  "payment_method": "stripe"
}

Copy


Success Response (200):
{
  "checkout_id": "checkout_123",
  "subtotal": "199.98",
  "shipping_cost": "4.99",
  "tax": "0.00",
  "discount": "0.00",
  "total": "204.97",
  "shipping_method": {
    "id": 1,
    "name": "Standard Shipping",
    "price": "4.99"
  },
  "payment_method": "stripe",
  "items": [
    {
      "product_id": 1,
      "name": "Product Name",
      "quantity": 2,
      "price": "99.99",
      "subtotal": "199.98"
    }
  ]
}

Copy


Error Response (400):
{
  "status": "error",
  "message": "Invalid shipping method or payment method"
}

Copy


Get Checkout Summary
URL: /checkout/summary/
Method: GET
Auth Required: Yes
Description: Retrieves a summary of the current checkout
Success Response (200):
{
  "checkout_id": "checkout_123",
  "subtotal": "199.98",
  "shipping_cost": "4.99",
  "tax": "0.00",
  "discount": "0.00",
  "total": "204.97",
  "shipping_method": {
    "id": 1,
    "name": "Standard Shipping",
    "price": "4.99"
  },
  "payment_method": "stripe",
  "items": [
    {
      "product_id": 1,
      "name": "Product Name",
      "quantity": 2,
      "price": "99.99",
      "subtotal": "199.98"
    }
  ]
}

Copy


Process Payment
URL: /checkout/payment/
Method: POST
Auth Required: Yes
Description: Processes payment for the checkout
Request Body:
{
  "payment_method_id": "pm_card_visa",
  "save_card": true
}

Copy


Success Response (200):
{
  "success": true,
  "order_id": 1,
  "order_number": "ORD-20240120-0001",
  "transaction_id": "txn_1234567890",
  "amount": "204.97",
  "status": "PAID"
}

Copy


Error Response (400):
{
  "status": "error",
  "message": "Payment processing failed",
  "details": "Your card was declined"
}

Copy


Support Ticket Endpoints
List Support Tickets
URL: /help/
Method: GET
Auth Required: Yes
Description: Retrieves all support tickets for the authenticated user
Success Response (200):
[
  {
    "id": 1,
    "full_name": "John Doe",
    "message": "My order hasn't arrived",
    "status": "OPEN",
    "created_at": "2024-01-20T10:30:00Z",
    "updated_at": "2024-01-20T10:30:00Z"
  }
]

Copy


Create Support Ticket
URL: /help/
Method: POST
Auth Required: Yes
Description: Creates a new support ticket
Request Body:
{
  "full_name": "John Doe",
  "message": "My order hasn't arrived"
}

Copy


Success Response (201):
{
  "id": 1,
  "full_name": "John Doe",
  "message": "My order hasn't arrived",
  "status": "OPEN",
  "created_at": "2024-01-20T10:30:00Z",
  "updated_at": "2024-01-20T10:30:00Z"
}

Copy


Get Support Ticket
URL: /help/<id>/
Method: GET
Auth Required: Yes
Description: Retrieves a specific support ticket
Success Response (200):
{
  "id": 1,
  "full_name": "John Doe",
  "message": "My order hasn't arrived",
  "status": "OPEN",
  "created_at": "2024-01-20T10:30:00Z",
  "updated_at": "2024-01-20T10:30:00Z"
}

Copy


Error Response (404):
{
  "status": "error",
  "message": "Support ticket not found"
}

Copy


Update Support Ticket
URL: /help/<id>/
Method: PATCH
Auth Required: Yes
Description: Updates a support ticket
Request Body:
{
  "status": "CLOSED"
}

Copy


Success Response (200):
{
  "id": 1,
  "full_name": "John Doe",
  "message": "My order hasn't arrived",
  "status": "CLOSED",
  "created_at": "2024-01-20T10:30:00Z",
  "updated_at": "2024-01-20T11:30:00Z"
}

Copy


Submit Support Ticket
URL: /support/submit/
Method: POST
Auth Required: Yes
Description: Alternative endpoint to create a support ticket
Request Body:
{
  "subject": "Order Issue",
  "message": "My order hasn't arrived"
}

Copy


Success Response (201):
{
  "status": "success",
  "message": "Support ticket submitted successfully",
  "ticket_id": 1
}

Copy


Dashboard Endpoints (Admin only)
Cart Metrics
URL: /dashboard/cart_metrics/
Method: GET
Auth Required: Yes (Admin)
Description: Retrieves cart metrics for the dashboard
Query Parameters:
period: day/week/month/year
Success Response (200):
{
  "success": true,
  "data": {
    "abandoned_rate": 0.75,
    "total_carts": 100,
    "abandoned_carts": 75,
    "period": "month"
  }
}

Copy


Customer Metrics
URL: /dashboard/customer_metrics/
Method: GET
Auth Required: Yes (Admin)
Description: Retrieves customer metrics for the dashboard
Query Parameters:
period: day/week/month/year
Success Response (200):
{
  "success": true,
  "data": {
    "total_customers": 500,
    "active_customers": 300,
    "growth_rate": 0.15,
    "period": "month"
  }
}

Copy


Order Metrics
URL: /dashboard/order_metrics/
Method: GET
Auth Required: Yes (Admin)
Description: Retrieves order metrics for the dashboard
Query Parameters:
period: day/week/month/year
Success Response (200):
{
  "success": true,
  "data": {
    "orders_by_status": [
      {
        "status": "PENDING",
        "count": 10
      },
      {
        "status": "PROCESSING",
        "count": 15
      },
      {
        "status": "SHIPPED",
        "count": 20
      },
      {
        "status": "DELIVERED",
        "count": 50
      },
      {
        "status": "CANCELLED",
        "count": 5
      }
    ],
    "total_revenue": "10000.00",
    "total_orders": 100,
    "period": "month"
  }
}

Copy


Sales Trend
URL: /dashboard/sales_trend/
Method: GET
Auth Required: Yes (Admin)
Description: Retrieves sales trend data for the dashboard
Query Parameters:
period: day/week/month/year
Success Response (200):
{
  "success": true,
  "data": [
    {
      "date": "2024-03-01",
      "revenue": "5000.00",
      "orders": 25
    },
    {
      "date": "2024-03-02",
      "revenue": "6500.00",
      "orders": 32
    }
  ]
}

Copy


Recent Orders
URL: /dashboard/recent_orders/
Method: GET
Auth Required: Yes (Admin)
Description: Retrieves recent orders for the dashboard
Success Response (200):
{
  "success": true,
  "data": [
    {
      "id": 1,
      "user_email": "customer@example.com",
      "total": "299.99",
      "status": "PROCESSING",
      "created_at": "2024-03-10T14:30:00Z",
      "items": [
        {
          "product_name": "Product Name",
          "quantity": 2,
          "price": "149.99"
        }
      ]
    }
  ]
}

Copy


Customer Management Endpoints (Admin only)
List Customers
URL: /customers/
Method: GET
Auth Required: Yes (Admin)
Description: Retrieves all customers
Success Response (200):
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+2348012345678",
    "orders_count": 5,
    "total_balance": "1000.00",
    "status": "Active"
  }
]

Copy


Get Customer
URL: /customers/<id>/
Method: GET
Auth Required: Yes (Admin)
Description: Retrieves a specific customer
Success Response (200):
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+2348012345678",
  "orders_count": 5,
  "total_balance": "1000.00",
  "status": "Active"
}

Copy


Error Response (404):
{
  "status": "error",
  "message": "Customer not found"
}

Copy


Create Customer
URL: /customers/
Method: POST
Auth Required: Yes (Admin)
Description: Creates a new customer
Request Body:
{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+2348012345679",
  "password": "securepassword"
}

Copy


Success Response (201):
{
  "id": 2,
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+2348012345679"
}

Copy


Update Customer
URL: /customers/<id>/
Method: PUT/PATCH
Auth Required: Yes (Admin)
Description: Updates a customer
Request Body:
{
  "phone": "+2348012345680"
}

Copy


Success Response (200):
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+2348012345680"
}

Copy


Delete Customer
URL: /customers/<id>/
Method: DELETE
Auth Required: Yes (Admin)
Description: Deletes a customer
Success Response (204): No content
Waitlist Endpoints
Join Waitlist
URL: /waitlist/signup/
Method: POST
Auth Required: No
Description: Adds an email to the waitlist
Request Body:
{
  "email": "user@example.com"
}

Copy


Success Response (201):
{
  "message": "Successfully joined the waitlist!",
  "data": {
    "email": "user@example.com",
    "created_at": "2024-12-13T12:07:18.068767Z"
  }
}

Copy


Error Response (400):
{
  "status": "error",
  "message": "This email is already on the waitlist."
}

Copy


Preview Email
URL: /preview_email/
Method: GET
Auth Required: No
Description: Previews the waitlist confirmation email template
Success Response (200): HTML content of the email
continue



Context
— none fetched
Common Error Responses
401 Unauthorized
{
  "success": false,
  "message": "Authentication credentials were not provided"
}

Copy


400 Bad Request
{
  "success": false,
  "message": "Invalid period parameter",
  "valid_periods": ["day", "week", "month", "year"]
}
 
Copy


500 Server Error
{
  "success": false,
  "message": "An error occurred while processing your request"
}

Copy


Rate Limiting
5 requests per minute per IP address
Status 429 will be returned if rate limit is exceeded
Data Formats
All timestamps are in ISO 8601 format
All monetary values are decimal strings with 2 decimal places
All percentage values are floats
Payment Integration
Supported Payment Methods
Stripe
PayPal
Clover
Payment Flow
Initiate checkout with selected payment method
Retrieve payment intent/token from the server
Complete payment on the client side
Server confirms payment and creates order
Save Payment Method
Users can save payment methods for future use by setting the save_card parameter to true during checkout.

Webhooks
Payment Webhooks
Stripe, PayPal, and Clover webhooks are supported for asynchronous payment processing
Webhooks should be configured in the respective payment provider dashboards
File Upload Guidelines
Product Images
Maximum file size: 5MB
Supported formats: JPG, PNG
Recommended dimensions: 1000x1000 pixels
User Profile Photos
Maximum file size: 2MB
Supported formats: JPG, PNG
Recommended dimensions: 500x500 pixels
Versioning
Current API version: v1
API versioning is handled through the URL path
Support
For API support, please contact:

Email: avalusht@gmail.com
Create a support ticket through the API
This documentation covers all the endpoints, request/response formats, and error handling for the Avantlush API.
---

## Admin Dashboard - Product Management UI Endpoints

This section details the API endpoints specifically used by the Product Management section of the Admin Dashboard UI.

### 1. List and Filter Products (Product Table)

This endpoint populates the main product table in the dashboard, supporting pagination, searching, and filtering by tabs (All, Published, Low Stock, Draft) and category.

*   **UI Feature:** Main product listing table, search bar, filter tabs, category filter, pagination.
*   **Endpoint:** `GET /api/dashboard/product_management_data/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves a paginated list of products tailored for the admin dashboard, with filtering and search capabilities.
*   **Query Parameters:**
    *   `tab` (string, optional): Filters products by status. Values: `all`, `published`, `low_stock`, `draft`. Default: `all`.
    *   `search` (string, optional): Search term for product name, SKU, or category name.
    *   `category` (string, optional): Filter by category slug.
    *   `page` (integer, optional): Page number for pagination. Default: `1`.
    *   `page_size` (integer, optional): Number of items per page. Default: `10`.
*   **Success Response (200 OK):**
    ```json
    {
        "products": [
            {
                "id": 1,
                "name": "Ergonomic Chair",
                "sku": "302012",
                "category": "Chair",
                "category_id": 1,
                "variants": "3 Variants",
                "variant_count": 3,
                "stock_quantity": 10,
                "stock_status": "low_stock", // "out_of_stock", "low_stock", "in_stock"
                "stock_label": "Low Stock",   // "Out of Stock", "Low Stock", "In Stock"
                "stock_color": "orange",    // "red", "orange", "green"
                "price": 121.00,
                "status": "low_stock", // "published", "draft", "low_stock", "out_of_stock", etc.
                "status_color": "orange", // "green", "gray", "orange", "red"
                "created_at": "29 Dec 2022", // Formatted date
                "updated_at": "29 Dec 2022",
                "main_image": "https://res.cloudinary.com/...",
                "is_featured": false,
                "rating": 0.00,
                "num_ratings": 0
            }
            // ... more products
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 10,
            "total_count": 100,
            "page_size": 10,
            "has_next": true,
            "has_previous": false
        },
        "filters": {
            "tab": "all",
            "search": "",
            "category": ""
        },
        "tab_counts": {
            "all": 100,
            "published": 50,
            "low_stock": 15,
            "draft": 35
        }
    }
    ```
*   **Error Response (401 Unauthorized):**
    ```json
    {
        "detail": "Authentication credentials were not provided."
    }
    ```
*   **Error Response (403 Forbidden):**
    ```json
    {
        "detail": "You do not have permission to perform this action."
    }
    ```

### 2. Add New Product

This endpoint is used when the "Add Product" button is clicked.

*   **UI Feature:** "Add Product" button and subsequent form.
*   **Endpoint:** `POST /api/products/`
*   **Method:** `POST`
*   **Auth Required:** Yes (Admin)
*   **Description:** Creates a new product.
*   **Request Body (Payload):** (Based on `ProductManagementSerializer`)
    ```json
    {
        "name": "New Awesome Chair",
        "description": "A very comfortable and stylish chair.",
        "product_details": ["Adjustable height", "Lumbar support"], // List of strings
        "category": 1, // Category ID
        "tags": [1, 2], // List of Tag IDs (optional)
        "base_price": "199.99", // Renamed from 'price' in serializer to 'base_price' for clarity if it's the base
        "discount_type": "percentage", // "percentage" or "fixed" (optional)
        "discount_percentage": "10.00", // (optional)
        "vat_amount": "5.00", // (optional)
        "sku": "CHR-NEW-001",
        "barcode": "1234567890123", // (optional)
        "stock_quantity": 50,
        "status": "draft", // "draft", "published", "active", etc.
        "is_featured": false,
        "is_physical_product": true,
        "weight": "15.5", // (optional)
        "height": "100.0", // (optional)
        "length": "60.0", // (optional)
        "width": "60.0", // (optional)
        "main_image": null, // Can be set via a separate image upload endpoint or included if serializer supports direct upload
        "image_files": [], // For multipart/form-data image uploads if supported by this endpoint directly
        "variations": [ // (optional)
            {
                "variation_type": "Color", // Kept for backward compatibility
                "variation": "Red",      // Kept for backward compatibility
                "price_adjustment": "10.00",
                "stock_quantity": 10,
                "sku": "CHR-NEW-001-RED",
                "is_default": false,
                "size_ids": [1], // List of Size IDs for this variation
                "color_ids": [2] // List of Color IDs for this variation
            }
        ]
    }
    ```
    *Note: For image uploads, it's common to use `multipart/form-data` and handle `main_image` or `image_files` separately or via dedicated image upload endpoints.*
*   **Success Response (201 Created):** (Based on `ProductManagementSerializer`)
    ```json
    {
        "id": 101,
        "name": "New Awesome Chair",
        "description": "A very comfortable and stylish chair.",
        "product_details": ["Adjustable height", "Lumbar support"],
        "category": 1,
        "category_name": "Chairs",
        "tags": [1, 2],
        "status": "draft",
        "status_display": "Draft",
        "main_image": null,
        "images": [], // URLs of additional images
        "is_featured": false,
        "is_liked": false, // Assuming not liked upon creation
        "available_sizes": [], // Populated if sizes are linked
        "available_colors": [], // Populated if colors are linked
        "base_price": "199.99",
        "discount_type": "percentage",
        "discount_percentage": "10.00",
        "vat_amount": "5.00",
        "sku": "CHR-NEW-001",
        "barcode": "1234567890123",
        "stock_quantity": 50,
        "variations": [
            {
                "id": 1,
                "variation_type": "Color",
                "variation": "Red",
                "price_adjustment": "10.00",
                "stock_quantity": 10,
                "sku": "CHR-NEW-001-RED",
                "is_default": false,
                "final_price": 209.99, // base_price + price_adjustment
                "sizes": [{"id": 1, "name": "Large"}],
                "colors": [{"id": 2, "name": "Red", "hex_code": "#FF0000"}]
            }
        ],
        "is_physical_product": true,
        "weight": "15.50",
        "height": "100.00",
        "length": "60.00",
        "width": "60.00",
        "created_at": "2024-06-05T14:00:00Z",
        "added_date_formatted": "05 Jun 2024",
        "variants_count": 1,
        "all_images": {
            "main_image": null,
            "gallery": []
        }
    }
    ```
*   **Error Response (400 Bad Request):**
    ```json
    {
        "name": ["This field is required."],
        "sku": ["Product with this SKU already exists."],
        "base_price": ["A valid number is required."]
        // ... other validation errors
    }
    ```

### 3. Edit Product

This endpoint is used when the "Edit" icon (pencil) in the product table is clicked.

*   **UI Feature:** "Edit" icon and subsequent product editing form.
*   **Endpoint:** `PUT /api/products/<id>/` or `PATCH /api/products/<id>/`
*   **Method:** `PUT` (to replace the entire resource) or `PATCH` (to partially update)
*   **Auth Required:** Yes (Admin)
*   **Description:** Updates an existing product.
*   **Request Body (Payload):** (Similar to "Add New Product", fields are optional for `PATCH`)
    ```json
    {
        "name": "Updated Ergonomic Chair",
        "base_price": "125.00",
        "stock_quantity": 45,
        "status": "published"
        // ... other fields to update
    }
    ```
*   **Success Response (200 OK):** (Similar to the "Add New Product" success response, showing the updated product)
    ```json
    {
        "id": 1, // Existing product ID
        "name": "Updated Ergonomic Chair",
        "base_price": "125.00",
        "stock_quantity": 45,
        "status": "published",
        "status_display": "Published",
        // ... other fields
    }
    ```
*   **Error Response (400 Bad Request):**
    ```json
    {
        "base_price": ["A valid number is required."]
    }
    ```
*   **Error Response (404 Not Found):**
    ```json
    {
        "detail": "Not found."
    }
    ```

### 4. Delete Product

This endpoint is used when the "Delete" icon (trash can) in the product table is clicked for a single product.

*   **UI Feature:** "Delete" icon in the product table.
*   **Endpoint:** `DELETE /api/products/<id>/`
*   **Method:** `DELETE`
*   **Auth Required:** Yes (Admin)
*   **Description:** Deletes a specific product.
*   **Success Response (204 No Content):** (No body content)
*   **Error Response (404 Not Found):**
    ```json
    {
        "detail": "Not found."
    }
    ```

### 5. View Product Details

This endpoint could be used if clicking the "View" icon (eye) leads to a detailed product view page (though the UI screenshot doesn't explicitly show this page, it's a common action).

*   **UI Feature:** "View" icon in the product table.
*   **Endpoint:** `GET /api/products/<id>/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin, if it's an admin-specific detailed view) or No (if it's a public product detail page). The `ProductViewSet` is `AllowAny` for GET by default.
*   **Description:** Retrieves details for a specific product.
*   **Success Response (200 OK):** (Based on `ProductManagementSerializer` or `ProductSerializer`)
    ```json
    {
        "id": 1,
        "name": "Ergonomic Chair",
        "slug": "ergonomic-chair",
        "description": "High-quality ergonomic chair.",
        "price": "121.00", // Or base_price depending on serializer
        "category": 1,
        "category_name": "Chair",
        "images": ["url_to_image1.jpg"],
        "main_image": "url_to_main_image.jpg",
        "stock_quantity": 10,
        "is_featured": false,
        "is_physical_product": true,
        "sku": "302012",
        "status": "low_stock",
        "rating": "0.00",
        "num_ratings": 0,
        "is_liked": false,
        "product_details": ["Adjustable", "Comfortable"],
        "variations": [
            // ... list of variations using ProductVariationSerializer
        ],
        // ... other fields from ProductManagementSerializer
        "created_at": "2022-12-29T00:00:00Z",
        "updated_at": "2022-12-29T00:00:00Z"
    }
    ```
*   **Error Response (404 Not Found):**
    ```json
    {
        "detail": "Not found."
    }
    ```

### 6. Bulk Product Actions

This endpoint handles actions like "Delete Selected", "Publish Selected", "Draft Selected" when multiple products are checked.

*   **UI Feature:** Checkboxes next to products and bulk action dropdown (e.g., "Delete Selected").
*   **Endpoint:** `POST /api/dashboard/bulk_product_action/`
*   **Method:** `POST`
*   **Auth Required:** Yes (Admin)
*   **Description:** Performs a bulk action (delete, publish, draft, feature) on selected products.
*   **Request Body (Payload):**
    ```json
    {
        "action": "delete", // "delete", "publish", "draft", "feature"
        "product_ids": [1, 2, 5] // Array of product IDs
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "message": "3 products deleted successfully" // Message varies based on action
    }
    ```
    For status updates:
    ```json
    {
        "message": "3 products published successfully"
    }
    ```
*   **Error Response (400 Bad Request):**
    ```json
    {
        "error": "Action and product_ids are required"
    }
    ```
    ```json
    {
        "error": "Invalid action"
    }
    ```

### 7. Export Products

This endpoint is triggered by the "Export" button.

*   **UI Feature:** "Export" button.
*   **Endpoint:** `GET /api/dashboard/export_products/`
    *(Note: `ProductViewSet` also has a `/api/products/export/` endpoint. The dashboard might use the one under `/dashboard/` if it has specific formatting or filtering for the dashboard context.)*
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Exports product data as a CSV file.
*   **Query Parameters:** (Potentially supports the same filters as the product list: `tab`, `search`, `category`)
*   **Success Response (200 OK):**
    *   Content-Type: `text/csv`
    *   Body: CSV formatted data of products.
    ```csv
    Name,SKU,Category,Price,Stock,Status,Created
    Ergonomic Chair,302012,Chair,121.00,10,Low Stock,2022-12-29
    Table,301600,Table,400.00,347,Published,2022-09-19
    ...
    ```
*   **Error Response (403 Forbidden):**
    ```json
    {
        "detail": "You do not have permission to perform this action."
    }
    ```

### 8. Get Tab Counts for Filtering

This endpoint can provide the counts displayed next to filter tabs (All, Published, Low Stock, Draft).

*   **UI Feature:** Counts next to filter tabs.
*   **Endpoint:** `GET /api/products/tab_counts/` (Action in `ProductViewSet`)
    *(Alternatively, this data is also included in the response of `GET /api/dashboard/product_management_data/`)*
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves the count of products for each status tab.
*   **Success Response (200 OK):**
    ```json
    {
        "all": 100,
        "published": 50,
        "low_stock": 15, // Products with stock_quantity <= 10
        "draft": 35
    }
    ```

### 9. Get Categories for Filtering

This endpoint populates the "Category" filter dropdown.

*   **UI Feature:** "Filters" button, which likely includes a category dropdown.
*   **Endpoint:** `GET /api/products/categories/` (Action in `ProductViewSet`)
*   **Method:** `GET`
*   **Auth Required:** No (Publicly accessible, but used in admin context here)
*   **Description:** Retrieves a list of all product categories.
*   **Success Response (200 OK):**
    ```json
    [
        {
            "id": 1,
            "name": "Chair",
            "slug": "chair",
            "parent": null
        },
        {
            "id": 2,
            "name": "Table",
            "slug": "table",
            "parent": null
        }
        // ... more categories
    ]
    ```

### 10. Get Product Sizes and Colors (for Product Form)

These endpoints are used to populate dropdowns for selecting sizes and colors when adding/editing a product with variations.

*   **UI Feature:** Size and Color selection in the "Add Product" / "Edit Product" form, especially for variations.
*   **Endpoints:**
    *   `GET /api/products/sizes/` (Action in `ProductViewSet`)
    *   `GET /api/products/colors/` (Action in `ProductViewSet`)
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves all available sizes or colors.
*   **Success Response for Sizes (200 OK):**
    ```json
    [
        {"id": 1, "name": "Small"},
        {"id": 2, "name": "Medium"},
        {"id": 3, "name": "Large"}
    ]
    ```
*   **Success Response for Colors (200 OK):**
    ```json
    [
        {"id": 1, "name": "Red", "hex_code": "#FF0000"},
        {"id": 2, "name": "Blue", "hex_code": "#0000FF"}
    ]
    ```

---
---

### Admin Dashboard - Overview UI Endpoints

This section details API endpoints supporting the main dashboard overview page, including summary cards, sales charts, and recent orders.

#### 1. Dashboard Overview Metrics (Summary Cards)

Provides aggregated data for the summary cards (All Orders, Pending, Completed, Abandoned Cart, Customers, Active Customers).

*   **UI Feature:** Summary cards at the top of the dashboard.
*   **Endpoint:** `GET /api/dashboard/overview_metrics/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves key performance indicators and their changes over a specified period.
*   **Query Parameters:**
    *   `period` (string, optional): Time period for metrics. Values: `day`, `week`, `month`, `year`. Default: `week`.
*   **Success Response (200 OK):**
    ```json
    {
        "abandoned_cart": {
            "rate": 25.5, // Percentage
            "change": 5.2, // Percentage point change from previous period
            "total_carts": 200,
            "abandoned_count": 51
        },
        "customers": {
            "new_customers": 50,
            "new_customers_growth": 10.5, // Percentage change
            "total_customers": 1500,
            "total_growth": 2.1 // Percentage change
        },
        "active_customers": {
            "count": 350,
            "growth": 8.0 // Percentage change
        },
        "orders": {
            "all_orders": {
                "count": 120,
                "growth": 15.0 // Percentage change
            },
            "pending": {
                "count": 15,
                "growth": -5.0 // Percentage change
            },
            "processing": {
                "count": 25,
                "growth": 10.0 // Percentage change
            },
            "shipped": {
                "count": 30,
                "growth": 15.0 // Percentage change
            },
            "delivered": {
                "count": 90,
                "growth": 20.0 // Percentage change
            },
            "cancelled": {
                "count": 5,
                "growth": -2.0 // Percentage change
            },
            "returned": {
                "count": 3,
                "growth": 1.0 // Percentage change
            },
            "damaged": {
                "count": 2,
                "growth": 0.0 // Percentage change
            }
        },
        "period": "week",
        "last_updated": "2024-06-05T14:30:00Z" // Added by _enhance_overview_response
    }
    ```
*   **Error Response (401 Unauthorized):**
    ```json
    {
        "detail": "Authentication credentials were not provided."
    }
    ```
*   **Error Response (403 Forbidden):**
    ```json
    {
        "detail": "You do not have permission to perform this action."
    }
    ```

#### 2. Dashboard Summary (Alternative for Summary Cards)

Provides a consolidated summary of key metrics, can also be used for summary cards.

*   **UI Feature:** Summary cards at the top of the dashboard.
*   **Endpoint:** `GET /api/dashboard/dashboard_summary/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves a summary of dashboard metrics for a specified period.
*   **Query Parameters:**
    *   `period` (string, optional): Time period for metrics. Values: `day`, `week`, `month`, `year`. Default: `week`.
*   **Success Response (200 OK):**
    ```json
    {
        "summary": {
            "all_orders": {
                "count": 120,
                "label": "All Orders"
            },
            "pending_orders": {
                "count": 15,
                "label": "Pending"
            },
            "processing_orders": {
                "count": 25,
                "label": "Processing"
            },
            "shipped_orders": {
                "count": 30,
                "label": "Shipped"
            },
            "delivered_orders": {
                "count": 90,
                "label": "Delivered"
            },
            "cancelled_orders": {
                "count": 5,
                "label": "Cancelled"
            },
            "returned_orders": {
                "count": 3,
                "label": "Returned"
            },
            "damaged_orders": {
                "count": 2,
                "label": "Damaged"
            },
            "total_revenue": 15250.75
        },
        "period": "week",
        "last_updated": "2024-06-05T14:30:00Z"
    }
    ```
*   **Error Response (500 Internal Server Error - if data fetching fails):**
    ```json
    {
        "summary": {
            "all_orders": {"count": 0, "label": "All Orders"},
            "pending_orders": {"count": 0, "label": "Pending"},
            "processing_orders": {"count": 0, "label": "Processing"},
            "shipped_orders": {"count": 0, "label": "Shipped"},
            "delivered_orders": {"count": 0, "label": "Delivered"},
            "cancelled_orders": {"count": 0, "label": "Cancelled"},
            "returned_orders": {"count": 0, "label": "Returned"},
            "damaged_orders": {"count": 0, "label": "Damaged"},
            "total_revenue": 0
        },
        "period": "week",
        "error": "Failed to fetch summary data"
    }
    ```

#### 3. Sales Chart Data

Provides time-series data for generating sales charts (or other metric charts).

*   **UI Feature:** Sales line chart.
*   **Endpoint:** `GET /api/dashboard/summary-chart-data/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves data points for a specified metric over a given period, suitable for charts.
*   **Query Parameters:**
    *   `metric` (string, required): The metric to retrieve data for. Values: `sales`, `orders_count`, `new_customers_count`.
    *   `period` (string, optional): Time period for the chart. Values: `last_7_days`, `last_30_days`, `this_month`. Default: `last_7_days`.
*   **Success Response (200 OK) for `metric=sales` & `period=last_7_days`:**
    ```json
    {
        "chart_data": [
            {"date": "2024-05-30", "value": "1250.50"},
            {"date": "2024-05-31", "value": "1800.75"},
            {"date": "2024-06-01", "value": "950.00"},
            {"date": "2024-06-02", "value": "2100.25"},
            {"date": "2024-06-03", "value": "1750.00"},
            {"date": "2024-06-04", "value": "1900.50"},
            {"date": "2024-06-05", "value": "2200.00"}
        ],
        "metric_label": "Total Sales",
        "period_label": "Last 7 Days"
    }
    ```
*   **Error Response (400 Bad Request - Invalid Metric):**
    ```json
    {
        "error": "Invalid metric specified. Choose from 'sales', 'orders_count', 'new_customers_count'."
    }
    ```

#### 4. Recent Orders Table

Provides data for the table listing recent orders.

*   **UI Feature:** "Recent Orders" table.
*   **Endpoint:** `GET /api/dashboard/recent_orders/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves a list of the most recent orders for dashboard display.
*   **Query Parameters:**
    *   `limit` (integer, optional): Number of recent orders to fetch. Default: `6`.
*   **Success Response (200 OK):**
    ```json
    {
        "recent_orders": [
            {
                "id": 105,
                "order_number": "ORD-20240605-0105",
                "customer_name": "Alice Wonderland",
                "customer_email": "alice@example.com",
                "total": 121.00,
                "status": "DELIVERED", // Raw status from model
                "status_display": "Completed", // UI-friendly status
                "created_at": "2024-06-05T10:15:00Z", // ISO format
                "product_image": "https://res.cloudinary.com/.../chair.jpg", // URL of the first item's image
                "items_count": 1,
                "first_product_name": "Ergonomic Chair"
            },
            {
                "id": 104,
                "order_number": "ORD-20240604-0104",
                "customer_name": "Bob The Builder",
                "customer_email": "bob@example.com",
                "total": 590.00,
                "status": "PENDING",
                "status_display": "Pending",
                "created_at": "2024-06-04T16:30:00Z",
                "product_image": "https://res.cloudinary.com/.../table.jpg",
                "items_count": 2,
                "first_product_name": "Large Dining Table"
            }
            // ... more recent orders
        ],
        "total_count": 105 // Total orders in the system
    }
    ```
*   **Error Response (500 Internal Server Error - if data fetching fails):**
    ```json
    {
        "recent_orders": [],
        "total_count": 0,
        "error": "Failed to fetch recent orders"
    }
    ```

---
---

## Admin Dashboard - Order Management UI Endpoints

This section details the API endpoints supporting the Order Management section of the Admin Dashboard UI.

### 1. List and Filter Orders (Order Table)

This endpoint populates the main order table, supporting pagination, searching, and filtering by status tabs (All order, Processing, Delivered, Cancelled) and date range.

*   **UI Feature:** Main order listing table, search (implicitly, though not shown, usually part of admin tables), filter tabs, "Select Date" filter, pagination.
*   **Endpoint:** `GET /api/orders/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves a paginated list of orders, with filtering and search capabilities.
*   **Query Parameters:**
    *   `status` (string, optional): Filters orders by status. Values: `PENDING`, `PROCESSING`, `SHIPPED`, `DELIVERED`, `CANCELLED`.
    *   `created_at_after` (date string, `YYYY-MM-DD`, optional): Filters orders created on or after this date.
    *   `created_at_before` (date string, `YYYY-MM-DD`, optional): Filters orders created on or before this date.
    *   `search` (string, optional): Search term for order number, customer email, customer name.
    *   `ordering` (string, optional): Fields to order by, e.g., `created_at`, `-total`. Default: `-created_at`.
    *   `page` (integer, optional): Page number for pagination. Default: `1`.
    *   `page_size` (integer, optional): Number of items per page. Default: (as per global pagination settings).
*   **Success Response (200 OK):** (Based on `OrderSerializer`)
    ```json
    {
        "count": 100,
        "next": "http://api/orders/?page=2",
        "previous": null,
        "results": [
            {
                "id": 302012,
                "order_number": "ORD-20221229-0001", // Example format
                "customer_email": "john.bushmill@example.com",
                "customer_name": "John Bushmill",
                "items": [ // Typically includes details of the first item or a summary
                    {
                        "id": 1,
                        "product": 50,
                        "product_name": "Handmade Pouch",
                        "product_sku": "HMP-001",
                        "quantity": 1,
                        "unit_price": "121.00",
                        "total_price": "121.00",
                        "variants": {}, // Or details of selected variant
                        "product_image": "url/to/handmade_pouch.jpg"
                    }
                    // Potentially more items if the serializer is configured to return all
                ],
                "products_display_string": "Handmade Pouch +2 other products", // Generated by serializer
                "total": "121.00",
                "status": "PROCESSING",
                "status_display": "Processing",
                "payment": { // Details of the first payment
                    "id": 1,
                    "method": "Mastercard", // Or from payment_type on Order
                    "amount": "121.00",
                    "status": "PAID", // Payment status
                    "created_at": "2022-12-29T10:00:00Z"
                },
                "payments": [ /* ... full list of payments ... */ ],
                "shipping_address": "123 Main St, Anytown, USA",
                "created_at": "2022-12-29T10:00:00Z",
                "estimated_delivery_date": "Monday, January 02, 2023", // Calculated by serializer
                "updated_at": "2022-12-29T10:05:00Z",
                "note": "Customer requested gift wrap.",
                "payment_type": "CREDIT", // From Order model
                "order_type": "STANDARD",
                "order_date": "2022-12-29",
                "order_time": "10:00:00"
            }
            // ... more orders
        ]
    }
    ```
*   **Error Response (401 Unauthorized / 403 Forbidden):** Standard error responses.

### 2. Add New Order

This endpoint is used when the "Add Order" button is clicked.

*   **UI Feature:** "Add Order" button and the subsequent order creation form.
*   **Endpoint:** `POST /api/orders/` (or `POST /api/orders/create_order/` if using the dedicated action, or `POST /api/order-create/` if using `OrderCreateView`)
*   **Method:** `POST`
*   **Auth Required:** Yes (Admin)
*   **Description:** Creates a new order.
*   **Request Body (Payload):** (Based on `OrderCreateEnhancedSerializer` or `OrderCreateSerializer`)
    ```json
    {
        "customer_id": 12, // ID of an existing customer (optional, if not provided, links to request.user)
        "items": [
            {
                "product_id": 50,
                "quantity": 1,
                "price": "121.00" // Unit price for this item in this order
            },
            {
                "product_id": 52,
                "quantity": 2,
                "price": "50.00"
            }
        ],
        "payment_type": "CREDIT", // e.g., 'CASH', 'CREDIT', 'DEBIT', 'TRANSFER'
        "order_type": "STANDARD", // e.g., 'STANDARD', 'EXPRESS', 'PICKUP'
        "status": "PENDING", // Initial order status
        "order_date": "2024-06-05", // Optional, defaults to now
        "order_time": "14:30:00", // Optional, defaults to now
        "note": "Special instructions for delivery.",
        "shipping_address": "123 New Street",
        "shipping_city": "New City",
        "shipping_state": "New State",
        "shipping_country": "New Country",
        "shipping_zip": "12345",
        "billing_address": "123 New Street, New City, New State, 12345, New Country" // (Optional, can be same as shipping)
        // "payment_method": "Mastercard" // If using OrderCreateSerializer
    }
    ```
*   **Success Response (201 Created):** (Response from `OrderSerializer` after creation)
    ```json
    {
        "id": 302013,
        "order_number": "ORD-20240605-0106",
        "customer_email": "new.customer@example.com",
        "customer_name": "New Customer",
        "items": [ /* ... created order items ... */ ],
        "total": "221.00", // Calculated based on items, shipping, tax, discount
        "status": "PENDING",
        "status_display": "Pending",
        // ... other fields as in the GET /api/orders/ response
    }
    ```
*   **Error Response (400 Bad Request):**
    ```json
    {
        "items": ["This field is required.", "Order must have at least one item"],
        "shipping_address": ["This field may not be blank."]
        // ... other validation errors
    }
    ```

### 3. Edit Order

This endpoint is used when the "Edit" icon (pencil) in the order table is clicked.

*   **UI Feature:** "Edit" icon and subsequent order editing form.
*   **Endpoint:** `PUT /api/orders/<id>/` or `PATCH /api/orders/<id>/`
*   **Method:** `PUT` or `PATCH`
*   **Auth Required:** Yes (Admin)
*   **Description:** Updates an existing order.
*   **Request Body (Payload):** (Fields from `OrderSerializer` that are updatable, e.g., status, note, shipping details. Items might be managed via separate item endpoints or a more complex update).
    ```json
    {
        "status": "PROCESSING",
        "note": "Updated note: Customer called to confirm address.",
        "shipping_address": "456 Updated St, Updated City"
        // Potentially other fields like payment_status, items (if supported by update)
    }
    ```
*   **Success Response (200 OK):** (Updated order details, similar to `GET /api/orders/<id>/`)
    ```json
    {
        "id": 302012,
        "status": "PROCESSING",
        "status_display": "Processing",
        "note": "Updated note: Customer called to confirm address.",
        "shipping_address": "456 Updated St, Updated City",
        // ... other fields
    }
    ```
*   **Error Response (404 Not Found):**
    ```json
    { "detail": "Not found." }
    ```

### 4. View Order Details

This endpoint is used when the "View" icon (eye) in the order table is clicked.

*   **UI Feature:** "View" icon, leading to an order detail page/modal.
*   **Endpoint:** `GET /api/orders/<id>/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves details for a specific order.
*   **Success Response (200 OK):** (Detailed order information, same as the single order object in the list response)
    ```json
    {
        "id": 302012,
        "order_number": "ORD-20221229-0001",
        "customer_email": "john.bushmill@example.com",
        // ... all fields as shown in the list example for a single order
    }
    ```
*   **Error Response (404 Not Found):**
    ```json
    { "detail": "Not found." }
    ```

### 5. Delete Order

This endpoint is used when the "Delete" icon (trash can) in the order table is clicked.

*   **UI Feature:** "Delete" icon.
*   **Endpoint:** `DELETE /api/orders/<id>/`
*   **Method:** `DELETE`
*   **Auth Required:** Yes (Admin)
*   **Description:** Deletes a specific order.
*   **Success Response (204 No Content):** (No body)
*   **Error Response (404 Not Found):**
    ```json
    { "detail": "Not found." }
    ```

### 6. Export Orders

This endpoint is triggered by the "Export" button.

*   **UI Feature:** "Export" button.
*   **Endpoint:** `GET /api/orders/export/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Exports order data as a CSV file. Supports current filters applied to the list.
*   **Query Parameters:** (Same as List Orders: `status`, `created_at_after`, `created_at_before`, `search`)
*   **Success Response (200 OK):**
    *   Content-Type: `text/csv`
    *   Body: CSV formatted data of orders.
    ```csv
    Order ID,Date,Customer,Email,Items,Total,Status,Payment Method,Payment Status
    ORD-20221229-0001,2022-12-29 10:00,John Bushmill,john.bushmill@example.com,"Handmade Pouch (x1)",121.00,Processing,Mastercard,PAID
    ...
    ```

### 7. Bulk Order Actions

This endpoint handles actions like "Delete Selected" or changing status for multiple selected orders.

*   **UI Feature:** Checkboxes next to orders and a bulk action dropdown.
*   **Endpoint:** `POST /api/orders/bulk_action/`
*   **Method:** `POST`
*   **Auth Required:** Yes (Admin)
*   **Description:** Performs a bulk action (e.g., update status, delete) on selected orders.
*   **Request Body (Payload):**
    ```json
    {
        "order_ids": [302012, 302011],
        "action": "update_status", // or "delete"
        "status": "SHIPPED" // Required if action is "update_status"
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "status": "success",
        "processed": 2 // Number of orders affected
    }
    ```
*   **Error Response (400 Bad Request):**
    ```json
    {
        "error": "order_ids and action are required"
    }
    ```
    ```json
    {
        "error": "status is required for update_status action"
    }
    ```

### 8. Get Order Status Counts (for Filter Tabs)

This endpoint provides the counts for each order status tab.

*   **UI Feature:** Numerical counts next to filter tabs (All order, Processing, Delivered, Cancelled).
*   **Endpoint:** `GET /api/dashboard/order_metrics/` (Specifically the `status_summary` part of the response)
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves various order metrics, including counts for each status.
*   **Query Parameters:**
    *   `period` (string, optional): `day`, `week`, `month`, `year`. Default: `week`.
*   **Success Response (200 OK - relevant part):**
    ```json
    {
        // ... other metrics ...
        "status_summary": {
            "all": {"count": 100, "total_value": 12500.00, "avg_order_value": 125.00},
            "pending": {"count": 15, "total_value": 1500.00, "avg_order_value": 100.00},
            "processing": {"count": 25, "total_value": 3000.00, "avg_order_value": 120.00},
            "shipped": {"count": 30, "total_value": 4500.00, "avg_order_value": 150.00},
            "delivered": {"count": 20, "total_value": 2500.00, "avg_order_value": 125.00},
            "cancelled": {"count": 10, "total_value": 1000.00, "avg_order_value": 100.00}
        },
        // ... other metrics ...
    }
    ```

---
---

### Admin Dashboard - Order Management UI Endpoints (Continued)

#### 2. Add New Order (Detailed for "Create New Order" Modal)

This endpoint is used when the "Add Order" button is clicked, and the "Create New Order" modal is filled.

*   **UI Feature:** "Add Order" button and the "Create New Order" modal.
*   **Endpoint:** `POST /api/orders/` (or `POST /api/orders/create_order/` or `POST /api/order-create/`)
*   **Method:** `POST`
*   **Auth Required:** Yes (Admin)
*   **Description:** Creates a new order based on the details provided in the modal.
*   **Supporting Endpoints for Dropdowns/Search:**
    *   **Select Customer Dropdown:** Populate with `GET /api/orders/customers/` (See "List Customers for Order Form" below).
    *   **Payment Type, Order Type, Order Status Dropdowns:** Populate with `GET /api/order-choices/` (See "Get Order Form Choices" below).
    *   **Search Product Name (for Items):** Use `GET /api/product-search/?q={search_term}` (See "Search Products for Order Form" below).
*   **Request Body (Payload):** (Based on `OrderCreateEnhancedSerializer` or `OrderCreateSerializer`)
    ```json
    {
        "customer_id": 12, // ID of an existing customer (from GET /api/orders/customers/). If "New Customer" is toggled, create customer first or adapt payload if backend supports inline creation.
        "payment_type": "CREDIT", // Selected from GET /api/order-choices/
        "order_type": "STANDARD", // Selected from GET /api/order-choices/
        "order_date": "2020-12-12", // From date picker
        "order_time": "12:00:00", // From time picker
        "status": "PENDING", // Selected from GET /api/order-choices/
        "note": "Order note content here.",
        "items": [ // Array of products selected via search
            {
                "product_id": 50, // ID of the product
                "quantity": 1,
                "price": "121.00" // Unit price for this item at the time of order
            },
            {
                "product_id": 52,
                "quantity": 2,
                "price": "50.00"
            }
        ],
        "shipping_address": "123 New Street", // Required if physical products
        "shipping_city": "New City",
        "shipping_state": "New State",
        "shipping_country": "New Country",
        "shipping_zip": "12345",
        "billing_address": "123 New Street, New City, New State, 12345, New Country" // Optional
    }
    ```
*   **Success Response (201 Created):** (Response from `OrderSerializer` after creation)
    ```json
    {
        "id": 302013,
        "order_number": "ORD-20240605-0106",
        "customer_email": "selected.customer@example.com",
        "customer_name": "Selected Customer Name",
        "items": [ /* ... created order items ... */ ],
        "total": "221.00",
        "status": "PENDING",
        "status_display": "Pending",
        "payment_type": "CREDIT",
        "order_type": "STANDARD",
        "order_date": "2020-12-12",
        "order_time": "12:00:00",
        "note": "Order note content here.",
        // ... other fields as in the GET /api/orders/ response
    }
    ```
*   **Error Response (400 Bad Request):**
    ```json
    {
        "items": ["This field is required.", "Order must have at least one item"],
        "shipping_address": ["This field may not be blank."],
        "customer_id": ["Invalid pk \"null\" - object does not exist."] // If customer_id is missing or invalid
    }
    ```

#### Supporting Endpoints for "Create New Order" Modal:

##### 2a. List Customers for Order Form

*   **UI Feature:** Populating the "Select Customer" dropdown in the "Create New Order" modal.
*   **Endpoint:** `GET /api/orders/customers/` (Action within `OrderViewSet`)
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves a list of customers suitable for selection in an order form.
*   **Success Response (200 OK):** (Based on `CustomerSimpleSerializer` or `CustomerSerializer`)
    ```json
    [
        {
            "id": 12,
            "name": "John Bushmill",
            "email": "john.bushmill@example.com",
            "phone": "+1234567890",
            "display_name": "John Bushmill (john.bushmill@example.com)"
        },
        {
            "id": 15,
            "name": "Linda Blair",
            "email": "linda.blair@example.com",
            "phone": "+0987654321",
            "display_name": "Linda Blair (linda.blair@example.com)"
        }
        // ... more customers
    ]
    ```

##### 2b. Get Order Form Choices

*   **UI Feature:** Populating "Payment Type", "Order Type", and "Order Status" dropdowns in the "Create New Order" modal.
*   **Endpoint:** `GET /api/order-choices/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves choice options for various order fields.
*   **Success Response (200 OK):**
    ```json
    {
        "payment_types": [
            ["CASH", "Cash"],
            ["CREDIT", "Credit Card"],
            ["DEBIT", "Debit Card"],
            ["TRANSFER", "Bank Transfer"]
        ],
        "order_types": [
            ["STANDARD", "Standard"],
            ["EXPRESS", "Express"],
            ["PICKUP", "Pickup"]
        ],
        "status_choices": [
            ["PENDING", "Pending"],
            ["PROCESSING", "Processing"],
            ["SHIPPED", "Shipped"],
            ["DELIVERED", "Delivered"],
            ["CANCELLED", "Cancelled"]
            // ... other statuses
        ]
    }
    ```

##### 2c. Search Products for Order Form

*   **UI Feature:** "Search product name" input field within the "Items" section of the "Create New Order" modal.
*   **Endpoint:** `GET /api/product-search/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin, as it's for an admin creating an order)
*   **Description:** Searches for products to be added to an order.
*   **Query Parameters:**
    *   `q` (string, required): The search term for product name, SKU, or description. Minimum 2 characters.
*   **Success Response (200 OK):**
    ```json
    [ // Array of simplified product data
        {
            "id": 50,
            "name": "Handmade Pouch",
            "sku": "HMP-001",
            "price": "121.00",
            "stock_quantity": 15,
            "image": "url/to/handmade_pouch.jpg"
        },
        {
            "id": 52,
            "name": "Smartwatch E2",
            "sku": "SMW-E2-BLK",
            "price": "50.00", // Assuming this is the current price
            "stock_quantity": 30,
            "image": "url/to/smartwatch_e2.jpg"
        }
        // ... up to 10 results
    ]
    ```
*   **Success Response (200 OK - if query too short or no results):**
    ```json
    []
    ```

---
---

## Admin Dashboard - Customer Management UI Endpoints

This section details the API endpoints supporting the Customer Management section of the Admin Dashboard UI.

### 1. List and Filter Customers (Customer Grid)

This endpoint populates the main customer grid/card view, supporting pagination, searching, and filtering by status tabs (All, Active, Blocked).

*   **UI Feature:** Main customer grid, search bar ("Search customer..."), filter tabs (All, Active, Blocked), pagination.
*   **Endpoint:** `GET /api/customers/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves a paginated list of customers, with filtering and search capabilities.
*   **Query Parameters:**
    *   `status` (string, optional): Filters customers by status. Values: `active`, `blocked`. If omitted, returns all.
    *   `search` (string, optional): Search term for customer name, email, or phone.
    *   `ordering` (string, optional): Fields to order by, e.g., `created_at`, `name`, `orders_count`, `balance`. Default: `-created_at`.
    *   `page` (integer, optional): Page number for pagination. Default: `1`.
    *   `page_size` (integer, optional): Number of items per page. Default: (as per `CustomerPagination`, e.g., 10).
    *   `created_at_after` (date string, `YYYY-MM-DD`, optional): Filter by customer creation date.
    *   `created_at_before` (date string, `YYYY-MM-DD`, optional): Filter by customer creation date.
    *   `orders_count` (integer, optional): Filter by exact number of orders.
    *   `balance` (decimal, optional): Filter by exact total balance.
*   **Success Response (200 OK):** (Based on `CustomerSerializer`)
    ```json
    {
        "count": 100,
        "next": "http://api/customers/?page=2",
        "previous": null,
        "results": [
            {
                "id": 1,
                "name": "John Bushmill",
                "email": "john.bushmill@example.com",
                "phone": "+1234567890",
                "status": "active", // "active" or "blocked"
                "orders_count": 12, // Example value
                "balance": "12091.00", // Example value
                "created_at": "2023-10-26T10:00:00Z"
            },
            {
                "id": 2,
                "name": "Laura Prichet",
                "email": "laura.prichet@example.com",
                "phone": "+0987654321",
                "status": "blocked",
                "orders_count": 5,
                "balance": "5500.50",
                "created_at": "2023-11-15T14:30:00Z"
            }
            // ... more customers
        ]
    }
    ```
*   **Error Response (401 Unauthorized / 403 Forbidden):** Standard error responses.

### 2. Add New Customer

This endpoint is used when the "Add Customer" button is clicked.

*   **UI Feature:** "Add Customer" button and the subsequent customer creation form/modal.
*   **Endpoint:** `POST /api/customers/` (or `POST /api/customers/add_customer/`)
*   **Method:** `POST`
*   **Auth Required:** Yes (Admin)
*   **Description:** Creates a new customer.
*   **Request Body (Payload):** (Based on `CustomerCreateSerializer`)
    ```json
    {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "country_code": "+1", // Optional
        "local_phone_number": "5551234567", // Optional
        "password": "secureNewPassword123", // Optional, if creating a user account for the customer
        "create_user_account": true, // Boolean, defaults to false. If true and password provided, a CustomUser is created.
        "address": { // Optional, AddressSerializer fields
            "full_name": "Jane Doe",
            "email": "jane.doe@example.com",
            "phone_number": "+15551234567",
            "street_address": "123 Oak St",
            "city": "Anytown",
            "state": "CA",
            "country": "USA",
            "zip_code": "90210",
            "is_default": true
        }
    }
    ```
*   **Success Response (201 Created):** (Based on `CustomerCreateSerializer` which might return limited fields, or `CustomerDetailSerializer` if the view returns the full object)
    ```json
    {
        // Response from CustomerCreateSerializer might be simpler,
        // but a GET after create would use CustomerDetailSerializer.
        // Assuming response from CustomerDetailSerializer for consistency:
        "id": 3,
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "phone": "+15551234567", // Formatted by model's save method
        "status": "active",
        "orders_count": 0,
        "balance": "0.00",
        "created_at": "2024-06-05T15:00:00Z",
        "recent_orders": []
    }
    ```
*   **Error Response (400 Bad Request):**
    ```json
    {
        "email": ["customer with this email already exists."],
        "local_phone_number": ["Phone number is required when country code is provided."]
    }
    ```

### 3. View Customer Details

This endpoint is used when an admin wants to see more details about a specific customer (e.g., by clicking on a customer card or a "View" action from the three-dot menu).

*   **UI Feature:** Clicking a customer card or a "View" action from the three-dot menu.
*   **Endpoint:** `GET /api/customers/<id>/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves detailed information for a specific customer.
*   **Success Response (200 OK):** (Based on `CustomerDetailSerializer`)
    ```json
    {
        "id": 1,
        "name": "John Bushmill",
        "email": "john.bushmill@example.com",
        "phone": "+1234567890",
        "status": "active",
        "orders_count": 12,
        "balance": "12091.00",
        "created_at": "2023-10-26T10:00:00Z",
        "recent_orders": [ // Example, list of recent orders
            {
                "id": 101,
                "order_number": "ORD-20240101-001",
                "total": "150.00",
                "status": "DELIVERED",
                // ... other order fields from OrderSerializer
            }
        ]
    }
    ```
*   **Error Response (404 Not Found):**
    ```json
    { "detail": "Not found." }
    ```

### 4. Edit Customer

This endpoint is used when an admin edits an existing customer's details (e.g., via an "Edit" action from the three-dot menu).

*   **UI Feature:** "Edit" action from the three-dot menu, leading to an edit form/modal.
*   **Endpoint:** `PUT /api/customers/<id>/` or `PATCH /api/customers/<id>/`
*   **Method:** `PUT` or `PATCH`
*   **Auth Required:** Yes (Admin)
*   **Description:** Updates an existing customer's details.
*   **Request Body (Payload):** (Fields from `CustomerDetailSerializer` or a specific update serializer)
    ```json
    {
        "name": "John B. Bushmill",
        "phone": "+1234567899" // Note: if sending country_code and local_phone_number, use those instead.
        // "status": "blocked" // To change status, usually done via bulk_action or a dedicated status update endpoint.
    }
    ```
*   **Success Response (200 OK):** (Updated customer details, based on `CustomerDetailSerializer`)
    ```json
    {
        "id": 1,
        "name": "John B. Bushmill",
        "email": "john.bushmill@example.com",
        "phone": "+1234567899",
        "status": "active",
        // ... other fields
    }
    ```
*   **Error Response (404 Not Found):**
    ```json
    { "detail": "Not found." }
    ```

### 5. Delete Customer

This endpoint is used when an admin deletes a customer (e.g., via a "Delete" action from the three-dot menu).

*   **UI Feature:** "Delete" action from the three-dot menu.
*   **Endpoint:** `DELETE /api/customers/<id>/`
*   **Method:** `DELETE`
*   **Auth Required:** Yes (Admin)
*   **Description:** Deletes a specific customer (and their associated user account if one exists).
*   **Success Response (204 No Content):** (No body)
*   **Error Response (404 Not Found):**
    ```json
    { "detail": "Not found." }
    ```

### 6. Export Customers

This endpoint is triggered by the "Export" button on the customer list page.

*   **UI Feature:** "Export" button.
*   **Endpoint:** `GET /api/customers/export/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Exports customer data as a CSV file. Supports current filters applied to the list.
*   **Query Parameters:** (Same as List Customers: `status`, `search`, `created_at_after`, etc.)
*   **Success Response (200 OK):**
    *   Content-Type: `text/csv`
    *   Body: CSV formatted data of customers.
    ```csv
    ID,Name,Email,Phone,Status,Orders,Total Balance,Created
    1,John Bushmill,john.bushmill@example.com,+1234567890,Active,12,$12091.00,2023-10-26
    ...
    ```

### 7. Bulk Customer Actions

This endpoint handles actions like "Delete Selected" or changing status for multiple selected customers.

*   **UI Feature:** Checkboxes on customer cards and a bulk action dropdown.
*   **Endpoint:** `POST /api/customers/bulk_action/`
*   **Method:** `POST`
*   **Auth Required:** Yes (Admin)
*   **Description:** Performs a bulk action (e.g., update status, delete) on selected customers.
*   **Request Body (Payload):**
    ```json
    {
        "customer_ids": [1, 2, 5], // Array of customer IDs
        "action": "update_status", // "update_status" or "delete"
        "status": "blocked", // Required if action is "update_status"; "active" or "blocked"
        "select_all": false, // Optional: if true, applies to all customers matching current filters
        "exclude_ids": [] // Optional: if select_all is true, IDs to exclude from the bulk action
    }
    ```
*   **Success Response (200 OK):**
    ```json
    {
        "status": "success",
        "affected": 3 // Number of customers affected
    }
    ```
*   **Error Response (400 Bad Request):**
    ```json
    {
        "error": "No customers selected"
    }
    ```
    ```json
    {
        "error": "Invalid status" // If status for update_status is not 'active' or 'blocked'
    }
    ```

### 8. Get Customer Statistics (for Detail View)

This endpoint provides detailed statistics for a single customer, often shown on a customer detail page.

*   **UI Feature:** Could be part of a customer detail view accessed via the "View" action.
*   **Endpoint:** `GET /api/customers/<id>/statistics/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves statistics for a specific customer.
*   **Success Response (200 OK):**
    ```json
    {
        "total_orders": 12,
        "total_spent": "12091.00",
        "monthly_orders": 3, // Orders in the current month
        "avg_order_value": "1007.58",
        "abandoned_carts_count": 1,
        "order_status_counts": {
            "pending": 1,
            "processing": 2,
            "shipped": 3,
            "completed": 5, // 'DELIVERED' status
            "cancelled": 1,
            "returned": 0,
            "damaged": 0
        },
        "recent_orders": [ // Array of simplified order objects (from OrderSerializer)
            {
                "id": 101,
                "order_number": "ORD-20240101-001",
                "total": "150.00",
                "status": "DELIVERED",
                // ... other relevant order fields
            }
        ]
    }
    ```
*   **Error Response (404 Not Found):**
    ```json
    { "detail": "Not found." }
    ```

---
---

#### Admin Dashboard - Customer Detail View UI Endpoints

This section details API endpoints supporting the "Customer Details" page within the Admin Dashboard.

##### 1. Get Customer Details (Main Info Panel)

*   **UI Feature:** Left panel displaying customer's avatar, name, status, ID, email, address, phone, last transaction, and last online.
*   **Endpoint:** `GET /api/customers/<id>/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves detailed information for a specific customer.
*   **Success Response (200 OK):** (Based on `CustomerDetailSerializer`, potentially needing to ensure `profile.photo.url`, default `Address`, and `user.last_login` are included)
    ```json
    {
        "id": 1, // Customer ID (e.g., ID-011221 in UI is likely derived from this)
        "name": "Linda Blair",
        "email": "lindablair@mail.com",
        "phone": "050 414 8778", // Formatted phone
        "status": "active", // Derived from user.is_active
        "orders_count": 10, // From annotation
        "balance": "12091.00", // From annotation
        "created_at": "2023-01-15T10:00:00Z",
        "user_details": { // Assuming user details are nested or part of profile
            "last_login": "2024-06-04T12:00:00Z", // For "Last Online"
            "profile_photo_url": "url/to/linda_blair_avatar.jpg" // If available
        },
        "default_address": { // Assuming default address is included
            "street_address": "1833 Bel Meadow Drive",
            "city": "Fontana",
            "state": "California",
            "zip_code": "92335",
            "country": "USA"
        },
        "recent_orders": [ /* ... from CustomerDetailSerializer ... */ ]
        // "last_transaction_date": "2022-12-12" // This would be derived from recent_orders or a dedicated field
    }
    ```
    *Note: "Last Transaction" date would typically be the `created_at` of the most recent order from the `recent_orders` list (available via `GET /api/customers/<id>/statistics/`) or by fetching the customer's latest order.*

*   **Error Response (404 Not Found):**
    ```json
    { "detail": "Not found." }
    ```

##### 2. Get Customer Statistics (Summary Cards)

*   **UI Feature:** Summary cards for Total Orders, Abandoned Cart, and order counts by status (All Orders, Pending, Completed, Canceled, Returned, Damaged). The UI shows an "All-time" filter.
*   **Endpoint:** `GET /api/customers/<id>/statistics/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves lifetime statistics for a specific customer, including order counts by status and abandoned cart information.
    *(Note: This endpoint currently provides "All-time" statistics. If per-period filtering (e.g., "Last 30 days") is needed for these cards on the customer detail page, this endpoint would require modification to accept a `period` parameter.)*
*   **Success Response (200 OK):**
    ```json
    {
        "total_orders": 25, // Maps to "Total Orders" card (UI shows 25,00.00 - likely a display format issue)
        "total_spent": "12091.00", // Could be displayed if needed
        "monthly_orders": 3, // Example: orders in the current month
        "avg_order_value": "483.64",
        "abandoned_carts_count": 2, // Maps to "Abandoned Cart" card
        "order_status_counts": { // Maps to "All Orders", "Pending", "Completed", etc. cards
            "pending": 2,
            "processing": 0, // Example
            "shipped": 0,    // Example
            "completed": 8,  // 'DELIVERED' status from backend maps to "Completed"
            "cancelled": 0,
            "returned": 0,
            "damaged": 0
            // Note: "All Orders" count for the card can be derived from summing these, or is `total_orders`.
        },
        "recent_orders": [ /* ... list of recent order objects ... */ ]
    }
    ```
*   **Error Response (404 Not Found):**
    ```json
    { "detail": "Not found." } // If the customer ID is invalid
    ```

##### 3. Get Customer Transaction History (Order List)

*   **UI Feature:** "Transaction History" table listing the customer's orders.
*   **Endpoint:** `GET /api/orders/`
*   **Method:** `GET`
*   **Auth Required:** Yes (Admin)
*   **Description:** Retrieves a paginated list of orders, filtered for the specific customer.
*   **Query Parameters:**
    *   `user_id` (integer, required): The ID of the user associated with the customer. (Or `customer_id=<customer_id>` if your `OrderFilter` supports direct filtering by `customer` foreign key).
    *   `created_at_after` (date string, `YYYY-MM-DD`, optional): For "Select Date" filter.
    *   `created_at_before` (date string, `YYYY-MM-DD`, optional): For "Select Date" filter.
    *   `status` (string, optional): For further filtering by status if the "Filters" button provides this.
    *   `page` (integer, optional): Page number.
    *   `page_size` (integer, optional): Items per page.
    *   `ordering` (string, optional): e.g., `-created_at`.
*   **Success Response (200 OK):** (Based on `OrderSerializer`, same structure as the main order list but filtered)
    ```json
    {
        "count": 10, // Total orders for this customer matching filters
        "next": "...",
        "previous": null,
        "results": [
            {
                "id": 302002,
                "order_number": "ORD-20231212-0001",
                "customer_name": "Linda Blair", // Should be redundant if already on customer page
                "customer_email": "lindablair@mail.com",
                "products_display_string": "Handmade Pouch +3 other products",
                "total": "121.00",
                "status": "PROCESSING",
                "status_display": "Processing",
                "created_at": "2023-12-12T00:00:00Z", // Used for "Date" column
                "payment": { "method": "Mastercard", /* ... */ }
                // ... other fields from OrderSerializer
            },
            {
                "id": 301901,
                "order_number": "ORD-20231201-0002",
                "products_display_string": "Smartwatch E2 +1 other products",
                "total": "590.00",
                "status": "PROCESSING",
                "status_display": "Processing",
                "created_at": "2023-12-01T00:00:00Z",
                "payment": { "method": "Visa", /* ... */ }
            }
            // ... more orders for this customer
        ]
    }
    ```

---

## Customer Management API Documentation
# Base URL
/api/customers/
Authentication
All endpoints require authentication with IsAdminUser permission class.
Include in headers: Authorization: Bearer <your-token>

📋 Customer Endpoints
1. List All Customers
GET /api/customers/
Query Parameters:

page (int): Page number for pagination
page_size (int): Items per page (max: 100, default: 10)
search (string): Search in name, email, phone
status (string): Filter by 'active' or 'blocked'
ordering (string): Sort by fields (created_at, name, orders_count, balance)
created_at_after (date): Filter created after date (YYYY-MM-DD)
created_at_before (date): Filter created before date (YYYY-MM-DD)

Response:
json{
  "count": 150,
  "next": "http://api/customers/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+2348123456789",
      "status": "active",
      "orders_count": 5,
      "balance": "1250.00",
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
2. Create New Customer
POST /api/customers/
Request Body:
json{
  "name": "Jane Smith",
  "email": "jane@example.com",
  "country_code": "+234",
  "local_phone_number": "8123456789",
  "create_user_account": true,
  "password": "securepassword123",
  "address": {
    "full_name": "Jane Smith",
    "email": "jane@example.com",
    "phone_number": "+2348123456789",
    "street_address": "123 Main Street",
    "city": "Lagos",
    "state": "Lagos",
    "country": "Nigeria",
    "zip_code": "100001",
    "is_default": true
  }
}
Response (Success):
json{
  "id": 2,
  "name": "Jane Smith",
  "email": "jane@example.com",
  "phone": "+2348123456789",
  "created_at": "2024-01-15T10:30:00Z"
}
Response (Error):
json{
  "name": ["This field is required."],
  "email": ["Enter a valid email address."],
  "phone_number": ["Please enter a valid phone number"]
}
3. Get Customer Details
GET /api/customers/{id}/
Response:
json{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+2348123456789",
  "status": "active",
  "orders_count": 5,
  "balance": "1250.00",
  "created_at": "2024-01-15T10:30:00Z",
  "recent_orders": [
    {
      "id": 101,
      "order_number": "ORD-20240115-0001",
      "status": "DELIVERED",
      "total": "250.00",
      "created_at": "2024-01-10T14:30:00Z"
    }
  ]
}
4. Update Customer
PUT/PATCH /api/customers/{id}/
Request Body:
json{
  "name": "John Smith",
  "email": "johnsmith@example.com",
  "country_code": "+234",
  "local_phone_number": "8123456790"
}
5. Delete Customer
DELETE /api/customers/{id}/
Response:
json{
  "detail": "Customer deleted successfully"
}

📊 Customer Statistics
GET /api/customers/{id}/statistics/
Response:
json{
  "total_orders": 5,
  "total_spent": "1250.00",
  "monthly_orders": 2,
  "avg_order_value": "250.00",
  "abandoned_carts_count": 1,
  "order_status_counts": {
    "pending": 1,
    "processing": 0,
    "shipped": 0,
    "completed": 3,
    "cancelled": 1,
    "returned": 0,
    "damaged": 0
  },
  "recent_orders": [...]
}

🔄 Bulk Operations
POST /api/customers/bulk_action/
Bulk Status Update
json{
  "action": "update_status",
  "status": "blocked",
  "customer_ids": [1, 2, 3]
}
Bulk Delete
json{
  "action": "delete",
  "customer_ids": [1, 2, 3]
}
Select All with Exclusions
json{
  "action": "update_status",
  "status": "active",
  "select_all": true,
  "exclude_ids": [5, 6]
}
Response:
json{
  "status": "success",
  "affected": 3
}

📤 Export Customers
GET /api/customers/export/
Query Parameters: Same as list endpoint for filtering
Response: CSV file download with headers:
ID,Name,Email,Phone,Status,Orders,Total Balance,Created

🏠 Address Management
List Customer Addresses
GET /api/addresses/
Response:
json[
  {
    "id": 1,
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone_number": "+2348123456789",
    "street_address": "123 Main Street",
    "city": "Lagos",
    "state": "Lagos",
    "country": "Nigeria",
    "zip_code": "100001",
    "is_default": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
Create Address
POST /api/addresses/
Request Body:
json{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone_number": "+2348123456789",
  "street_address": "456 Second Street",
  "city": "Abuja",
  "state": "FCT",
  "country": "Nigeria",
  "zip_code": "900001",
  "is_default": false
}
Update Address
PUT/PATCH /api/addresses/{id}/
Delete Address
DELETE /api/addresses/{id}/
Set Default Address
POST /api/addresses/{id}/set_default/

📱 Profile Management
Get User Profile
GET /api/profiles/
Update Profile
PUT/PATCH /api/profiles/{id}/
Update User Details
PATCH /api/profiles/update-details/
Request Body:
json{
  "full_name": "John Smith",
  "email": "john.smith@example.com",
  "phone_number": "8123456789",
  "country_code": "+234"
}
Upload Profile Photo
POST /api/profiles/upload_photo/
Request: Form data with photo file
Remove Profile Photo
DELETE /api/profiles/remove_photo/

🚨 Error Response Format
All endpoints return consistent error responses:
json{
  "status": "error",
  "success": false,
  "message": "Validation error",
  "errors": {
    "field_name": "Error message"
  }
}
✅ Success Response Format
json{
  "status": "success", 
  "success": true,
  "message": "Operation completed successfully",
  "data": { ... }
}

🔍 Search & Filter Examples
Search customers by name or email:
GET /api/customers/?search=john
Filter by status and date range:
GET /api/customers/?status=active&created_at_after=2024-01-01
Sort by balance descending:
GET /api/customers/?ordering=-balance
Combined filters:
GET /api/customers/?search=gmail&status=active&ordering=-created_at&page_size=25

📝 Field Validation Rules
Customer Creation:

name: Required, max 255 characters
email: Required, valid email format, must be unique
country_code: Optional, must start with '+', max 5 characters
local_phone_number: Optional, max 20 characters
password: Optional, required only if create_user_account is true

Phone Number:

Country code and local number are validated together
Both must be provided if either is provided
Formatted phone number is auto-generated

Address:

All address fields are validated for presence and format
Email format validation
Phone number format validation
Zip code cannot be empty and max 20 characters


## Customer Management API Documentation
# Overview
This documentation covers all API endpoints for customer management in your system, based on the provided backend code and UI requirements.
Authentication
All endpoints require authentication unless specified otherwise.

Header: Authorization: Bearer <token>
Permission: Admin users only for customer management endpoints


Customer Endpoints
1. List Customers
GET /api/customers/
Description: Retrieve a paginated list of customers with filtering and search capabilities.
Query Parameters:
page=1                    # Page number
page_size=10             # Items per page (max 100)
search=john              # Search by name, email, or phone
status=active            # Filter by status: active, blocked
created_at_after=2024-01-01    # Filter by creation date
created_at_before=2024-12-31   # Filter by creation date
ordering=-created_at     # Sort by: created_at, name, orders_count, balance
Response:
json{
  "count": 150,
  "next": "http://api/customers/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+1234567890",
      "status": "active",
      "orders_count": 5,
      "balance": 1250.00,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ]
}
2. Create Customer
POST /api/customers/
Description: Create a new customer with optional user account and address.
Request Body:
json{
  "name": "John Doe",
  "email": "john@example.com",
  "country_code": "+1",
  "local_phone_number": "2345678901",
  "create_user_account": true,
  "password": "securepassword123",
  "address": {
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone_number": "+12345678901",
    "street_address": "123 Main St, Apt 4B",
    "city": "New York",
    "state": "NY",
    "country": "United States",
    "zip_code": "10001",
    "is_default": true
  }
}
Response:
json{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+12345678901",
  "country_code": "+1",
  "local_phone_number": "2345678901",
  "created_at": "2024-01-15T10:30:00Z"
}
3. Get Customer Details
GET /api/customers/{id}/
Description: Retrieve detailed information about a specific customer.
Response:
json{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+12345678901",
  "status": "active",
  "orders_count": 5,
  "balance": 1250.00,
  "created_at": "2024-01-15T10:30:00Z",
  "recent_orders": [
    {
      "id": 101,
      "order_number": "ORD-20240115-0001",
      "status": "DELIVERED",
      "total": 299.99,
      "created_at": "2024-01-10T14:20:00Z"
    }
  ]
}
4. Update Customer
PUT/PATCH /api/customers/{id}/
Description: Update customer information.
Request Body (PATCH example):
json{
  "name": "John Smith",
  "phone": "+12345678902"
}
5. Delete Customer
DELETE /api/customers/{id}/
Description: Delete a customer and optionally their user account.
Response:
json{
  "status": "success",
  "message": "Customer deleted successfully"
}
6. Customer Statistics
GET /api/customers/{id}/statistics/
Description: Get detailed statistics for a specific customer.
Response:
json{
  "total_orders": 5,
  "total_spent": 1250.00,
  "monthly_orders": 2,
  "avg_order_value": 250.00,
  "abandoned_carts_count": 1,
  "order_status_counts": {
    "pending": 1,
    "processing": 0,
    "shipped": 0,
    "completed": 3,
    "cancelled": 1,
    "returned": 0,
    "damaged": 0
  },
  "recent_orders": [...]
}
7. Bulk Actions
POST /api/customers/bulk_action/
Description: Perform bulk operations on multiple customers.
Request Body:
json{
  "action": "update_status",
  "customer_ids": [1, 2, 3],
  "status": "blocked"
}
Alternative for select all:
json{
  "action": "delete",
  "select_all": true,
  "exclude_ids": [5, 10]
}
Available Actions:

update_status: Change customer status (active/blocked)
delete: Remove customers

8. Export Customers
GET /api/customers/export/
Description: Export customer data as CSV file.
Query Parameters: Same as list endpoint for filtering
Response: CSV file download

Address Management Endpoints
1. List Customer Addresses
GET /api/addresses/
Description: Get addresses for the authenticated user.
Response:
json[
  {
    "id": 1,
    "full_name": "John Doe",
    "email": "john@example.com",
    "phone_number": "+12345678901",
    "street_address": "123 Main St, Apt 4B",
    "city": "New York",
    "state": "NY",
    "country": "United States",
    "zip_code": "10001",
    "is_default": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  }
]
2. Create Address
POST /api/addresses/
Request Body:
json{
  "full_name": "John Doe",
  "email": "john@example.com",
  "phone_number": "+12345678901",
  "street_address": "456 Oak Street",
  "city": "Boston",
  "state": "MA",
  "country": "United States",
  "zip_code": "02101",
  "is_default": false
}
3. Update Address
PUT/PATCH /api/addresses/{id}/
4. Delete Address
DELETE /api/addresses/{id}/
5. Set Default Address
POST /api/addresses/{id}/set_default/

Profile Management Endpoints
1. Get Profile
GET /api/profile/
2. Update Profile
PUT/PATCH /api/profile/{id}/
3. Upload Profile Photo
POST /api/profile/upload_photo/
4. Remove Profile Photo
DELETE /api/profile/remove_photo/
5. Update User Details
PATCH /api/profile/update-details/

Missing Backend Features for UI
1. Customer Address Integration
Your current Customer model doesn't have direct address fields. You need to either:
Option A: Add address fields to Customer model:
pythonclass Customer(models.Model):
    # ... existing fields ...
    street_address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    billing_same_as_shipping = models.BooleanField(default=True)
    billing_address = models.TextField(blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)
    billing_zip_code = models.CharField(max_length=20, blank=True)
Option B: Create relationship to existing Address model:
pythonclass Customer(models.Model):
    # ... existing fields ...
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='shipping_customers')
    billing_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='billing_customers')
2. Enhanced Customer Creation API
Update CustomerCreateSerializer to handle the address fields from your UI form.
3. Country/State Lists API
Consider adding endpoints for:

GET /api/countries/ - List of countries
GET /api/countries/{country_code}/states/ - States for a country

Error Handling
All endpoints return errors in this format:
json{
  "status": "error",
  "success": false,
  "message": "Validation error",
  "errors": {
    "email": "This email is already in use.",
    "phone_number": "Please enter a valid phone number"
  }
}
Success Responses
Success responses follow this format:
json{
  "status": "success",
  "success": true,
  "message": "Customer created successfully",
  "data": { ... }
}