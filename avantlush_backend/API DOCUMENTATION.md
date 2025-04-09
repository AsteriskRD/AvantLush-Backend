AvantLush API Documentation
Base URL
Production: https://avantlush-backend-2s6k.onrender.com/api/
Development: http://localhost:8000/api/
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