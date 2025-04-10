#!/bin/bash

# Create the main project directory structure
mkdir -p gitako/settings
mkdir -p apps/{accounts,farms,activities,recommendations,marketplace,inventory,financials}/tests
mkdir -p core
mkdir -p api/v1
mkdir -p services/{weather,maps,payments}
mkdir -p tasks
mkdir -p templates/admin
mkdir -p static/admin

# Create __init__.py files in all Python packages
find . -type d -not -path "*/\.*" -exec touch {}/__init__.py \;

# Create the Django project
django-admin startproject gitako .

# Move settings to the settings directory
mv gitako/settings.py gitako/settings/base.py
touch gitako/settings/{__init__.py,development.py,production.py}

# Create Django apps
for app in accounts farms activities recommendations marketplace inventory financials; do
    django-admin startapp $app apps/$app
    # Update apps.py to reflect the correct app name
    sed -i '' "s/name = '$app'/name = 'apps.$app'/" apps/$app/apps.py
    # Create additional files needed for each app
    touch apps/$app/serializers.py
    touch apps/$app/urls.py
done

# Create core files
touch core/{authentication.py,permissions.py,pagination.py,utils.py}

# Create API files
touch api/middleware.py
touch api/v1/urls.py

# Create service files
touch services/weather/client.py
touch services/maps/client.py
touch services/payments/client.py

# Create task files
touch tasks/{celery.py,notifications.py,scheduled_tasks.py}

# Create basic requirements.txt
echo "Django>=5.2
djangorestframework>=3.16.0
psycopg2-binary>=2.9.5
python-dotenv>=1.0.0
celery>=5.3.0
redis>=4.5.0
Pillow>=9.5.0
django-cors-headers>=4.0.0
drf-yasg>=1.21.0
django-filter>=23.0
djangorestframework-simplejwt>=5.2.0
" > requirements.txt

# Create .env file
echo "# Django settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database settings
DATABASE_URL=postgres://postgres:postgres@db:5432/gitako

# Redis settings
REDIS_URL=redis://redis:6379/0

# Celery settings
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# External APIs
WEATHER_API_KEY=your-weather-api-key
MAPS_API_KEY=your-maps-api-key
PAYMENT_API_KEY=your-payment-api-key
" > .env

# Create .gitignore
echo "# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/
staticfiles/

# Environment variables
.env
.venv
env/
venv/
ENV/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db
" > .gitignore

# Create Docker files
echo "FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Run gunicorn
CMD [\"gunicorn\", \"--bind\", \"0.0.0.0:8000\", \"gitako.wsgi\"]
" > Dockerfile

echo "version: '3.8'

services:
  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - \"8000:8000\"
    env_file:
      - .env
    depends_on:
      - db
      - redis
    networks:
      - gitako_network

  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data/
    environment:
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_USER=postgres
      - POSTGRES_DB=gitako
    networks:
      - gitako_network

  redis:
    image: redis:7
    networks:
      - gitako_network

  celery:
    build: .
    command: celery -A tasks worker -l INFO
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      - web
      - redis
    networks:
      - gitako_network

  celery-beat:
    build: .
    command: celery -A tasks beat -l INFO
    volumes:
      - .:/app
    env_file:
      - .env
    depends_on:
      - web
      - redis
    networks:
      - gitako_network

networks:
  gitako_network:

volumes:
  postgres_data:
" > docker-compose.yml

echo "Setup complete!"