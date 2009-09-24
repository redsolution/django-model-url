"""
Replace macro in response with absolute urls.

>>> bool(MACRO_RE.match('{@ example.models.Page 1 @}'))
True

>>> bool(MACRO_RE.match('{@ example.models.DoesNotExists 1 @}'))
True

>>> bool(MACRO_RE.match('{@ 1 @}'))
False

>>> MACRO_RE.sub(MACRO_REPL, '<a href="{@ example.models.Page 1 @}">Page</a>')
'<a href="/page_by_id/1">Page</a>'

>>> MACRO_RE.sub(MACRO_REPL, '<a href="{@ example.models.DoesNotExists 1 @}">Page</a>') 
'<a href="">Page</a>'

>>> MACRO_RE.sub(MACRO_REPL, '<a href="{@ 1 @}">Page</a>') 
'<a href="{@ 1 @}">Page</a>'

>>> MACRO_RE.sub(MACRO_REPL, '<a href="{@ example-models-Page 1 @}">Page</a>')
'<a href="{@ example-models-Page 1 @}">Page</a>'

>>> (MACRO_RE.sub(MACRO_REPL, u'<a href="{@ example.models.Page 1 @}">\u00a0</a>') ==
... u'<a href="/page_by_id/1">\u00a0</a>')
True

"""

import re
from modelurl.importpath import importpath
from django.utils.safestring import mark_safe
from django.conf import settings

MACRO_RE = re.compile(r'{@\s*([.a-zA-Z]+)\s*(\S+)\s*@}')

def MACRO_REPL(match):
    model, pk = match.groups()
    for setting in getattr(settings, 'MODELURL_MODELS', []):
        if model == setting.get('model', ''):
            function = setting.get('function', 'get_absolute_url')
            break
    else:
        return mark_safe('')
    model = importpath(model)
    try:
        obj = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return mark_safe('')
    if not function:
        function = 'get_absolute_url'
    url = getattr(obj, function)()
    return mark_safe(url.encode('utf-8'))

class ModelUrlMiddleware(object):
    def process_response(self, request, response):
        response.content = MACRO_RE.sub(MACRO_REPL, response.content)
        return response
