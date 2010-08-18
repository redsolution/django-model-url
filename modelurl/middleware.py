"""
Replace macro in response with absolute urls.

>>> from django.test import Client
>>> from modelurl.utils import macro
>>> from example.models import Page, Item
>>> client = Client()

# Get an object
>>> item = Item.objects.get(pk=1)
>>> item.my_url()
'/item_by_barcode/first'

# Save content with link to the object
>>> page = Page.objects.get(pk=1)
>>> page.content = '<a href="%s">link</a>' % macro(item)
>>> page.save()
>>> page.content
'<a href="{@ example.models.Item 1 @}">link</a>'

# Request content with link to the object
>>> client.get('/page_by_id/1').content
'<a href="/item_by_barcode/first">link</a>'

# Change the object
>>> item.barcode = 'changed'
>>> item.save()
>>> item.my_url()
'/item_by_barcode/changed'

# Request content with new link to the object
>>> client.get('/page_by_id/1').content
'<a href="/item_by_barcode/changed">link</a>'

# It is safe
>>> page.content = '<a href="{@ example.models.Item.objects.delete 1 @}">link</a>'
>>> page.save()
>>> client.get('/page_by_id/1').content
'<a href="">link</a>'

# It takes only macros
>>> page.content = '<a href="{@ link @}">link</a>'
>>> page.save()
>>> client.get('/page_by_id/1').content
'<a href="{@ link @}">link</a>'
"""

from django.conf import settings
from modelurl.utils import MACRO_RE, MACRO_REPL

class ModelUrlMiddleware(object):
    def process_response(self, request, response):
        if 'content-type' in response._headers:
            if list(response._headers.get('content-type', [])[1:2]) != ["%s; charset=%s" % (
                settings.DEFAULT_CONTENT_TYPE, settings.DEFAULT_CHARSET)]:
                return response
        response.content = MACRO_RE.sub(MACRO_REPL, response.content)
        return response
