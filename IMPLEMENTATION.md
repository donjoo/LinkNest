# LinkNest - URL Shortening Platform Implementation

## Overview

This implementation provides a complete namespaced URL shortening platform with organizational privileges. The system allows users to create organizations, manage namespaces, and create short URLs with role-based access control.

## Backend Implementation (Django + DRF)

### Models Created

1. **Organization**: Represents an organization with an owner
2. **OrganizationMembership**: Manages user roles within organizations (Admin, Editor, Viewer)
3. **Namespace**: Globally unique namespaces within organizations
4. **ShortURL**: Short URLs with unique codes within namespaces

### Key Features

- **Role-based Access Control**: Admin, Editor, and Viewer roles with different permissions
- **URL Shortening Logic**: Auto-generates unique short codes or accepts custom ones
- **Click Tracking**: Tracks click counts for analytics
- **JWT Authentication**: Secure API access with token refresh
- **Admin Interface**: Django admin for managing all entities

### API Endpoints

- `GET/POST /api/organizations/` - List/create organizations
- `GET/PUT/DELETE /api/organizations/{id}/` - Organization details
- `GET/POST /api/organizations/{id}/members/` - Organization members
- `POST /api/organizations/{id}/invite_member/` - Invite users
- `GET/POST /api/namespaces/` - List/create namespaces
- `GET/PUT/DELETE /api/namespaces/{id}/` - Namespace details
- `GET/POST /api/short-urls/` - List/create short URLs
- `GET/PUT/DELETE /api/short-urls/{id}/` - Short URL details
- `GET /api/short-urls/by_namespace/?namespace_id={id}` - URLs by namespace
- `POST /api/short-urls/{id}/redirect/` - Handle redirects

### URL Redirects

Short URLs are accessible at: `/{namespace_name}/{short_code}/`

## Frontend Implementation (React + Vite)

### Components Created

1. **Dashboard**: Lists organizations with create functionality
2. **Organization**: Shows namespaces and members with tabs
3. **Namespace**: Displays short URLs with create/edit functionality

### Key Features

- **Modern UI**: Beautiful dark theme with Tailwind CSS
- **Responsive Design**: Works on desktop and mobile
- **Real-time Updates**: Immediate UI updates after API calls
- **Form Validation**: Client-side validation for all forms
- **Copy to Clipboard**: Easy sharing of short URLs
- **Role-based UI**: Different actions based on user permissions

### Navigation

- `/dashboard` - Main dashboard with organizations
- `/organizations/{id}` - Organization details page
- `/namespaces/{id}` - Namespace details page

## Setup Instructions

### Backend Setup

1. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements/local.txt
   ```

2. Set environment variables:
   ```bash
   export DATABASE_URL=sqlite:///db.sqlite3
   export CELERY_BROKER_URL=redis://localhost:6379/0
   export USE_DOCKER=no
   ```

3. Run migrations:
   ```bash
   python3 manage.py migrate
   ```

4. Start the server:
   ```bash
   python3 manage.py runserver
   ```

### Frontend Setup

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

## Usage Flow

1. **Register/Login**: Users create accounts and authenticate
2. **Create Organization**: Users can create organizations where they become admins
3. **Invite Members**: Admins can invite users with different roles
4. **Create Namespaces**: Admins and editors can create namespaces
5. **Create Short URLs**: Users can create short URLs in namespaces they have access to
6. **Share URLs**: Short URLs can be shared and will redirect to original URLs

## Role Permissions

- **Admin**: Full access to organization, can invite members, create namespaces, manage all short URLs
- **Editor**: Can create namespaces and short URLs, view organization details
- **Viewer**: Can only view organization details and short URLs

## Technical Details

- **Database**: SQLite for development (easily configurable for PostgreSQL)
- **Authentication**: JWT tokens with automatic refresh
- **CORS**: Configured for frontend-backend communication
- **API Documentation**: Available at `/api/docs/` (Swagger UI)
- **Admin Interface**: Available at `/admin/`

## Future Enhancements

- Analytics dashboard for click tracking
- Bulk URL import/export
- Custom domains for organizations
- API rate limiting
- URL expiration dates
- QR code generation
- Advanced user management features
