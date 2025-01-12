# API Documentation

## Base URL
https://avantlush-backend-13.onrender.com
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

### GET /products/
- **Description:** Lists all products.
- **Response Codes:**
  - `200 OK`: Returns a list of products.

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

### GET /cart/
- **Description:** Lists all items in the authenticated user's cart.
- **Response Codes:**
  - `200 OK`: Returns a list of cart items.
  - `401 UNAUTHORIZED`: User is not authenticated.

- **POST /cart/**
    - **Description:** Creates a new cart for the authenticated user (if one doesn't exist).
    - **Response Codes:**
        - `201 CREATED`: Successfully created a new cart.
        - `400 BAD REQUEST`: Invalid request.
        - `401 UNAUTHORIZED`: User is not authenticated.

- **DELETE /cart/**
    - **Description:** Clears the authenticated user's cart.
    - **Response Codes:**
        - `204 NO CONTENT`: Successfully cleared the cart.
        - `401 UNAUTHORIZED`: User is not authenticated.

### GET /cart/items/
- **Description:** Lists all items in the authenticated user's cart.
- **Response Codes:**
  - `200 OK`: Returns a list of cart items.
  - `401 UNAUTHORIZED`: User is not authenticated.

### POST /cart/items/
- **Description:** Adds a new item to the authenticated user's cart.
- **Request Body:**
    ```json
    {
      "cart": 1,  // ID of the cart
      "product": 1, // ID of the product
      "quantity": 1
    }
    ```
- **Response Codes:**
  - `201 CREATED`: Successfully added the item to the cart.
  - `400 BAD REQUEST`: Invalid request.
  - `401 UNAUTHORIZED`: User is not authenticated.

### GET /cart/items/<int:pk>/
- **Description:** Retrieves a specific item from the authenticated user's cart.
- **Response Codes:**
  - `200 OK`: Returns the cart item.
  - `401 UNAUTHORIZED`: User is not authenticated.
  - `404 NOT FOUND`: Cart item with the given ID not found.

### PUT /cart/items/<int:pk>/
- **Description:** Updates a specific item in the authenticated user's cart.
- **Request Body:**
    ```json
    {
      "quantity": 2
    }
    ```
- **Response Codes:**
  - `200 OK`: Successfully updated the cart item.
  - `400 BAD REQUEST`: Invalid request.
  - `401 UNAUTHORIZED`: User is not authenticated.
  - `404 NOT FOUND`: Cart item with the given ID not found.

### PATCH /cart/items/<int:pk>/
- **Description:** Partially updates a specific item in the authenticated user's cart.
- **Request Body:**
    ```json
    {
      "quantity": 3
    }
    ```
- **Response Codes:**
  - `200 OK`: Successfully updated the cart item.
  - `400 BAD REQUEST`: Invalid request.
  - `401 UNAUTHORIZED`: User is not authenticated.
  - `404 NOT FOUND`: Cart item with the given ID not found.

### DELETE /cart/items/<int:pk>/
- **Description:** Deletes a specific item from the authenticated user's cart.
- **Response Codes:**
  - `204 NO CONTENT`: Successfully deleted the cart item.
  - `401 UNAUTHORIZED`: User is not authenticated.
  - `404 NOT FOUND`: Cart item with the given ID not found.

### GET /orders/
- **Description:** Lists all orders for the authenticated user.
- **Response Codes:**
  - `200 OK`: Returns a list of orders.
  - `401 UNAUTHORIZED`: User is not authenticated.

### POST /orders/
- **Description:** Creates a new order for the authenticated user.
- **Request Body:**
    ```json
    {
      "items": [
        {
          "product": 1,
          "quantity": 2
        }
      ]
    }
    ```
- **Response Codes:**
  - `201 CREATED`: Successfully created a new order.
  - `400 BAD REQUEST`: Invalid request.
  - `401 UNAUTHORIZED`: User is not authenticated.

### GET /orders/<int:pk>/
- **Description:** Retrieves a specific order for the authenticated user.
- **Response Codes:**
  - `200 OK`: Returns the order details.
  - `401 UNAUTHORIZED`: User is not authenticated.
  - `404 NOT FOUND`: Order with the given ID not found.

### PATCH /orders/<int:pk>/status/
- **Description:** Updates the status of a specific order.
- **Request Body:**
    ```json
    {
      "status": "SHIPPED"
    }
    ```
- **Response Codes:**
  - `200 OK`: Successfully updated the order status.
  - `400 BAD REQUEST`: Invalid request.
  - `401 UNAUTHORIZED`: User is not authenticated.
  - `404 NOT FOUND`: Order with the given ID not found.

### Admin Endpoint
- `GET /admin/`: Django admin interface.

### Accounts Endpoints
- **Description:** Includes URLs for Django Allauth for social authentication and account management. Refer to the Django Allauth documentation for details. Key endpoints include:
    - `GET /accounts/login/`: User login page.
    - `GET /accounts/logout/`: User logout.
    - `GET /accounts/signup/`: User signup page.
    - `GET /accounts/profile/`: User profile information.
# API Documentation

## Base URL

All API endpoints are prefixed with `/api/`.

## Endpoints

### GET /api/
- **Description:**  Returns the status of the API and available endpoints.
- **Response Codes:**
  - `200 OK`

### POST /api/waitlist/signup/
- **Description:**  Adds a new email to the waitlist.
- **Request Body:**
  ```json
  {
    "email": "user@example.com"
  }
  ```
- **Response Codes:**
  - `201 CREATED`: Successfully added to the waitlist.
  - `400 BAD REQUEST`: Invalid email format or other input errors.
  - `500 INTERNAL SERVER ERROR`: An unexpected error occurred on the server.

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

### GET /api/products/
- **Description:**  Lists all products.
- **Response Codes:**
  - `200 OK`

### GET /api/products/<int:pk>/
- **Description:** Retrieves details of a specific product.
- **Response Codes:**
  - `200 OK`

### GET /api/articles/
- **Description:**  Lists all articles.
- **Response Codes:**
  - `200 OK`

### GET /api/articles/<int:pk>/
- **Description:** Retrieves details of a specific article.
- **Response Codes:**
  - `200 OK`

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

### POST /api-token-auth/
- **Description:**  Obtains an authentication token using email and password.
- **Request Body:**
  ```json
  {
    "email": "user@example.com",
    "password": "password"
  }
  ```
- **Response Codes:**
    - `200 OK`: Successfully authenticated. Returns an authentication token.
    - `400 BAD REQUEST`: Invalid credentials.

### GET /preview-email/
- **Description:**  Previews the waitlist confirmation email template.
- **Response Codes:**
  - `200 OK`

### POST /auth/google/
- **Description:** Authenticates a user using a Google ID token.
- **Request Body:**
  ```json
  {
    "token": "GOOGLE_ID_TOKEN",
    "email": "user@example.com",
    "location": "Country"
  }
  ```
- **Response Codes:**
    - `200 OK`: Successfully authenticated. Returns an authentication token.
    - `400 BAD REQUEST`: Invalid token or email verification failed.

### Cart Endpoints
- `GET /api/cart/`: Lists all items in the user's cart.
- `POST /api/cart/`: Adds a new item to the cart.
- `DELETE /api/cart/`: Clears the user's cart.

### Cart Item Endpoints
- `GET /api/cart/items/`: Lists all cart items.
- `POST /api/cart/items/`: Adds a new item to the cart.
- `GET /api/cart/items/<int:pk>/`: Retrieves a specific cart item.
- `PUT /api/cart/items/<int:pk>/`: Updates a specific cart item.
- `PATCH /api/cart/items/<int:pk>/`: Partially updates a specific cart item.
- `DELETE /api/cart/items/<int:pk>/`: Deletes a specific cart item.

### Order Endpoints
- `GET /api/orders/`: List all orders for the authenticated user.
- `POST /api/orders/`: Create a new order.
- `GET /api/orders/<int:pk>/`: Retrieve a specific order.
- `PATCH /api/orders/<int:pk>/status/`: Update the status of a specific order.

### Admin Endpoint
- `GET /admin/`: Django admin interface.

### Accounts Endpoints
- **Description:** Includes URLs for Django Allauth for social authentication and account management. Refer to the Django Allauth documentation for details. Key endpoints include:
    - `GET /accounts/login/`: User login page.
    - `GET /accounts/logout/`: User logout.
    - `GET /accounts/signup/`: User signup page.
    - `GET /accounts/profile/`: User profile information.
