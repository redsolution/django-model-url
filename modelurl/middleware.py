import re
from django.utils.safestring import mark_safe

#PATTERN = re.compile(r'{@\s*?(\S+?)\s*?(\d{1,9})\s*?@}')
#
#class CsrfMiddleware(object):
#    def process_response(self, request, response):
#        def add_csrf_field(match):
#            return mark_safe("asd<a>s</a>d")
#
#        # Modify any POST forms
#        response.content = PATTERN.sub(add_csrf_field, response.content)
#        return response

PATTERN = re.compile(r'{@\s*?(\S+?)\s*?(\d{1,9})\s*?@}')

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
            model, id = match.groups()
            model = import_model(model)
            id = int(id)
            try:
                obj = model.objects.get(pk=id)
            except model.DoesNotExist:
                return mark_safe('')
            url = obj.get_absolute_url()
            print repr(url)
            return mark_safe("asd<a>s</a>d")
        response.content = PATTERN.sub(repl, response.content)
        return response
