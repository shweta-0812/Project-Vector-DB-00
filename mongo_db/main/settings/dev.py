# flake8: noqa
from .settings import *

DEBUG = True
ALLOWED_HOSTS = ['*']

CORS_ALLOW_ALL_ORIGINS = True

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = [
    'http://localhost:5173',  # vite FE dev server
    'http://127.0.0.1:5173',
    'http://localhost',  # vite FE dev server
    'http://127.0.0.1',
]
