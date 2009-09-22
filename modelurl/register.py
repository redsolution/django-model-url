import threading
from django.template import Template

# Create local variable for all threads
local = threading.local()

def render(func):
    def wrapper(self, context):
        if hasattr(local, 'modelurl_object'):
            # We don`t want to render content if required object was found
            # for this thread.  
            return ''
        if hasattr(local, 'modelurl_object_name'):
            # We want to get object for modelurl if object_name was specified
            # for this thread.
            try:
                local.modelurl_object = context[local.modelurl_object_name]
            except KeyError:
                # Just skip it, may be we get it later.
                pass
        return func(self, context)
    return wrapper

# Register another render function to provide ReplaceByView
Template.render = render(Template.render)
