# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Django REST API project for a video clip sharing and contest platform. The application allows users to upload video clips, participate in contests, rate videos, and comment on content. It uses MinIO for object storage, PostgreSQL for the database, and includes Celery for background task processing.

## Development Setup

### Environment Setup
```bash
# Create virtual environment (one time only)
python -m venv .venv

# Activate virtual environment
# PowerShell:
.venv\Scripts\Activate.ps1
# CMD:
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Database Setup
```bash
# Run database migrations
python manage.py makemigrations
python manage.py migrate
```

### Docker Services
```bash
# Start PostgreSQL, pgAdmin, and MinIO services
docker compose up -d
```

### Development Server
```bash
# Start Django development server
python manage.py runserver
```

## Key Commands

### Development
- `python manage.py runserver` - Start development server
- `python manage.py makemigrations` - Create database migrations
- `python manage.py migrate` - Apply database migrations
- `python manage.py createsuperuser` - Create admin user
- `python manage.py collectstatic` - Collect static files

### Docker
- `docker compose up -d` - Start all services in background
- `docker compose down` - Stop all services
- `docker compose logs [service]` - View service logs

### Custom Management Commands
- `python manage.py close_contests` - Close expired contests
- `python manage.py test_spareggio` - Test playoff functionality

## Architecture

### Project Structure
- `project_clip/` - Django project configuration
- `cs_clips/` - Main application containing all business logic
  - `models/` - Data models (User, Video, Contest, Comment, Rating)
  - `api/` - REST API endpoints organized by feature
  - `management/commands/` - Custom Django management commands
  - `utils/` - Utility functions and helpers
  - `scheduler.py` - Background task scheduling

### Key Models
- **User** - Custom user model for authentication
- **Video** - Video uploads with metadata and contest association
- **Contest** - Video contests with categories and time limits
- **Comment** - User comments on videos
- **Rating** - User ratings for videos

### API Structure
The API is organized into feature-based modules:
- `/api/comments/` - Comment management
- `/api/contests/` - Contest operations
- Video, user, and rating endpoints follow similar patterns

### Storage
- **MinIO** - Object storage for video files and media
- **PostgreSQL** - Primary database
- Media files are stored in MinIO buckets with automatic backup

### Background Processing
- Uses APScheduler for task scheduling
- Celery with Redis for async task processing
- Automatic contest closure based on schedules

## Environment Configuration

Copy `.env.example` to `.env` and configure:
- Database connection settings
- MinIO storage credentials
- Django secret key and debug settings
- Service ports and container names

## API Documentation

Swagger documentation available at: `http://127.0.0.1:8000/api/docs/`

## Services

### Development Services (Docker)
- **PostgreSQL** (port 5432) - Primary database
- **pgAdmin** (port 8080) - Database administration
- **MinIO** (port 9000) - Object storage API
- **MinIO Console** (port 9001) - Storage administration

### Dependencies
Key Python packages:
- Django 5.1.6 with DRF for API development
- MinIO SDK for object storage
- Celery + Redis for background tasks
- APScheduler for cron-like scheduling
- MoviePy for video processing
- Spectacular for API documentation