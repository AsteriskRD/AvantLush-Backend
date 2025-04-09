# Avantlush API Documentation

## Base URL
Production: https://avantlush-backend-2s6k.onrender.com
Development: `http://localhost:8000/api/`

## Authentication
All authenticated endpoints require JWT token:
```bash
Authorization: Bearer <your_jwt_token>
In Development stage for now, all authenticated endpoints are open for testing purposes.

1. Authentication Endpoints
Waitlist Signup
URL: /waitlist/signup/
Method: POST
Rate Limit: 5 requests per minute
Body:
{
    "email": "user@example.com"
}

Success Response (201):
{
    "success": true,
    "message": "Successfully added to waitlist",
    "email": "user@example.com",
    "statusCode": 201
}

Error Response (409):
{
    "success": false,
    "message": "Waitlist entry with this email already exists",
    "email": "user@example.com",
    "statusCode": 409
}

### Registration
- **URL**: `/register/`
- **Method**: POST
- **Body**:
```json
{
    "email": "user@example.com",
    "password": "securepassword123",
    "location": "Nigeria"
}

Success Response (201):
{
    "success": true,
    "message": "Registration successful. Please check your email to verify your account.",
    "email": "user@example.com",
    "id": "uuid-string",
    "location": "Nigeria"
}

Error Response (400):
{
    "success": false,
    "message": "Invalid data",
    "errors": {
        "email": ["User with this email address already exists."],
        "password": ["Password must be at least 8 characters long."]
    }
}

Login
URL: /login/
Method: POST
Body:
{
    "email": "user@example.com",
    "password": "securepassword123"
}

Success Response (200):
{
    "success": true,
    "token": "your-jwt-token",
    "id": 1,
    "email": "user@example.com",
    "message": "Login successful"
}

Error Response (401):
{
    "success": false,
    "message": "Invalid credentials"
}

### Google Authentication
- **URL**: `/auth/google/`
- **Method**: POST
- **Body**:
```json
{
    "token": "google-oauth-token",
    "email": "user@gmail.com",
    "location": "Nigeria"
}

Success Response (200):
{
    "token": "jwt-token",
    "email": "user@gmail.com",
    "location": "Nigeria"
}

Error Response (400):
{
    "error": "Invalid token"
}

Apple Authentication
URL: /auth/apple/
Method: POST
Body:
{
    "token": "apple-oauth-token",
    "code": "authorization-code",
    "id_token": "identity-token"
}

Success Response (200):
{
    "user_id": 1,
    "email": "user@example.com",
    "message": "Successfully authenticated with Apple"
}

Error Response (400):
{
    "error": "Email verification failed"
}

### Password Reset Flow

#### Request Password Reset
- **URL**: `/forgot-password/`
- **Method**: POST
- **Body**:
```json
{
    "email": "user@example.com"
}

Success Response (200):
{
    "success": true,
    "message": "Password reset instructions have been sent to your email. Please check both your inbox and spam folder."
}

Error Response (404):
{
    "success": false,
    "message": "Your account does not exist"
}


Reset Password
URL: /reset-password/<uidb64>/<token>/
Method: POST
Body:
{
    "password": "newSecurePassword123"
}

Reset Password
URL: /reset-password/<uidb64>/<token>/
Method: POST
Body:
{
    "password": "newSecurePassword123"
}

Success Response (200):
{
    "success": true,
    "message": "Password reset successful",
    "token": "new-jwt-token"
}

Error Response (400):
{
    "success": false,
    "message": "Reset link has expired",
    "errors": {
        "password": ["Password must contain at least 8 characters"]
    }
}

### Email Verification

#### Verify Email
- **URL**: `/verify-email/<uidb64>/<token>/`
- **Method**: GET
- **Success Response (200)**:
```json
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
Body:
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


## Product Management

### List Products
- **URL**: `/products/`
- **Method**: GET
- **Auth**: Optional
- **Query Parameters**:
  - `search`: Search term
  - `category`: Filter by category ID
  - `min_price`: Minimum price
  - `max_price`: Maximum price
  - `in_stock`: true/false
  - `ordering`: price, -price, name, -name, created_at, -created_at
  - `page`: Page number (default: 1)
  - `page_size`: Items per page (default: 12)

- **Success Response (200)**:
```json
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
            "stock_quantity": 50,
            "is_featured": true,
            "sku": "PRD001",
            "status": "active",
            "rating": "4.50",
            "num_ratings": 10,
            "created_at": "2024-01-20T10:30:00Z",
            "updated_at": "2024-01-20T10:30:00Z"
        }
    ]
}


### Product Search
- **URL**: `/products/search/`
- **Method**: GET
- **Query Parameters**:
  - `search`: Search in name, description, SKU, tags, categories
  - `category`: Filter by category
  - `tags`: Filter by tags
  - `is_featured`: true/false
  - `status`: active/inactive/out_of_stock
  - `page`: Page number

- **Success Response (200)**:
```json
{
    "count": 50,
    "results": [
        {
            "id": 1,
            "name": "Product Name",
            "slug": "product-name",
            "description": "Product description",
            "price": "99.99",
            "category_name": "Category Name",
            "images": ["url1"],
            "stock_quantity": 50,
            "status": "active",
            "rating": "4.50"
        }
    ]
}


Featured Products
URL: /products/featured/
Method: GET
Success Response (200):
[
    {
        "id": 1,
        "name": "Featured Product",
        "price": "149.99",
        "images": ["url1"],
        "is_featured": true,
        "rating": "4.80"
    }
]

Product Recommendations
URL: /products/{product_id}/recommendations/
Method: GET
Success Response (200):
[
    {
        "id": 1,
        "product": 1,
        "recommended_product": {
            "id": 2,
            "name": "Recommended Product",
            "price": "79.99",
            "images": ["url1"]
        },
        "score": 0.85
    }
]

## Cart Management

### Get Cart Summary
- **URL**: `/cart/summary/`   (IMAGES NEEDED TO BE IMPLEMENTED)
- **Method**: GET
- **Auth**: Required
- **Success Response (200)**:
```json
{
    "items": [
        {
            "id": 1,
            "product": 1,
            "product_name": "Product Name",
            "product_price": "99.99",
            "quantity": 2,
            "stock_status": "active"
        }
    ],
    "subtotal": "199.98",
    "shipping": "4.99",
    "total": "204.97",
    "item_count": 1
}


Add Item to Cart
URL: /cart/add-item/   (IMAGES NEEDED TO BE IMPLEMENTED)

Method: POST
Auth: Required
Body:
{
  "product": 1,
  "quantity": 2
}

Success Response (200):
{
    "id": 1,
    "product": 1,
    "product_name": "Product Name",
    "product_price": "99.99",
    "quantity": 2,
    "stock_status": "active"
}

Error Response (400):
{
    "error": "Not enough stock available"
}

### Update Cart Item Quantity
- **URL**: `/cart/update-quantity/`
- **Method**: POST
- **Auth**: Required
- **Body**:
```json
{
  "item_id": 4,
  "quantity": 3
}

{
    "status": "success"
}


Error Response (400):
{
    "error": "Not enough stock available"
}

Remove Item from Cart
URL: /cart/remove-item/
Method: POST
Auth: Required
Body:
{
    "item_id": 1
}

Success Response (200):
{
    "status": "success"
}

Error Response (404):
{
    "error": "Cart item not found"
}

Copy

Apply

Clear Cart
URL: /cart/clear/
Method: POST
Auth: Required
Success Response (200):
{
    "status": "success"
}

Apply Discount
URL: /cart/apply-discount/
Method: POST
Auth: Required
Body:
{
    "code": "WELCOME20"
}

Success Response (200):
{
    "status": "success",
    "discount": "10.00",
    "message": "Discount applied successfully"
}

ALL CART RELATED ENDPOINTS UPDATED 
--------------------------------------------------------------------------------------------
## Wishlist Management

### Get Wishlist
- **URL**: `/wishlist/`
- **Method**: GET
- **Auth**: Required
- **Success Response (200)**:
```json
{
    "id": 1,
    "user": 1,
    "products": [
        {
            "id": 1,
            "product": {
                "id": 1,
                "name": "Product Name",
                "price": "99.99",
                "images": ["url1"],
                "stock_quantity": 10
            },
            "added_at": "2024-01-20T10:30:00Z"
        }
    ]
}


Move Items to Cart
URL: /wishlist/move-to-cart/
Method: POST
Auth: Required
Body:
{
    "item_ids": [1, 2, 3]
}

Success Response (200):
{
    "status": "Items moved to cart successfully"
}

Error Response (400):
{
    "error": "Some items are out of stock"
}

### Bulk Delete Wishlist Items
- **URL**: `/wishlist/bulk-delete/`
- **Method**: POST
- **Auth**: Required
- **Body**:
```json
{
    "item_ids": [1, 2, 3]
}


{
    "status": "Items deleted successfully"
}



Get Stock Notifications
URL: /wishlist/stock-notifications/
Method: GET
Auth: Required
Success Response (200):
[
    {
        "product_id": 1,
        "product_name": "Product Name",
        "stock_quantity": 5,
        "added_at": "2024-01-20T10:30:00Z"
    }
]

Add Item to Wishlist
URL: /wishlist-items/
Method: POST
Auth: Required
Body:
{
    "product": 1
}


Success Response (201):
{
    "id": 1,
    "wishlist": 1,
    "product": 1,
    "added_at": "2024-01-20T10:30:00Z"
}



## Order Management

### List Orders
- **URL**: `/orders/`
- **Method**: GET
- **Auth**: Required
- **Query Parameters**:
  - `status`: PENDING/PROCESSING/SHIPPED/DELIVERED/CANCELLED
  - `start_date`: Filter by start date
  - `end_date`: Filter by end date

- **Success Response (200)**:
```json
[
    {
        "id": 1,
        "user": 1,
        "items": [
            {
                "id": 1,
                "product": 1,
                "quantity": 2,
                "price": "99.99"
            }
        ],
        "status": "PENDING",
        "shipping_address": "123 Main St",
        "shipping_city": "Lagos",
        "shipping_state": "Lagos",
        "shipping_country": "Nigeria",
        "shipping_zip": "100001",
        "shipping_cost": "4.99",
        "subtotal": "199.98",
        "discount": "0.00",
        "total": "204.97",
        "payment_method": "STRIPE",
        "payment_status": "PENDING",
        "created_at": "2024-01-20T10:30:00Z",
        "updated_at": "2024-01-20T10:30:00Z"
    }
]

### Order Tracking
- **URL**: `/orders/{order_id}/tracking/`
- **Method**: GET
- **Auth**: Required
- **Success Response (200)**:
```json
[
    {
        "id": 1,
        "status": "PROCESSING",
        "location": "Lagos Sorting Center",
        "description": "Package is being processed",
        "timestamp": "2024-01-20T10:30:00Z"
    }
]


Add Tracking Event
URL: /orders/{order_id}/tracking/add/
Method: POST
Auth: Required
Body:
{
    "status": "SHIPPED",
    "location": "Lagos Distribution Center",
    "description": "Package has left the warehouse"
}


Success Response (200):
{
    "id": 2,
    "status": "SHIPPED",
    "location": "Lagos Distribution Center",
    "description": "Package has left the warehouse",
    "timestamp": "2024-01-20T11:30:00Z"
}

Update Order Status
URL: /orders/{order_id}/update_status/
Method: PATCH
Auth: Required
Body:
{
    "status": "SHIPPED"
}

Success Response (200):
{
    "id": 1,
    "status": "SHIPPED",
    "updated_at": "2024-01-20T11:30:00Z"
}

Success Response (201):
{
    "status": "success",
    "message": "Order created successfully",
    "order_id": 1,
    "total": "204.97"
}

Error Response (400):
{
    "status": "error",
    "message": "Cart is empty"
}

### Get Payment Methods
- **URL**: `/checkout/payment-methods/`
- **Method**: GET
- **Auth**: Required
- **Success Response (200)**:
```json
{
    "methods": [
        {
            "id": "visa",
            "name": "Visa",
            "enabled": true
        },
        {
            "id": "mastercard",
            "name": "Mastercard",
            "enabled": true
        },
        {
            "id": "stripe",
            "name": "Stripe",
            "enabled": true
        },
        {
            "id": "paypal",
            "name": "PayPal",
            "enabled": true
        },
        {
            "id": "google_pay",
            "name": "Google Pay",
            "enabled": true
        }
    ]
}

Process Payment
URL: /checkout/process-payment/
Method: POST
Auth: Required
Body:
{
    "payment_method": "STRIPE",
    "payment_data": {
        "card_details": {
            "last4": "4242",
            "brand": "visa",
            "exp_date": "12/25"
        }
    },
    "order_id": 1,
    "save_card": true
}


Success Response (200):
{
    "status": "success",
    "payment_id": 1
}

Error Response (400):
{
    "status": "error",
    "message": "Payment processing failed"
}

### Calculate Shipping Cost
- **URL**: `/checkout/shipping-cost/`
- **Method**: POST
- **Auth**: Required
- **Body**:
```json
{
    "shipping_method_id": 1,
    "address_id": 1
}

Success Response (200):
{
    "shipping_cost": "4.99",
    "estimated_days": 3
}

Error Response (400):
{
    "error": "Invalid shipping method or address"
}

List Shipping Methods
URL: /shipping-methods/
Method: GET
Auth: Required
Success Response (200):
[
    {
        "id": 1,
        "name": "Standard Shipping",
        "price": "4.99",
        "estimated_days": 3,
        "description": "Delivery within 3-5 business days",
        "delivery_date": "2024-01-23T10:30:00Z"
    }
]

## Address Management

### List Addresses
- **URL**: `/addresses/`
- **Method**: GET
- **Auth**: Required
- **Success Response (200)**:
```json
[
    {
        "id": 1,
        "street_address": "123 Main St",
        "city": "Lagos",
        "state": "Lagos",
        "zip_code": "100001",
        "country": "Nigeria",
        "is_default": true,
        "created_at": "2024-01-20T10:30:00Z",
        "updated_at": "2024-01-20T10:30:00Z"
    }
]

Add New Address
URL: /addresses/
Method: POST
Auth: Required
Body:
{
    "street_address": "123 Main St",
    "city": "Lagos",
    "state": "Lagos",
    "zip_code": "100001",
    "country": "Nigeria",
    "is_default": true
}

Success Response (201):
{
    "status": "success",
    "message": "Address added successfully",
    "data": {
        "id": 1,
        "street_address": "123 Main St",
        "city": "Lagos",
        "state": "Lagos",
        "zip_code": "100001",
        "country": "Nigeria",
        "is_default": true
    }
}

## Review System

### List Reviews
- **URL**: `/reviews/`
- **Method**: GET
- **Query Parameters**:
  - `rating`: Filter by rating (1-5)
  - `has_images`: true/false
  - `tag`: Filter by tag slug 
  - `ordering`: created_at, helpful_votes, rating
- **Success Response (200)**:
```json
{
    "count": 10,
    "results": [
        {
            "id": 1,
            "product": 1,
            "user_email": "user@example.com",
            "rating": 5,
            "content": "Great product!",
            "images": ["url1", "url2"],
            "tags": [
                {
                    "id": 1,
                    "name": "Fast shipping",
                    "slug": "fast-shipping",
                    "count": 5
                }
            ],
            "helpful_count": 10,
            "is_helpful": true,
            "variant": "White",
            "is_verified_purchase": true,
            "created_at": "2024-01-20T10:30:00Z"
        }
    ]
}


### Create Review
- **URL**: `/reviews/`
- **Method**: POST
- **Auth**: Required
- **Body**:
```json
{
    "product": 1,
    "rating": 5,
    "content": "Great product!",
    "images": ["url1", "url2"],
    "tag_ids": [1, 2],
    "variant": "White"
}


{
    "id": 1,
    "product": 1,
    "user_email": "user@example.com",
    "rating": 5,
    "content": "Great product!",
    "images": ["url1", "url2"],
    "tags": [
        {
            "id": 1,
            "name": "Fast shipping",
            "slug": "fast-shipping"
        }
    ],
    "helpful_count": 0,
    "is_helpful": false,
    "is_verified_purchase": true,
    "created_at": "2024-01-20T10:30:00Z"
}


Mark Review as Helpful
URL: /reviews/{review_id}/helpful/
Method: POST
Auth: Required
Success Response (200):
{
    "helpful": true,
    "count": 11
}

### Get Review Summary
- **URL**: `/reviews/summary/`
- **Method**: GET
- **Query Parameters**:
  - `product`: Product ID (required)
- **Success Response (200)**:
```json
{
    "rating_distribution": {
        "1": 2,
        "2": 3,
        "3": 8,
        "4": 15,
        "5": 25
    },
    "tag_distribution": {
        "Fast shipping": 12,
        "Good quality": 18,
        "Great value": 15
    }
}


Get Review Tags
URL: /reviews/tags/
Method: GET
Success Response (200):
[
    {
        "id": 1,
        "name": "Fast shipping",
        "slug": "fast-shipping",
        "count": 12
    },
    {
        "id": 2,
        "name": "Good quality",
        "slug": "good-quality",
        "count": 18
    }
]

## Support Ticket System

### List Support Tickets
- **URL**: `/support-tickets/`
- **Method**: GET
- **Auth**: Required
- **Success Response (200)**:
```json
[
    {
        "id": 1,
        "subject": "Order Issue",
        "message": "My order hasn't arrived",
        "status": "OPEN",
        "priority": "HIGH",
        "order": 1,
        "created_at": "2024-01-20T10:30:00Z",
        "updated_at": "2024-01-20T10:30:00Z",
        "responses": [
            {
                "id": 1,
                "message": "We're looking into it",
                "is_staff_response": true,
                "created_at": "2024-01-20T10:35:00Z",
                "attachment": null
            }
        ]
    }
]

Create Support Ticket
URL: /support-tickets/
Method: POST
Auth: Required
Body:
{
    "subject": "Order Issue",
    "message": "My order hasn't arrived",
    "priority": "HIGH",
    "order": 1
}

Success Response (201):
{
    "status": "success",
    "message": "Ticket created successfully",
    "data": {
        "id": 1,
        "subject": "Order Issue",
        "status": "OPEN",
        "priority": "HIGH"
    }
}

### Add Response to Ticket
- **URL**: `/support-tickets/{ticket_id}/add_response/`
- **Method**: POST
- **Auth**: Required
- **Body**:
```json
{
    "message": "Any update on this?",
    "attachment": null
}


Success Response (200):
{
    "status": "success",
    "message": "Response added successfully",
    "data": {
        "id": 2,
        "message": "Any update on this?",
        "is_staff_response": false,
        "created_at": "2024-01-20T11:30:00Z",
        "attachment": null
    }
}


Update Ticket Status
URL: /support-tickets/{ticket_id}/
Method: PATCH
Auth: Required
Body:
{
    "status": "IN_PROGRESS"
}


Success Response (200):
{
    "id": 1,
    "status": "IN_PROGRESS",
    "updated_at": "2024-01-20T11:35:00Z"
}

## Error Handling and Status Codes

### Global Error Format
All API errors follow this consistent format:
```json
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
Authentication
All authenticated endpoints require JWT token in header:

Authorization: Bearer <jwt_token>


Pagination
Default pagination settings:

Page size: 12 items
Query parameters:
page: Page number
page_size: Items per page (optional)
Testing Instructions
Base URL: https://avantlush-backend-13.onrender.com/api/
Development URL: http://localhost:8000/api/
Required headers:
Content-Type: application/json
Authorization: Bearer <jwt_token>


#New Api Endpoints_____________________________________________________________
/api/dashboard/cart_metrics/
/api/dashboard/customer_metrics/
/api/dashboard/order_metrics/
/api/dashboard/sales_trend/
/api/dashboard/recent_orders/

Here are the API endpoints you can now use:

List Products (with filtering):

CopyGET /api/product-management/?view=management

Filter by status:

CopyGET /api/product-management/?status=published
GET /api/product-management/?status=draft
GET /api/product-management/?status=low_stock

Search products:

CopyGET /api/product-management/?search=query

Export products:

CopyGET /api/product-management/export/

Bulk update status:

CopyPOST /api/product-management/bulk-update-status/
Body: {
    "product_ids": [1, 2, 3],
    "status": "active"
}

You can now filter products by tab using the API endpoint:
CopyGET /api/products/?tab=all
GET /api/products/?tab=published
GET /api/products/?tab=low_stock
GET /api/products/?tab=draft

____________________________________________________
# AvantLush Dashboard API Documentation

## Base URL
`https://avantlush-backend-13.onrender.com/api/dashboard/`

## Authentication
- All endpoints require authentication via Bearer token
- Status 401 will be returned if unauthorized

## 1. Cart Metrics
**GET** `/cart_metrics/`

Query Parameters:
- `period`: string, optional (day|week|month|year), default: 'week'

Success Response (200):
```json
{
    "success": true,
    "data": {
        "abandoned_rate": 25.5,
        "total_carts": 100,
        "abandoned_carts": 25,
        "period": "week"
    }
}

Error Response (401):

{
    "success": false,
    "message": "Authentication credentials were not provided"
}

2. Customer Metrics
GET /customer_metrics/

Query Parameters:

period: string, optional (day|week|month|year), default: 'week'
Success Response (200):

{
    "success": true,
    "data": {
        "total_customers": 500,
        "active_customers": 150,
        "growth_rate": 12.5,
        "period": "week"
    }
}

 Order Metrics
GET /order_metrics/

Query Parameters:

period: string, optional (day|week|month|year), default: 'week'
Success Response (200):

{
    "success": true,
    "data": {
        "orders_by_status": [
            {
                "status": "PENDING",
                "count": 5
            },
            {
                "status": "PROCESSING",
                "count": 10
            },
            {
                "status": "SHIPPED",
                "count": 15
            },
            {
                "status": "DELIVERED",
                "count": 20
            }
        ],
        "total_revenue": "15000.00",
        "total_orders": 50,
        "period": "week"
    }
}

4. Sales Trend
GET /sales_trend/

Query Parameters:

period: string, optional (day|week|month|year), default: 'week'
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

5. Recent Orders
GET /recent_orders/

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

Common Error Responses:

401 Unauthorized:

{
    "success": false,
    "message": "Authentication credentials were not provided"
}

400 Bad Request:

{
    "success": false,
    "message": "Invalid period parameter",
    "valid_periods": ["day", "week", "month", "year"]
}

500 Server Error:

{
    "success": false,
    "message": "An error occurred while processing your request"
}

Rate Limiting
5 requests per minute per IP address
Status 429 will be returned if rate limit is exceeded
Data Formats
All timestamps are in ISO 8601 format
All monetary values are decimal strings with 2 decimal places
All percentage values are floats