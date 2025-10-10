# Next Steps - Django Backend

## ✅ What's Been Created

### Models Created:
1. **Authentication App** (`apps/authentication/models.py`)
   - `User` - Custom user model with email auth
   - `MagicLink` - Passwordless authentication tokens
   - `UserSession` - Session tracking

2. **Instances App** (`apps/instances/models.py`)
   - `Instance` - Restaurant/bar instances
   - `InstanceMember` - User membership in instances
   - `BusinessHours` - Opening hours per day

3. **Menus App** (`apps/menus/models.py`)
   - `Menu` - Digital menus
   - `MenuSection` - Menu sections (Appetizers, etc.)
   - `MenuItem` - Individual dishes
   - `MenuView` - Analytics tracking
   - `QRCode` - QR code generation

### Admin Configured:
- All models registered in Django admin
- Jazzmin theme configured
- Inline editing for related models

### Settings Configured:
- Custom User model enabled
- CORS configured
- JWT authentication ready
- REST Framework configured

## 🚀 Run These Commands Now

### 1. Activate Virtual Environment
Open **Anaconda Prompt** or **Miniconda Prompt** and run:
```bash
conda activate VEO
```

### 2. Navigate to Backend Directory
```bash
cd D:\1\Projects\VEO\veo_menu_backend
```

### 3. Install Dependencies
**IMPORTANT**: You MUST install these packages before running migrations:
```bash
pip install -r requirements.txt
```

This will install:
- Django 4.2.7
- Django REST Framework
- JWT Authentication
- CORS Headers
- Pillow (for image fields)
- Jazzmin (admin UI)
- And all other dependencies

### 4. Uncomment Third-Party Apps
After installing packages, **edit `veo_menu_backend/settings.py`** and uncomment these lines:

```python
INSTALLED_APPS = [
    'jazzmin',  # Uncomment this
    # ... core Django apps
    'rest_framework',  # Uncomment this
    'rest_framework_simplejwt',  # Uncomment this
    'corsheaders',  # Uncomment this
    'django_filters',  # Uncomment this
    'drf_spectacular',  # Uncomment this
    # ... local apps
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # Uncomment this
    # ... other middleware
]
```

### 5. Create Database Migrations
After uncommenting the third-party apps in settings.py:
```bash
python manage.py makemigrations
```

### 6. Apply Migrations
```bash
python manage.py migrate
```

### 7. Create Superuser
```bash
python manage.py createsuperuser
```
Enter:
- Email: your-email@example.com
- Name: Your Name
- Password: (your secure password)

### 8. Run Development Server
```bash
python manage.py runserver
```

The server will start at: **http://localhost:8000/**

## 📍 Check These URLs

After running the server:

1. **Admin Panel**: http://localhost:8000/admin/
   - Login with your superuser credentials
   - Explore the Jazzmin UI
   - View all models

2. **API Root**: http://localhost:8000/api/ (to be created)

3. **API Docs**: http://localhost:8000/api/schema/swagger-ui/ (to be created)

## 📋 What's Next

### Immediate Next Steps:

1. **Create Serializers** for each model
   - Convert models to/from JSON
   - Handle validation
   - Files to create:
     - `apps/authentication/serializers.py`
     - `apps/instances/serializers.py`
     - `apps/menus/serializers.py`

2. **Create API Views** (ViewSets)
   - CRUD operations
   - Multi-tenant filtering
   - Files to create:
     - `apps/authentication/views.py`
     - `apps/instances/views.py`
     - `apps/menus/views.py`

3. **Configure URLs**
   - Map endpoints to views
   - Create `urls.py` in each app
   - Update main `veo_menu_backend/urls.py`

4. **Implement Magic Link Auth**
   - Email sending functionality
   - Token generation
   - JWT token creation

5. **Create Multi-Tenant Middleware**
   - Extract `X-Instance-ID` from headers
   - Attach to request object
   - Filter queries automatically

## 🔍 Verify Installation

After running migrations, verify everything is working:

```bash
# Check migrations applied
python manage.py showmigrations

# You should see all apps with [X] marks:
# authentication
#  [X] 0001_initial
# instances
#  [X] 0001_initial
# menus
#  [X] 0001_initial
```

## 📊 Database Structure

Your database now has these tables:
- `users` - User accounts
- `magic_links` - Authentication tokens
- `user_sessions` - Active sessions
- `instances` - Restaurants/bars
- `instance_members` - User-instance relationships
- `business_hours` - Opening hours
- `menus` - Digital menus
- `menu_sections` - Menu sections
- `menu_items` - Dishes/items
- `menu_views` - Analytics
- `qr_codes` - QR code data

## 🐛 Troubleshooting

### If migrations fail:
```bash
# Delete db.sqlite3 file
rm db.sqlite3

# Delete migration files (keep __init__.py)
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc" -delete

# Recreate migrations
python manage.py makemigrations
python manage.py migrate
```

### If imports fail:
```bash
# Make sure you're in the VEO conda environment
conda activate VEO

# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

## 📝 Notes

- Database is SQLite by default (good for development)
- Emails will print to console (not sent)
- Debug mode is ON
- CORS allows localhost:3000 (your React frontend)

## 🎯 Success Indicators

You'll know everything is working when:
- ✅ Server runs without errors
- ✅ Admin panel loads with Jazzmin theme
- ✅ You can create instances in admin
- ✅ You can create menus in admin
- ✅ No migration warnings

After this, we'll create the API endpoints and connect the frontend!
