# VEOmenu API Documentation

## 🎉 Backend Setup Complete!

The Django REST API is fully functional and ready to use. The server runs at **http://127.0.0.1:8000/**

## 📚 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://127.0.0.1:8000/api/schema/swagger-ui/
- **OpenAPI Schema**: http://127.0.0.1:8000/api/schema/

## 🔐 Authentication Endpoints

### Register User
```
POST /api/auth/register/
Content-Type: application/json

{
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "+351912345678",
  "language": "en",
  "timezone": "Europe/Lisbon"
}
```

**Response**:
```json
{
  "message": "Registration successful. Please log in.",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    "phone": "+351912345678",
    "language": "en",
    "timezone": "Europe/Lisbon",
    "is_active": true,
    "date_joined": "2025-10-08T02:00:00Z"
  }
}
```

### Request Magic Link
```
POST /api/auth/request-magic-link/
Content-Type: application/json

{
  "email": "user@example.com"
}
```

**Response**:
```json
{
  "message": "Magic link sent to your email. Please check your inbox.",
  "expires_in_minutes": 15
}
```

**Email will contain**: A link like `http://localhost:3000/auth/verify?token=abc123...`

### Verify Magic Link
```
POST /api/auth/verify-magic-link/
Content-Type: application/json

{
  "token": "abc123..."
}
```

**Response**:
```json
{
  "message": "Login successful",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "John Doe",
    ...
  }
}
```

### Logout
```
POST /api/auth/logout/
Authorization: Bearer <access_token>
```

**Response**:
```json
{
  "message": "Logout successful"
}
```

## 👤 User Endpoints

### Get Current User Profile
```
GET /api/users/me/
Authorization: Bearer <access_token>
```

**Response**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "John Doe",
  "phone": "+351912345678",
  "avatar": null,
  "language": "en",
  "timezone": "Europe/Lisbon",
  "is_active": true,
  "date_joined": "2025-10-08T02:00:00Z",
  "last_login": "2025-10-08T02:05:00Z"
}
```

### Update User Profile
```
PATCH /api/users/update-profile/
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "John Smith",
  "language": "pt"
}
```

### Get Active Sessions
```
GET /api/users/sessions/
Authorization: Bearer <access_token>
```

### Revoke Session
```
POST /api/users/revoke-session/
Authorization: Bearer <access_token>

{
  "session_id": 123
}
```

## 🏢 Instance Endpoints

### List User's Instances
```
GET /api/instances/
Authorization: Bearer <access_token>
```

**Response**:
```json
[
  {
    "id": "uuid-1234",
    "name": "My Restaurant",
    "slug": "my-restaurant",
    "logo": null,
    "city": "Lisbon",
    "country": "Portugal",
    "subscription_status": "trial",
    "created_at": "2025-10-08T02:00:00Z",
    "member_count": 3
  }
]
```

### Create Instance
```
POST /api/instances/
Authorization: Bearer <access_token>

{
  "name": "My Restaurant",
  "description": "A cozy family restaurant",
  "address": "Rua Example, 123",
  "city": "Lisbon",
  "country": "Portugal",
  "postal_code": "1000-001",
  "phone": "+351212345678",
  "email": "info@myrestaurant.com",
  "website": "https://myrestaurant.com"
}
```

### Get Instance Details
```
GET /api/instances/{id}/
Authorization: Bearer <access_token>
```

### Update Instance
```
PATCH /api/instances/{id}/
Authorization: Bearer <access_token>

{
  "name": "Updated Restaurant Name",
  "wifi_ssid": "Restaurant_WiFi",
  "wifi_password": "password123"
}
```

### Get Instance Members
```
GET /api/instances/{id}/members/
Authorization: Bearer <access_token>
```

### Invite Member
```
POST /api/instances/{id}/invite-member/
Authorization: Bearer <access_token>

{
  "email": "employee@example.com",
  "role": "staff"
}
```

**Roles**: `admin`, `manager`, `staff`

### Remove Member
```
DELETE /api/instances/{id}/remove-member/
Authorization: Bearer <access_token>

{
  "user_id": 5
}
```

### Get/Update Business Hours
```
GET /api/instances/{id}/business-hours/
PUT /api/instances/{id}/business-hours/
Authorization: Bearer <access_token>

# PUT Body:
[
  {
    "day_of_week": 0,
    "open_time": "09:00:00",
    "close_time": "22:00:00",
    "is_closed": false
  },
  {
    "day_of_week": 1,
    "open_time": "09:00:00",
    "close_time": "22:00:00",
    "is_closed": false
  },
  ...
]
```

**day_of_week**: 0=Monday, 1=Tuesday, ... 6=Sunday

## 📋 Menu Endpoints

### List Menus
```
GET /api/menus/
Authorization: Bearer <access_token>
```

### Create Menu
```
POST /api/menus/
Authorization: Bearer <access_token>

{
  "instance": "uuid-1234",
  "name": "Dinner Menu",
  "description": "Our evening menu",
  "default_language": "en",
  "available_languages": ["en", "pt", "es"]
}
```

### Get Menu Details
```
GET /api/menus/{id}/
Authorization: Bearer <access_token>
```

**Response includes full menu with all sections and items**

### Update Menu
```
PATCH /api/menus/{id}/
Authorization: Bearer <access_token>

{
  "name": "Updated Menu Name",
  "is_active": true
}
```

### Public Menu View (No Auth Required)
```
GET /api/menus/{id}/public/?language=en
```

**Used by customers to view the menu via QR code**

### Get Menu Analytics
```
GET /api/menus/{id}/analytics/?days=7
Authorization: Bearer <access_token>
```

**Response**:
```json
{
  "menu_id": "uuid-1234",
  "menu_name": "Dinner Menu",
  "period_days": 7,
  "total_views": 145,
  "language_breakdown": {
    "en": 80,
    "pt": 45,
    "es": 20
  },
  "device_breakdown": {
    "mobile": 120,
    "desktop": 25
  },
  "views_by_day": {
    "2025-10-01": 20,
    "2025-10-02": 18,
    ...
  }
}
```

## 📁 Menu Section Endpoints

### List Sections
```
GET /api/menu-sections/
Authorization: Bearer <access_token>
```

### Create Section
```
POST /api/menu-sections/
Authorization: Bearer <access_token>

{
  "menu": "uuid-menu-id",
  "name": {
    "en": "Appetizers",
    "pt": "Entradas",
    "es": "Entrantes"
  },
  "description": {
    "en": "Start your meal right",
    "pt": "Comece bem a sua refeição"
  },
  "order": 1,
  "is_active": true
}
```

### Get Section Details
```
GET /api/menu-sections/{id}/
Authorization: Bearer <access_token>
```

### Update Section
```
PATCH /api/menu-sections/{id}/
Authorization: Bearer <access_token>
```

## 🍽️ Menu Item Endpoints

### List Items
```
GET /api/menu-items/
Authorization: Bearer <access_token>
```

### Create Item
```
POST /api/menu-items/
Authorization: Bearer <access_token>

{
  "section": "section-id",
  "name": {
    "en": "Grilled Salmon",
    "pt": "Salmão Grelhado",
    "es": "Salmón a la Parrilla"
  },
  "description": {
    "en": "Fresh Atlantic salmon with vegetables",
    "pt": "Salmão do Atlântico fresco com legumes"
  },
  "price": 18.50,
  "image": null,
  "is_available": true,
  "is_featured": false,
  "is_vegetarian": false,
  "is_vegan": false,
  "is_gluten_free": true,
  "is_spicy": false,
  "allergens": ["fish"],
  "calories": 450,
  "preparation_time": 20,
  "order": 1
}
```

### Get Item Details
```
GET /api/menu-items/{id}/
Authorization: Bearer <access_token>
```

### Update Item
```
PATCH /api/menu-items/{id}/
Authorization: Bearer <access_token>
```

### Toggle Item Availability
```
PATCH /api/menu-items/{id}/toggle-availability/
Authorization: Bearer <access_token>
```

**Response**:
```json
{
  "message": "Item is now unavailable",
  "item": { ... }
}
```

## 📱 QR Code Endpoints

### List QR Codes
```
GET /api/qrcodes/
Authorization: Bearer <access_token>
```

### Get QR Code Details
```
GET /api/qrcodes/{id}/
Authorization: Bearer <access_token>
```

### Scan QR Code (Public)
```
POST /api/qrcodes/{id}/scan/
```

**Response**:
```json
{
  "menu_url": "http://localhost:3000/menu/uuid-1234",
  "menu_id": "uuid-1234"
}
```

## 🔑 Authorization

All authenticated endpoints require the `Authorization` header:

```
Authorization: Bearer <access_token>
```

The access token is obtained from the `/api/auth/verify-magic-link/` endpoint after successful authentication.

## 🌐 CORS Configuration

The backend is configured to accept requests from:
- http://localhost:3000 (React frontend)

To add more origins, update the `CORS_ALLOWED_ORIGINS` setting in `settings.py`.

## 🚀 Running the Server

```bash
# Activate conda environment
conda activate VEO

# Navigate to backend directory
cd D:\1\Projects\VEO\veo_menu_backend

# Run server
python manage.py runserver
```

Server will start at: **http://127.0.0.1:8000/**

## 📊 Admin Panel

Access the Django admin panel at: **http://127.0.0.1:8000/admin/**

Create a superuser first:
```bash
python manage.py createsuperuser
```

The admin panel uses the Jazzmin theme for a modern UI.

## 🧪 Testing the API

You can test the API using:
1. **Swagger UI**: http://127.0.0.1:8000/api/schema/swagger-ui/
2. **Postman**: Import the OpenAPI schema from http://127.0.0.1:8000/api/schema/
3. **curl** or **httpie** command-line tools
4. **Thunder Client** (VS Code extension)

## 📝 Next Steps

1. ✅ Backend API is complete and functional
2. ✅ All models, serializers, and views are created
3. ✅ URL routing is configured
4. ⏭️ **Next**: Update frontend API integration layer
5. ⏭️ Connect frontend authentication to backend
6. ⏭️ Test end-to-end flow from React to Django

## 🔗 Frontend Integration

The frontend should make API calls to:
- Base URL: `http://127.0.0.1:8000/api/`
- All endpoints documented above

Example fetch call:
```javascript
const response = await fetch('http://127.0.0.1:8000/api/auth/register/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    email: 'user@example.com',
    name: 'John Doe',
  }),
});
const data = await response.json();
```

For authenticated requests:
```javascript
const token = localStorage.getItem('access_token');
const response = await fetch('http://127.0.0.1:8000/api/users/me/', {
  method: 'GET',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  },
});
```
