# AvantLush Waitlist API Documentation

## API Endpoint
Base URL: https://your-domain.com
Endpoint: /api/waitlist/signup/

## Usage
Method: POST
Content-Type: application/json

### Request Format
```json
{
    "email": "user@example.com"
}


{
    "message": "Successfully joined the waitlist!",
    "data": {
        "email": "user@example.com",
        "created_at": "2024-12-13T12:07:18.068767Z"
    }
}
