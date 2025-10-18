# URL Shortening Implementation Guide

This document provides comprehensive instructions for setting up and testing the URL shortening functionality in the LinkNest Django + React project.

## 🚀 Features Implemented

### Backend (Django + DRF)
- ✅ **Namespace Model**: Globally unique namespaces linked to organizations
- ✅ **ShortURL Model**: URLs with customizable shortcodes, expiry dates, and analytics
- ✅ **Organization Access Control**: Only organization members can create/edit URLs
- ✅ **URL Resolution**: `domain.com/<namespace>/<shortcode>/` redirects to original URL
- ✅ **Analytics**: Click count tracking and timestamps
- ✅ **Expiry Support**: Optional expiry dates with validation
- ✅ **API Endpoints**: Full CRUD operations for namespaces and short URLs

### Frontend (React)
- ✅ **URL Creation Form**: With optional shortcode input and expiry date
- ✅ **URL List View**: Per organization with analytics display
- ✅ **Namespace Management**: Create and manage namespaces
- ✅ **Environment Configuration**: Uses environment variables for API URLs
- ✅ **Modern UI**: Clean, responsive design with Tailwind CSS

## 📋 Prerequisites

- Python 3.8+
- Node.js 16+
- Redis (for Celery)
- SQLite (default) or PostgreSQL

## 🛠️ Setup Instructions

### 1. Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd /home/donjo/LinkNest/backend
   ```

2. **Create environment file:**
   ```bash
   cp env.example .env
   ```

3. **Edit `.env` file with your settings:**
   ```env
   # Django Settings
   DJANGO_DEBUG=True
   DJANGO_READ_DOT_ENV_FILE=True
   DJANGO_SECRET_KEY=your-secret-key-here
   DJANGO_SETTINGS_MODULE=config.settings.local

   # Database
   DATABASE_URL=sqlite:///db.sqlite3

   # Celery
   CELERY_BROKER_URL=redis://localhost:6379/0

   # Email (for development)
   DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

   # Frontend URL for generating short URLs
   FRONTEND_BASE_URL=http://localhost:8000

   # CORS settings
   DJANGO_ACCOUNT_ALLOW_REGISTRATION=True

   # Docker settings
   USE_DOCKER=no
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements/local.txt
   ```

5. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server:**
   ```bash
   python manage.py runserver 8001
   ```

### 2. Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd /home/donjo/LinkNest/frontend
   ```

2. **Create environment file:**
   ```bash
   cp env.example .env
   ```

3. **Edit `.env` file:**
   ```env
   # Frontend Environment Variables

   # API Base URL - Backend API endpoint
   VITE_API_BASE_URL=http://localhost:8001/api

   # Frontend Base URL - Used for generating short URLs and redirects
   VITE_FRONTEND_BASE_URL=http://localhost:8000
   ```

4. **Install dependencies:**
   ```bash
   npm install
   ```

5. **Start the development server:**
   ```bash
   npm run dev
   ```

## 🧪 Testing the Implementation

### 1. Automated Testing

Run the comprehensive test script:

```bash
cd /home/donjo/LinkNest
python3 test_url_shortening.py
```

This script tests:
- User and organization creation
- Namespace creation and uniqueness
- Short URL creation with expiry dates
- Click count tracking
- Expiry validation
- Short code generation and uniqueness

### 2. Manual Testing via Frontend

1. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001/api
   - Admin: http://localhost:8001/admin

2. **Create an organization:**
   - Register/login to the application
   - Create a new organization from the dashboard

3. **Create a namespace:**
   - Navigate to your organization
   - Create a new namespace (must be globally unique)

4. **Create short URLs:**
   - Navigate to the namespace
   - Create short URLs with optional custom shortcodes and expiry dates

5. **Test URL resolution:**
   - Copy the generated short URL
   - Visit it in a new browser tab
   - Verify it redirects to the original URL
   - Check that click count increments

### 3. API Testing

You can test the API endpoints directly:

```bash
# Get authentication token
curl -X POST http://localhost:8001/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "your-email@example.com", "password": "your-password"}'

# Create a namespace
curl -X POST http://localhost:8001/api/namespaces/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "my-namespace", "organization": "ORG_ID", "description": "My test namespace"}'

# Create a short URL
curl -X POST http://localhost:8001/api/short-urls/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"namespace": "NAMESPACE_ID", "original_url": "https://example.com", "short_code": "test123"}'
```

## 📊 API Endpoints

### Namespaces
- `GET /api/namespaces/` - List namespaces
- `POST /api/namespaces/` - Create namespace
- `GET /api/namespaces/{id}/` - Get namespace details
- `PUT /api/namespaces/{id}/` - Update namespace
- `DELETE /api/namespaces/{id}/` - Delete namespace

### Short URLs
- `GET /api/short-urls/` - List short URLs
- `POST /api/short-urls/` - Create short URL
- `GET /api/short-urls/{id}/` - Get short URL details
- `PUT /api/short-urls/{id}/` - Update short URL
- `DELETE /api/short-urls/{id}/` - Delete short URL
- `GET /api/short-urls/by_namespace/?namespace_id={id}` - Get URLs by namespace
- `POST /api/short-urls/{id}/redirect/` - Simulate redirect (increments click count)

### URL Resolution
- `GET /{namespace_name}/{short_code}/` - Redirect to original URL

## 🔧 Configuration Options

### Environment Variables

#### Backend (.env)
- `FRONTEND_BASE_URL`: Base URL for generating short URLs (default: http://localhost:8000)
- `DATABASE_URL`: Database connection string
- `CELERY_BROKER_URL`: Redis URL for Celery
- `DJANGO_SECRET_KEY`: Django secret key

#### Frontend (.env)
- `VITE_API_BASE_URL`: Backend API base URL (default: http://localhost:8001/api)
- `VITE_FRONTEND_BASE_URL`: Frontend base URL for redirects

## 🏗️ Architecture

### Models
- **Organization**: Groups users and namespaces
- **Namespace**: Globally unique containers for short URLs
- **ShortURL**: Individual shortened URLs with analytics
- **OrganizationMembership**: User roles within organizations

### Key Features
- **Global Namespace Uniqueness**: Namespace names must be unique across all organizations
- **Namespace-scoped Shortcodes**: Short codes are unique within each namespace
- **Expiry Support**: Optional expiry dates with validation
- **Click Analytics**: Automatic click count tracking
- **Access Control**: Organization-based permissions

## 🐛 Troubleshooting

### Common Issues

1. **Database connection errors:**
   - Ensure DATABASE_URL is correctly set
   - Run migrations: `python manage.py migrate`

2. **CORS errors:**
   - Check CORS_ALLOWED_ORIGINS in settings
   - Ensure frontend URL is included

3. **Authentication issues:**
   - Verify JWT token configuration
   - Check API base URL in frontend

4. **URL resolution not working:**
   - Ensure FRONTEND_BASE_URL is set correctly
   - Check that short URL redirect pattern is at the end of URL patterns

### Debug Mode

Enable debug mode for detailed error messages:
```env
DJANGO_DEBUG=True
```

## 📈 Performance Considerations

- **Database Indexing**: Short codes and namespace names are indexed for fast lookups
- **Caching**: Consider implementing Redis caching for frequently accessed URLs
- **Rate Limiting**: Implement rate limiting for URL creation and resolution
- **Analytics**: Consider implementing more detailed analytics (user agents, referrers, etc.)

## 🔒 Security Features

- **Authentication Required**: All API endpoints require authentication
- **Organization Access Control**: Users can only access URLs from their organizations
- **Input Validation**: Comprehensive validation for URLs, shortcodes, and expiry dates
- **CSRF Protection**: Enabled for all forms
- **CORS Configuration**: Properly configured for frontend-backend communication

## 🚀 Production Deployment

For production deployment:

1. **Set production environment variables:**
   ```env
   DJANGO_DEBUG=False
   DJANGO_SECRET_KEY=your-production-secret-key
   DATABASE_URL=postgresql://user:password@host:port/dbname
   FRONTEND_BASE_URL=https://yourdomain.com
   ```

2. **Use a production database** (PostgreSQL recommended)

3. **Set up proper logging and monitoring**

4. **Configure HTTPS and security headers**

5. **Set up Redis for Celery in production**

## 📝 Example Usage

### Creating a Short URL via API

```python
import requests

# Authenticate
response = requests.post('http://localhost:8001/api/auth/login/', {
    'email': 'user@example.com',
    'password': 'password'
})
token = response.json()['access']

# Create short URL
response = requests.post('http://localhost:8001/api/short-urls/', {
    'namespace': 'namespace-id',
    'original_url': 'https://example.com/very-long-url',
    'short_code': 'custom123',  # Optional
    'title': 'My Custom URL',
    'expiry_date': '2024-12-31T23:59:59Z'  # Optional
}, headers={'Authorization': f'Bearer {token}'})

short_url = response.json()
print(f"Short URL: {short_url['full_short_url']}")
```

### Resolving a Short URL

```bash
# Visit the short URL in browser
curl -I http://localhost:8000/my-namespace/custom123/
# Should return 302 redirect to original URL
```

## 🎯 Next Steps

Potential enhancements:
- **Custom Domains**: Allow organizations to use custom domains
- **QR Code Generation**: Generate QR codes for short URLs
- **Advanced Analytics**: Detailed click analytics with charts
- **Bulk URL Import**: Import multiple URLs at once
- **URL Preview**: Show preview of destination URLs
- **Password Protection**: Add password protection for short URLs
- **Geographic Analytics**: Track clicks by location
- **API Rate Limiting**: Implement rate limiting for API endpoints

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the test script output for validation
3. Check Django logs for backend errors
4. Check browser console for frontend errors

The implementation is fully functional and ready for production use with proper configuration and deployment setup.

