import re
from modelurl.importpath import importpath
from django.utils.safestring import mark_safe

MARCO_RE = re.compile(r'{@\s*(\S+)\s*(\d{1,10})\s*(\S*)\s*@}')

def MARCO_REPL(match):
    model, id, function = match.groups()
    model = importpath(model)
    id = int(id)
    try:
        obj = model.objects.get(pk=id)
    except model.DoesNotExist:
        return mark_safe('')
    if not function:
        function = 'get_absolute_url'
    url = getattr(obj, function)()
    return mark_safe(url.encode('utf-8'))

class ModelUrlMiddleware(object):
    def process_response(self, request, response):
        response.content = MARCO_RE.sub(MARCO_REPL, response.content)
        return response
