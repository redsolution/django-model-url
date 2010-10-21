================
django-model-url
================

Django-model-url helps you to show correctly links to all objects even if page`s url was changed.

Usage case
----------

For example, you have news page on your web site.
You add a lot of links to the news page from other pages.
At some time you had to change url for the news page. This action lead to the problem: all old links are broken now.
Of course, you can add redirect from old address to new. This can application solve problem more elegantly.

How it works?
-------------

Before you save content with hyperlink to your database ``django-model-url`` tries to replace it with something like this ``{@ myapp.models.MyModel id @}``.
Module will search for controller (view) that presents specified url.
If controller will be found module  calls it and looks for object in context that passed to template.

When ever such "macro-url" will appear in response it will be replaced with actual url.

Installation:
=============

In settings.py:
---------------

1. Add ``'modelurl'`` to your ``INSTALLED_APPS``.

2. Add ``'modelurl.middleware.ModelUrlMiddleware'`` to the end of ``MIDDLEWARE_CLASSES``.

3. Configure the list of available models to be used by django-model-url ::

    MODELURL_MODELS = [
        {
            'model': 'myapp.models.MyModel',
        },
        ...
    ]

4. Configure the list of views that return objects of specified models.
You must also specify the name of your context variable that represents your object ::

    MODELURL_VIEWS = [
        {
            'view': 'myapp.views.get',
            'context': 'object',
        },
    ]

You can disable view if you don`t want to work with it: ::

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

1. You can check single url by hands before saving ::  

	from modelurl.utils import ReplaceByView
	
	class MyModel(models.Model):
	    url = models.CharField(max_length=200)
	    def save(self, *args, **kwargs):
	        self.url = ReplaceByView().url(self.url)
	        super(MyModel, self).save(*args, **kwargs)

2. You can check html before saving ::

	from modelurl.utils import ReplaceByView
	
	class MyModel(models.Model):
	    html = models.TextField()
	    def save(self, *args, **kwargs):
	        self.html = ReplaceByView().html(self.html)
	        super(MyModel, self).save(*args, **kwargs)

3. You can use django-model-url together with `django-trusted-html`_ to make your html correct, pretty and safe.

Classifiers:
-------------

`Utilities`_

.. _`django-trusted-html`: http://pypi.python.org/pypi/redsolutioncms.django-trusted-html/
.. _`Utilities`: http://www.redsolutioncms.org/classifiers/utilities