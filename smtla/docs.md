# SMTLA Backend Project Documentation

## 1. Project Overview
**Project Name:** `smtla`
**Type:** Django Backend Application
**Description:** This project is a backend application built with Django (v4.2) and Django REST Framework, configured to serve APIs with JWT authentication. It appears to be designed to support a frontend application (likely running on localhost:3000 during development).

## 2. Technology Stack
- **Language:** Python
- **Web Framework:** Django 4.2
- **API Framework:** Django REST Framework (DRF)
- **Authentication:** Simple JWT (JSON Web Tokens)
- **Database Interface:** `dj_database_url` (Supports SQLite, PostgreSQL, etc.)
- **Static Files Serving:** WhiteNoise
- **CORS Handling:** `django-cors-headers`

## 3. Configuration Analysis (`smtla/settings.py`)

### 3.1. Database
The project uses `dj_database_url` to configure the database connection.
- **Default:** SQLite (`db.sqlite3` in the base directory) with a connection max age of 600 seconds.
- **Configuration:** The setup allows for database credentials to be passed via environment variables, which is standard for PaaS deployments (like Render or Heroku).

### 3.2. Installed Applications
**Third-Party Apps:**
- `rest_framework`: Toolkit for building Web APIs.
- `rest_framework_simplejwt.token_blacklist`: Provides token management and blacklisting capabilities.
- `corsheaders`: Handles Cross-Origin Resource Sharing headers.

**Local Apps:**
- `api`: The core custom application containing the project's specific logic.

### 3.3. Authentication & Security
- **User Model:** The project uses a custom user model defined as `api.Utilisateur`.
- **Authentication Mechanism:** `JWTAuthentication` via `rest_framework_simplejwt`.
- **Permissions:** `AllowAny` is set as the default permission class globally.
  > **Note:** This makes all endpoints public by default. It is recommended to change this to `IsAuthenticated` for production.
- **CORS (Cross-Origin Resource Sharing):**
  - `CORS_ORIGIN_ALLOW_ALL = True`: Allows requests from any origin.
  - `CSRF_TRUSTED_ORIGINS`: Specifically trusts `http://localhost:3000`.

### 3.4. JWT Settings (`SIMPLE_JWT`)
The JWT configuration is quite specific:
- **Access Token Lifetime:** 365 days. (Unusually long; typically short-lived).
- **Refresh Token Lifetime:** 400 days.
- **Auth Header:** `Bearer <token>`
- **Rotation:** Refresh token rotation is disabled (`ROTATE_REFRESH_TOKENS = False`).

### 3.5. Static and Media Files
- **Static URL:** `/static/`
- **Media URL:** `/media/`
- **Storage:** `whitenoise.storage.CompressedStaticFilesStorage` is used, indicating that WhiteNoise handles static file serving, optimized for production performance.

## 4. URL Routing (`smtla/urls.py`)
The project defines the following primary route structures:
- `/admin/`: Standard Django Administration interface.
- `/api/`: Root entry point for the application APIs (delegates to `api.urls`).
- **Media Files:** Served manually via `static()` helper when `DEBUG` is True.

## 5. Deployment & Runtime
- **WSGI:** Configured in `smtla/wsgi.py` for standard synchronous servers (e.g., Gunicorn).
- **ASGI:** Configured in `smtla/asgi.py` for asynchronous server support (e.g., Uvicorn, Daphne).
- **Middleware:** Includes `WhiteNoiseMiddleware` for static files and `CorsMiddleware` for cross-origin requests, placed correctly before `CommonMiddleware`.

## 6. Recommendations for Production
Based on the file analysis, the following should be reviewed before going live:

1.  **Debug Mode:** `DEBUG = True` is currently set in `settings.py`. This must be set to `False` in production.
2.  **Secret Key:** The `SECRET_KEY` is hardcoded. It should be loaded from environment variables.
3.  **Permissions:** The default `AllowAny` permission is insecure for most APIs. Consider switching to `IsAuthenticated` and selectively allowing public access.
4.  **JWT Lifetime:** An access token lifetime of 365 days negates the security benefits of JWTs. Consider shortening it (e.g., 15-60 minutes) and relying on the refresh token flow.
5.  **CORS:** `CORS_ORIGIN_ALLOW_ALL = True` is risky. Restrict `CORS_ALLOWED_ORIGINS` to known frontend domains.

## 7. File Structure Summary
```text
smtla-backend/
├── smtla/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/
│   ├── admin/
│   └── rest_framework/
└── api/ (inferred)
```