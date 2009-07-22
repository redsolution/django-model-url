# -*- coding: utf-8 -*-

from django import template
from django import conf
from django.core.cache import cache
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

register = template.Library()

def import_model(path):
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        return getattr(__import__(module, {}, {}, ['']), attr)
    except ImportError, e:
        raise ImproperlyConfigured('Error importing %s: "%s"' % (path, e))

class ModelUrlNode(template.Node):
    def __init__(self, tag_name, model, id, function='"get_absolute_url"'):
        self.model = template.Variable(model)
        self.id = template.Variable(id)
        self.function = template.Variable(function)
        
    def render(self, context):
        model = self.model.resolve(context)
        model = import_model(model)
        id = self.id.resolve(context)
        try:
            obj = model.objects.get(pk=id)
        except model.DoesNotExist:
            return ''
        function = self.function.resolve(context)
        url = getattr(obj, function)()
        return url

@register.tag
def model_url(parser, token):
    splited = token.split_contents()
    if len(splited) < 3 or len(splited) > 4:
        raise template.TemplateSyntaxError, "%r tag requires 2 or 3 arguments: model id [get_absolute_url_function]" % splited[0]
    return ModelUrlNode(*splited)
