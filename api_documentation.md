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
