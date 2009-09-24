import os

DEBUG = False

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'modelurl.sqlite'
SITE_ID = 1

SECRET_KEY = 'woh(%=g%iu2sieo1!ztovprqr#8(s^(87tbjw61%45x)oi2n33'

ROOT_URLCONF = 'example.urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'urlmethods',
    'modelurl',
    'example',
)
