"""
Development settings for gitako project.
"""

from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--apu&a^%j7a*wzijr&15bb%=lza9h67mg@!7*i-^&ugu(d93eo'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_WHITELIST = [
    'http://localhost:3000',  # React frontend
    'http://localhost:8000',  # Django development server
]

# This is the correct format for ACCOUNT_SIGNUP_FIELDS when using mandatory email verification
ACCOUNT_SIGNUP_FIELDS = {
    'email': {'required': True, 'verified': True},
    'username': {'required': True},
}

# Traditional django-allauth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 3
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGIN_METHODS = ['username', 'email']
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGOUT_REDIRECT_URL = '/accounts/login/'
ACCOUNT_SESSION_REMEMBER = True


# Email settings (using console backend for development)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Set JWT_AUTH_SECURE to False for development
REST_AUTH['JWT_AUTH_SECURE'] = False