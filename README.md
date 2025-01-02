# API Documentation

## Endpoints

### GET /
- **Description:**  Returns the status of the API and available endpoints.
- **Response Codes:**
  - `200 OK`

### POST /waitlist/signup/
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

### /accounts/
- **Description:** Includes URLs for Django Allauth for social authentication and account management. Refer to the Django Allauth documentation for details.
