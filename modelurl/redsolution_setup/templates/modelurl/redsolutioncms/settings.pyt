# django-model-url
MIDDLEWARE_CLASSES += ['modelurl.middleware.ModelUrlMiddleware']
INSTALLED_APPS += ['modelurl']

MODELURL_MODELS = [{% for model in modelurl_settings.models.all %}
    {'model': '{{ model.model }}',},{% endfor %}
]
MODELURL_VIEWS = [
    {
        'view': 'django.contrib.admin.site.root',
        'disable': True,
    },{% for view in modelurl_settings.views.all %}
    {
    	'view': '{{ view.view }}',
    	'context': '{{ view.object }}',
	},{% endfor %}
]
