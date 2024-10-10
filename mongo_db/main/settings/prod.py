# flake8: noqa
from .settings import *
from common_utils import get_env_key

DEBUG = True

ALLOWED_HOSTS = get_env_key('ALLOWED_HOSTS', '127.0.0.1').split(',')
