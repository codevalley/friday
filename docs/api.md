# API Documentation

## Overview

The Friday API service provides endpoints for user management and note operations. All endpoints are RESTful and return JSON responses.

## Base URL

```
http://localhost:8000
```

## Authentication

Most endpoints require JWT authentication. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication

#### POST /auth/login
Login with username and password to get JWT token.

**Request Body:**
```json
{
    "username": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "access_token": "string",
    "token_type": "bearer"
}
```

#### POST /auth/register
Register a new user.

**Request Body:**
```json
{
    "username": "string",
    "email": "string",
    "password": "string"
}
```

**Response:**
```json
{
    "id": "uuid",
    "username": "string",
    "email": "string"
}
```

### Notes

#### GET /notes
Get all notes for the authenticated user.

**Response:**
```json
[
    {
        "id": "uuid",
        "title": "string",
        "content": "string",
        "created_at": "datetime",
        "updated_at": "datetime"
    }
]
```

#### POST /notes
Create a new note.

**Request Body:**
```json
{
    "title": "string",
    "content": "string"
}
```

**Response:**
```json
{
    "id": "uuid",
    "title": "string",
    "content": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### GET /notes/{note_id}
Get a specific note by ID.

**Response:**
```json
{
    "id": "uuid",
    "title": "string",
    "content": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### PUT /notes/{note_id}
Update a specific note.

**Request Body:**
```json
{
    "title": "string",
    "content": "string"
}
```

**Response:**
```json
{
    "id": "uuid",
    "title": "string",
    "content": "string",
    "created_at": "datetime",
    "updated_at": "datetime"
}
```

#### DELETE /notes/{note_id}
Delete a specific note.

**Response:**
```json
{
    "message": "Note deleted successfully"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
    "detail": "Error message explaining the validation error"
}
```

### 401 Unauthorized
```json
{
    "detail": "Could not validate credentials"
}
```

### 403 Forbidden
```json
{
    "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
    "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
    "detail": "Internal server error"
}
```

## Rate Limiting

API requests are limited to 100 requests per minute per IP address. The following headers are included in responses:

- `X-RateLimit-Limit`: Maximum number of requests allowed per window
- `X-RateLimit-Remaining`: Number of requests remaining in current window
- `X-RateLimit-Reset`: Time when the rate limit will reset 