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

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.common.CommonMiddleware',
    'modelurl.middleware.ModelUrlMiddleware',
]

#django-model-url
MODELURL_MODELS = [
    {
        'model': 'example.models.Page',
    },
    {
        'model': 'example.models.Item',
        'function': 'my_url',
    },
]

MODELURL_VIEWS = [
    {
        'view': 'example.views.page_by_id',
        'context': 'page',
    },
    {
        'view': 'example.views.item_by_id',
        'context': 'item',
        'remove_query': True,
    },
    {
        'view': 'example.views.item_by_barcode',
        'context': 'item',
    },
]
