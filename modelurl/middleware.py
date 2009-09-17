import re
from django.utils.safestring import mark_safe

PATTERN = re.compile(r'{@\s*(\S+)\s*(\d{1,10})\s*(\S*)\s*@}')

def import_model(path):
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        return getattr(__import__(module, {}, {}, ['']), attr)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing %s: "%s"' % (path, e))

class ModelUrlMiddleware(object):
    def process_response(self, request, response):
        def repl(match):
            model, id, function = match.groups()
            model = import_model(model)
            id = int(id)
            try:
                obj = model.objects.get(pk=id)
            except model.DoesNotExist:
                return mark_safe('')
            if not function:
                function = 'get_absolute_url'
            url = getattr(obj, function)()
            return mark_safe(url.encode('utf-8'))
        response.content = PATTERN.sub(repl, response.content)
        return response
