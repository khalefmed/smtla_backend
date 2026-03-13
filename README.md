# SMTLA Backend Application

A robust, production-ready REST API backend for the SMTLA project, built with Django and Django REST Framework (DRF). The project features secure JWT authentication, PostgreSQL database integration, and a complete Dockerized environment for easy deployment.

## 🚀 Technology Stack

- **Language:** Python 3.11
- **Framework:** Django 5.0+
- **API Toolkit:** Django REST Framework (DRF)
- **Authentication:** Simple JWT (JSON Web Tokens)
- **Database:** PostgreSQL (`psycopg2`)
- **Server:** Gunicorn & WhiteNoise (for static files)
- **Containerization:** Docker & Docker Compose

## 📋 Prerequisites

To run this project, you will need:
- **Docker** and **Docker Compose** (Recommended)
- *OR* Python 3.11+ and a local PostgreSQL instance (for local, non-Docker development)

## ⚙️ Environment Variables

The project uses environment variables for configuration. Create a `.env` file in the root directory based on the following template:


## 🐳 Getting Started (Docker - Recommended)

1. Ensure your `.env` file is properly configured.
2. Build and start the containers in detached mode:
   ```bash
   docker-compose up -d --build
   ```
3. The Docker Compose setup will automatically:
   - Start the PostgreSQL database.
   - Run Django migrations (`python manage.py migrate`).
   - Load initial mock data (`python manage.py loaddata data.json`).
   - Collect static files.
   - Start the Gunicorn server on `http://localhost:8000`.

4. To view live logs:
   ```bash
   docker-compose logs -f backend
   ```

## 📖 Documentation

Detailed project documentation and API specifications are available in the repository:

- Project Architecture & Config Docs
- REST API Specification (Endpoints, Payloads, and Schemas)

## 🔒 Security Features

- Default API endpoints are secured via `IsAuthenticated` permission classes.
- JWT tokens are configured with optimized lifetimes (60 mins access, 7 days refresh) and blacklisting.
- CORS and CSRF protections are strictly tied to environment variables, disabling wildcard access in production.
- Production-ready static file serving via WhiteNoise.
