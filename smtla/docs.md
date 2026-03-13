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
- **Database Interface:** `psycopg2-binary` (PostgreSQL)
- **Static Files Serving:** WhiteNoise
- **CORS Handling:** `django-cors-headers`

## 3. Configuration Analysis (`smtla/settings.py`)

### 3.1. Database
The project connects to a PostgreSQL database using environment variables.
- **Engine:** `django.db.backends.postgresql_psycopg2`
- **Configuration:** Database credentials (`DATABASE_NAME`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_HOST`, `DATABASE_PORT`) are passed via environment variables, specifically designed for Docker and PaaS deployments.

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
- **Permissions:** `IsAuthenticated` is set as the default permission class globally, securing the API by default.
- **Security Settings (Environment Driven):**
  - `DEBUG`: Disabled by default in production (controlled via `DEBUG=1` or `DEBUG=0`).
  - `SECRET_KEY`: Loaded securely from the environment.
  - `ALLOWED_HOSTS`: Safely parsed from the environment.
- **CORS (Cross-Origin Resource Sharing):**
  - `CORS_ORIGIN_ALLOW_ALL`: Set to `False` for strict origin checking.
  - `CORS_ALLOWED_ORIGINS` & `CSRF_TRUSTED_ORIGINS`: Loaded from environment variables to strictly trust specified frontend domains.
  - `CORS_ALLOW_CREDENTIALS`: Enabled via environment variables to allow cross-origin cookies/auth headers when required.

### 3.4. JWT Settings (`SIMPLE_JWT`)
The JWT configuration is secured for production:
- **Access Token Lifetime:** 60 minutes.
- **Refresh Token Lifetime:** 7 days.
- **Auth Header:** `Bearer <token>`
- **Rotation:** Refresh token rotation is enabled (`ROTATE_REFRESH_TOKENS = True`).
- **Blacklisting:** Blacklisting after rotation is enabled to invalidate old tokens.

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

## 6. Production Enhancements Applied
The following security and deployment features have been successfully implemented:

1.  **Environment Variables:** Sensitive data, debug modes, and host configurations are completely decoupled from the source code via a `.env` file and `os.environ.get`.
2.  **Docker Ready:** A `docker-compose.yml` file is configured with health checks to orchestrate the PostgreSQL database and the Django Gunicorn backend seamlessly.
3.  **Strict Security:** Wildcard CORS and open API permissions have been replaced with strict origin lists and authentication-by-default.
4.  **Optimized JWT:** Lifespans are shortened, and token blacklisting is active to prevent session hijacking.

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