# API Documentation

## Base URL
https://avantlush-backend-2s6k.onrender.com
All API endpoints are prefixed with `/api/`.

## Endpoints

### GET /api/
- **Description:** Returns the status of the API and available endpoints.
- **Response Codes:**
  - `200 OK`

### POST /waitlist/signup/
- **Description:** Adds a new email to the waitlist and sends a confirmation email.
- **Request Body:**
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Response Codes:**
  - `201 CREATED`: Successfully added to the waitlist.
  - `400 BAD REQUEST`: Invalid email format.
  - `500 INTERNAL SERVER ERROR`: An unexpected error occurred on the server.

### GET /preview_email/
- **Description:** Previews the waitlist confirmation email template.
- **Response Codes:**
    - `200 OK`: Returns the HTML content of the email.

### POST /register/
- **Description:** Registers a new user.
- **Request Body:**
  ```json
  {
    "email": "newuser@example.com",
    "password": "securepassword",
    "location": "Country"
  }
  ```
- **Response Codes:**
  - `201 CREATED`: Successfully registered. Returns an authentication token.
  - `400 BAD REQUEST`: Invalid input or email already exists.

### POST /login/
- **Description:** Authenticates an existing user and returns an authentication token.
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password"
  }
  ```
- **Response Codes:**
  - `200 OK`: Successfully logged in. Returns an authentication token.
  - `401 UNAUTHORIZED`: Invalid credentials.
  - `400 BAD REQUEST`: Missing email or password.

### POST /auth/google/
- **Description:** Authenticates a user using Google OAuth.
- **Request Body:**
  ```json
  {
    "access_token": "GOOGLE_ACCESS_TOKEN"
  }
  ```
- **Response Codes:**
    - `200 OK`: Successfully authenticated. Returns an authentication token.
    - `400 BAD REQUEST`: Invalid token or authentication failed.

### GET /verify-email/<str:token>/<str:uidb64>/
- **Description:** Verifies user email using token and uidb64.
- **Response Codes:**
    - `200 OK`: Successfully verified email.
    - `400 BAD REQUEST`: Invalid token or uidb64.

### POST /resend-verification/
- **Description:** Resends email verification link to the user.
- **Request Body:**
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Response Codes:**
    - `200 OK`: Successfully resent verification email.
    - `400 BAD REQUEST`: Invalid email or user not found.

### POST /forgot-password/
- **Description:** Sends password reset link to the user's email.
- **Request Body:**
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Response Codes:**
    - `200 OK`: Successfully sent password reset email.
    - `400 BAD REQUEST`: Invalid email or user not found.

### POST /reset-password/<str:uidb64>/<str:token>/
- **Description:** Resets user password using uidb64 and token.
- **Request Body:**
  ```json
  {
    "new_password": "new_secure_password"
  }
  ```
- **Response Codes:**
    - `200 OK`: Successfully reset password.
    - `400 BAD REQUEST`: Invalid uidb64, token or password.

### POST /login/
- **Description:** Authenticates an existing user and returns an authentication token.
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password"
  }
  ```
- **Response Codes:**
  - `200 OK`: Successfully logged in. Returns an authentication token.
  - `401 UNAUTHORIZED`: Invalid credentials.
  - `400 BAD REQUEST`: Missing email or password.

### GET /products/
- **Description:** Lists all products.
- **Response Codes:**
  - `200 OK`: Returns a list of products.

### GET /products/search/
- **Description:** Searches products based on query parameters.
- **Query Parameters:**
    - `q`: Search term.
    - `category`: Category filter.
    - `price_min`: Minimum price.
    - `price_max`: Maximum price.
    - `rating_min`: Minimum average rating.
    - `review_count_min`: Minimum review count.
    - `ordering`: Fields to order results by.
- **Response Codes:**
    - `200 OK`: Returns a list of products matching the search criteria.

### GET /products/<int:product_id>/recommendations/
- **Description:** Retrieves product recommendations for a specific product.
- **Response Codes:**
    - `200 OK`: Returns a list of recommended products.
    - `404 NOT FOUND`: Product with the given ID not found.

### GET /products/<int:pk>/
- **Description:** Retrieves details of a specific product.
- **Response Codes:**
  - `200 OK`: Returns the details of the product.
  - `404 NOT FOUND`: Product with the given ID not found.

### GET /articles/
- **Description:** Lists all articles.
- **Response Codes:**
  - `200 OK`: Returns a list of articles.

### GET /articles/<int:pk>/
- **Description:** Retrieves details of a specific article.
- **Response Codes:**
  - `200 OK`: Returns the details of the article.
  - `404 NOT FOUND`: Article with the given ID not found.

### Cart Endpoints
- **GET /cart/summary/**
    - **Description:** Retrieves a summary of the authenticated user's cart, including total items and total price.
    - **Response Codes:**
        - `200 OK`: Returns a summary of the cart.
        - `401 UNAUTHORIZED`: User is not authenticated.

- **POST /cart/add-item/**
    - **Description:** Adds a product item to the authenticated user's cart.
    - **Request Body:**
        ```json
        {
          "product_id": 1,
          "quantity": 1
        }
        ```
    - **Response Codes:**
        - `201 CREATED`: Successfully added the item to the cart.
        - `400 BAD REQUEST`: Invalid request, product or quantity.
        - `401 UNAUTHORIZED`: User is not authenticated.

- **POST /cart/update-quantity/**
    - **Description:** Updates the quantity of a specific item in the authenticated user's cart.
    - **Request Body:**
        ```json
        {
          "product_id": 1,
          "quantity": 2
        }
        ```
    - **Response Codes:**
        - `200 OK`: Successfully updated the cart item quantity.
        - `400 BAD REQUEST`: Invalid request, product or quantity.
        - `401 UNAUTHORIZED`: User is not authenticated.

- **POST /cart/remove-item/**
    - **Description:** Removes a specific item from the authenticated user's cart.
    - **Request Body:**
        ```json
        {
          "product_id": 1
        }
        ```
    - **Response Codes:**
        - `204 NO CONTENT`: Successfully removed the item from the cart.
        - `400 BAD REQUEST`: Invalid request, product.
        - `401 UNAUTHORIZED`: User is not authenticated.

- **POST /cart/apply-discount/**
    - **Description:** Applies a discount code to the authenticated user's cart.
    - **Request Body:**
        ```json
        {
          "discount_code": "SUMMER20"
        }
        ```
    - **Response Codes:**
        - `200 OK`: Successfully applied the discount.
        - `400 BAD REQUEST`: Invalid discount code.
        - `401 UNAUTHORIZED`: User is not authenticated.

- **POST /cart/clear/**
    - **Description:** Clears the authenticated user's cart.
    - **Response Codes:**
        - `204 NO CONTENT`: Successfully cleared the cart.
        - `401 UNAUTHORIZED`: User is not authenticated.


### Order Endpoints
- **GET /orders/<int:pk>/tracking/**
    - **Description:** Retrieves the tracking history for a specific order.
    - **Response Codes:**
        - `200 OK`: Returns the tracking history for the order.
        - `401 UNAUTHORIZED`: User is not authenticated.
        - `404 NOT FOUND`: Order with the given ID not found.

- **POST /orders/<int:pk>/tracking/add/**
    - **Description:** Adds a new tracking event to a specific order.
    - **Request Body:**
        ```json
        {
          "event": "Shipped",
          "location": "Warehouse",
          "timestamp": "2025-03-10T10:00:00Z"
        }
        ```
    - **Response Codes:**
        - `201 CREATED`: Successfully added the tracking event.
        - `400 BAD REQUEST`: Invalid request, order or tracking event data.
        - `401 UNAUTHORIZED`: User is not authenticated.
        - `404 NOT FOUND`: Order with the given ID not found.

- **GET /orders/filter-by-date/**
    - **Description:** Filters orders by date range.
    - **Query Parameters:**
        - `start_date`: Start date for filtering (YYYY-MM-DD).
        - `end_date`: End date for filtering (YYYY-MM-DD).
    - **Response Codes:**
        - `200 OK`: Returns a list of orders within the specified date range.
        - `400 BAD REQUEST`: Invalid date range.
        - `401 UNAUTHORIZED`: User is not authenticated.


### Wishlist Endpoints:

*   **`POST /wishlist/move-to-cart/`**
    *   **Description:** Moves a wishlist item to the user's cart.
    *   **Request Body:**
        ```json
        {
          "wishlist_item_id": 1,
          "quantity": 1
        }
        ```
    *   **Response:**
        *   Success (201 Created): Item moved to cart successfully.
        *   `400 BAD REQUEST`: Invalid request, wishlist item or quantity.
        *   `401 UNAUTHORIZED`: User is not authenticated.
        *   `404 NOT FOUND`: Wishlist item with the given ID not found.

*   **`POST /wishlist/bulk-delete/`**
    *   **Description:** Deletes multiple wishlist items in bulk.
    *   **Request Body:**
        ```json
        {
          "wishlist_item_ids": [1, 2, 3]
        }
        ```
    *   **Response:**
        *   Success (204 No Content): Wishlist items deleted successfully.
        *   `400 BAD REQUEST`: Invalid request, wishlist item IDs.
        *   `401 UNAUTHORIZED`: User is not authenticated.

*   **`GET /wishlist/stock-notifications/`**
    *   **Description:** Retrieves stock notifications for wishlist items that are back in stock.
    *   **Response:**
        *   Success (200 OK): List of stock notifications.
        *   `401 UNAUTHORIZED`: User is not authenticated.


### Shipping Method Endpoints:
- **`GET /shipping-methods/`**
    - **Description:** Lists available shipping methods.
    - **Response Codes:**
        - `200 OK`: Returns a list of shipping methods.

- **`POST /shipping-methods/`**
    - **Description:** Creates a new shipping method. (Admin only)
    - **Request Body:**
        ```json
        {
          "name": "Express Shipping",
          "price": "10.00"
        }
        ```
    - **Response Codes:**
        - `201 CREATED`: Successfully created a new shipping method.
        - `400 BAD REQUEST`: Invalid request.
        - `403 FORBIDDEN`: User is not an admin.

- **`GET /shipping-methods/{id}/`**
    - **Description:** Retrieves a specific shipping method by ID.
    - **Response Codes:**
        - `200 OK`: Returns the shipping method details.
        - `404 NOT FOUND`: Shipping method with the given ID not found.

- **`PUT /shipping-methods/{id}/`**
    - **Description:** Updates an existing shipping method. (Admin only)
    - **Request Body:**
        ```json
        {
          "name": "Updated Shipping Method",
          "price": "12.00"
        }
        ```
    - **Response Codes:**
        - `200 OK`: Successfully updated the shipping method.
        - `400 BAD REQUEST`: Invalid request.
        - `403 FORBIDDEN`: User is not an admin.
        - `404 NOT FOUND`: Shipping method with the given ID not found.

- **`PATCH /shipping-methods/{id}/`**
    - **Description:** Partially updates an existing shipping method. (Admin only)
    - **Request Body:**
        ```json
        {
          "price": "15.00"
        }
        ```
    - **Response Codes:**
        - `200 OK`: Successfully updated the shipping method.
        - `400 BAD REQUEST`: Invalid request.
        - `403 FORBIDDEN`: User is not an admin.
        - `404 NOT FOUND`: Shipping method with the given ID not found.

- **`DELETE /shipping-methods/{id}/`**
    - **Description:** Deletes a shipping method. (Admin only)
    - **Response Codes:**
        - `204 NO CONTENT`: Successfully deleted the shipping method.
        - `403 FORBIDDEN`: User is not an admin.
        - `404 NOT FOUND`: Shipping method with the given ID not found.


### Checkout Endpoints:
- **`POST /checkout/initiate/`**
    - **Description:** Initiates the checkout process.
    - **Request Body:**
        ```json
        {
          "shipping_method_id": 1,
          "payment_method": "stripe"
        }
        ```
    - **Response Codes:**
        - `200 OK`: Checkout initiated successfully, returns checkout details.
        - `400 BAD REQUEST`: Invalid request, shipping method or payment method.
        - `401 UNAUTHORIZED`: User is not authenticated.

- **`GET /checkout/summary/`**
    - **Description:** Retrieves a summary of the current checkout.
    - **Response Codes:**
        - `200 OK`: Returns checkout summary details.
        - `401 UNAUTHORIZED`: User is not authenticated.

- **`POST /checkout/payment/`**
    - **Description:** Processes payment for the checkout.
    - **Request Body:**
        ```json
        {
          "token": "payment_token_from_payment_gateway"
        }
        ```
    - **Response Codes:**
        - `200 OK`: Payment processed successfully, returns order confirmation.
        - `400 BAD REQUEST`: Invalid payment token or payment processing error.
        - `401 UNAUTHORIZED`: User is not authenticated.


### Support Ticket Endpoints:
- **`POST /support/submit/`**
    - **Description:** Submits a support ticket.
    - **Request Body:**
        ```json
        {
          "subject": "Issue with order",
          "message": "My order hasn't arrived yet."
        }
        ```
    - **Response Codes:**
        - `201 CREATED`: Successfully submitted support ticket.
        - `400 BAD REQUEST`: Invalid request, subject or message missing.
        - `401 UNAUTHORIZED`: User is not authenticated.


### Review Endpoints:

*   **`GET /reviews/`**
    -   **Description:** Lists all reviews with filtering and ordering.
    -   **Request Method:** GET
    -   **Query Parameters:** (See previous documentation)
    -   **Response:**
        *   Success (200 OK): List of reviews (structure based on `ReviewSerializer`):
            ```json
            [
                {
                    "id": 1,
                    "product": 1,       // Product ID
                    "user_email": "user@example.com",
                    "rating": 5,
                    "content": "This product is amazing!",
                    "images": [],        // Array of image URLs
                    "tags": [           // Array of ReviewTagSerializer
                        {
                            "id": 1,
                            "name": "High Quality",
                            "slug": "high-quality",
                            "count": 10
                        },
                        ...
                    ],
                    "tag_ids": [],      // Write-only, for creating/updating, array of tag IDs
                    "helpful_count": 5,
                    "is_helpful": true, // Whether current user marked as helpful
                    "variant": null,
                    "is_verified_purchase": true,
                    "created_at": "2025-01-27T16:00:00Z"
                },
                ...
            ]
            ```

### Admin Endpoint
- `GET /admin/`: Django admin interface.

### Accounts Endpoints
- **Description:** Includes URLs for Django Allauth for social authentication and account management. Refer to the Django Allauth documentation for details. Key endpoints include:
    - `GET /accounts/login/`: User login page.
    - `GET /accounts/logout/`: User logout.
    - `GET /accounts/signup/`: User signup page.
    - `GET /accounts/profile/`: User profile information.
