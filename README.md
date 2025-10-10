# VEOmenu Backend

Multi-tenant Django REST Framework backend for the VEOmenu digital menu platform.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL (optional, SQLite by default)
- Virtual environment tool (venv, virtualenv, or conda)

### Installation

1. **Create and activate virtual environment:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env file with your configuration
```

4. **Run migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create superuser:**
```bash
python manage.py createsuperuser
```

6. **Run development server:**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## 📁 Project Structure

```
veo_menu_backend/
├── apps/
│   ├── authentication/      # User authentication & magic links
│   ├── instances/           # Multi-tenant instance management
│   ├── menus/              # Menu CRUD operations
│   ├── analytics/          # Analytics and dashboard data
│   ├── support/            # Support ticket system
│   └── ai/                 # AI integrations (menu extraction, etc.)
├── veo_menu_backend/
│   ├── settings.py         # Django settings
│   ├── urls.py             # Main URL configuration
│   └── wsgi.py             # WSGI application
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
└── .env.example           # Environment variables template
```

## 🔧 Configuration

### Database Setup (PostgreSQL)

1. Install PostgreSQL
2. Create database:
```sql
CREATE DATABASE veomenu_db;
CREATE USER veomenu_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE veomenu_db TO veomenu_user;
```

3. Update `.env`:
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=veomenu_db
DB_USER=veomenu_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### Email Configuration (Magic Links)

For development, emails are printed to console. For production:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

## 📡 API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - Register new user
- `POST /api/v1/auth/login/` - Send magic link to email
- `POST /api/v1/auth/verify/{token}/` - Verify magic link token
- `GET /api/v1/auth/profile/` - Get user profile
- `POST /api/v1/auth/logout/` - Logout user

### Instances
- `GET /api/v1/instances/` - List user's instances
- `POST /api/v1/instances/` - Create new instance
- `GET /api/v1/instances/{id}/` - Get instance details
- `PUT /api/v1/instances/{id}/` - Update instance
- `DELETE /api/v1/instances/{id}/` - Delete instance

### Menus
- `GET /api/v1/menus/` - List instance menus
- `POST /api/v1/menus/` - Create menu
- `GET /api/v1/menus/{id}/` - Get menu details
- `PUT /api/v1/menus/{id}/` - Update menu
- `DELETE /api/v1/menus/{id}/` - Delete menu

Full API documentation available at: `/api/schema/swagger-ui/`

## 🔐 Multi-Tenancy

All authenticated requests must include:

```javascript
headers: {
  'Authorization': 'Bearer <jwt_token>',
  'X-Instance-ID': '<instance_id>'
}
```

The backend automatically filters all data based on the instance ID in the header.

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.authentication

# Run with coverage
coverage run manage.py test
coverage report
```

## 📊 Admin Panel

Access the admin panel at `http://localhost:8000/admin/`

The admin uses Jazzmin for an enhanced UI experience.

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure proper `SECRET_KEY`
- [ ] Set up PostgreSQL database
- [ ] Configure production email backend
- [ ] Set up media file storage (S3, etc.)
- [ ] Configure ALLOWED_HOSTS
- [ ] Set up HTTPS
- [ ] Configure CORS for production frontend URL
- [ ] Run `python manage.py collectstatic`
- [ ] Set up proper logging

## 📝 Development

### Creating a new app

```bash
python manage.py startapp app_name
```

Remember to:
1. Add app to `INSTALLED_APPS` in `settings.py`
2. Create models, serializers, views
3. Add URLs to main `urls.py`
4. Write tests

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migrations
python manage.py showmigrations
```

## 🤝 Contributing

1. Create feature branch
2. Make changes
3. Write tests
4. Run tests and linting
5. Submit pull request

## 📄 License

Proprietary - All rights reserved
