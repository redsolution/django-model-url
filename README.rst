================
django-model-url
================

Django-model-url help you to show always correctly links to all pages even if page`s url was changed.

Why do you need it?
-------------------

Imaging that you have news page on your web site. You add a lot of links to this news from other pages.
But suddenly you need to change url to for this news page. No your must rewrite a lot of content to fix broken links.

That`s while you will need to use django-model-url.

How it works?
-------------

Before save url to your database django-model-url try to replace it with something like this ``{@ myapp.models.MyModel id @}``.
To make this django-model-url will search for view that present specified url, call it and look for object in context passed to template.

When ever such "macro-url" will appear in response it will be replaced with actual url.

Installation:
=============

In settings.py:
---------------

1. Add ``'modelurl'`` to your ``INSTALLED_APPS``.

2. Add ``'modelurl.middleware.ModelUrlMiddleware'`` to the end of ``MIDDLEWARE_CLASSES``.

3. Write list of available models to be used by django-model-url::

    MODELURL_MODELS = [
        {
            'model': 'myapp.models.MyModel',
        },
        ...
    ]

4. Write list of views that return objects of specified models.
To make possible to get object, you must specify name of your object in context passed to render template::

    MODELURL_VIEWS = [
        {
            'view': 'myapp.views.get',
            'context': 'object',
        },
    ]

You can also disable view if you don`t want to work with it:

    MODELURL_VIEWS = [
        {
            'view': 'django.contrib.admin.site.root',
            'disable': True,
        },
    ]


Usage:
======

In your models:
---------------

1. You can check single url before it will be saved::  

	from modelurl.utils import ReplaceByView
	
	class MyModel(models.Model):
	    url = models.CharField(max_length=200)
	    def save(self, *args, **kwargs):
	        self.url = ReplaceByView().url(self.url)
	        super(MyModel, self).save(*args, **kwargs)

2. You can check html before it will be saved::

	from modelurl.utils import ReplaceByView
	
	class MyModel(models.Model):
	    html = models.TextField()
	    def save(self, *args, **kwargs):
	        self.html = ReplaceByView().html(self.html)
	        super(MyModel, self).save(*args, **kwargs)

3. You can use django-model-url together with django-trusted-html to make your html correct, pretty and safe.
