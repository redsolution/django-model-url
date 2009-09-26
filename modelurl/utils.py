"""
Utils to replace macro with url for specified objects.
And to replace urls with macro.
"""

import re
import threading

from django.conf import settings
from django.contrib.sites.models import Site
from django.core.urlresolvers import RegexURLResolver
from django.template import NodeList
from django.utils.safestring import mark_safe

from urlmethods import urlsplit, urljoin, local_response_unthreaded
from urlmethods.threadmethod import threadmethod

from importpath import importpath

local = threading.local()

MACRO_RE = re.compile(r'{@\s*([.a-zA-Z]+)\s+(\S+)\s*@}')

def MACRO_REPL(match):
    """
    Replace function for macro.
    
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

def macro(obj):
    """
    Return macro string for specified ``obj``.
    
    >>> from example.models import Page
    >>> from modelurl.middleware import MACRO_RE
    
    >>> page = Page.objects.get(pk=1)
    >>> macro(page)
    '{@ example.models.Page 1 @}'

    >>> bool(MACRO_RE.match(macro(page)))
    True
    """
    return '{@ %s.%s %s @}' % (obj.__class__.__module__, obj.__class__.__name__, obj.pk)

class ReplaceException(Exception):
    """
    Base exception class.
    """
    pass

class DoesNotFoundException(ReplaceException):
    """
    Specified that url was not found.
    """
    pass

class UnregisteredException(ReplaceException):
    """
    Specified that url exists but wasn`t registered in MODELURL_VIEWS.
    """
    pass

class AlreadyMacroException(ReplaceException):
    """
    Specified that url already is macro.
    """
    pass

class NoPathException(ReplaceException):
    """
    Url has no path (only anchor or/and query).
    """
    pass

class ForeignException(ReplaceException):
    """
    Url has link to the foreign site.
    """
    pass


class BaseReplace(object):
    """
    Base class to replace urls.
    """
    
    def __init__(self, silent=False):
        """
        If ``silent`` is True then instance of this class must
        raise exceptions when urls can`t be replaces with macro.
        
        If ``silent`` is False then instance of this class must
        return source value.
        """
        self.silent = silent


def silentmethod(func):
    """
    Decorator to make function silent if specified
    """
    def wrapper(self, value, *args, **kwargs):
        try:
            return func(self, value, *args, **kwargs)
        except ReplaceException, exception:
            if self.silent:
                return value
            else:
                raise exception
    return wrapper


class ReplaceByDict(BaseReplace):
    """
    Replace urls with macros using dictionary.
    
    >>> from example.models import Page, Item
    
    >>> dictionary = {}
    >>> for page in Page.objects.all():
    ...     dictionary[page.get_absolute_url()] = macro(page)
    ...
    >>> for item in Item.objects.all():
    ...     dictionary[item.my_url()] = macro(item)
    ...
    >>> replace = ReplaceByDict(dictionary)
    
    >>> replace.url('/page_by_id/1')
    '{@ example.models.Page 1 @}'

    >>> replace.url('/page_by_id/11')
    '{@ example.models.Page 11 @}'

    >>> replace.url('/page_by_id/12')
    Traceback (most recent call last):
        ...
    DoesNotFoundException

    >>> replace.url('/page_by_id/1/')
    Traceback (most recent call last):
        ...
    DoesNotFoundException

    >>> replace.url('/page_by_id/1?query')
    Traceback (most recent call last):
        ...
    DoesNotFoundException

    >>> replace.text('<a href="/page_by_id/1">page</a> and /page_by_id/1 ')
    '<a href="{@ example.models.Page 1 @}">page</a> and {@ example.models.Page 1 @} '

    >>> replace.text('<a href=/page_by_id/1>page</a> and /page_by_id/1')
    '<a href={@ example.models.Page 1 @}>page</a> and {@ example.models.Page 1 @}'

    >>> replace.text("<a href='/page_by_id/1'>page</a> and /page_by_id/1/another")
    "<a href='{@ example.models.Page 1 @}'>page</a> and /page_by_id/1/another"

    >>> replace.text('<a href="/page_by_id/1#anchor">page</a> and /page_by_id/1?query')
    '<a href="{@ example.models.Page 1 @}#anchor">page</a> and {@ example.models.Page 1 @}?query'

    >>> replace.text('<a href="/page_by_id/1/">page</a> and /page_by_id/1/?query')
    '<a href="/page_by_id/1/">page</a> and /page_by_id/1/?query'

    >>> replace.text('<a href="http://another.com/page_by_id/1">page</a> and /page_by_id/11')
    '<a href="http://another.com{@ example.models.Page 1 @}">page</a> and {@ example.models.Page 11 @}'

    >>> replace.text('<a href="/page_by_id/12">page</a> and /item_by_barcode/second')
    '<a href="/page_by_id/12">page</a> and {@ example.models.Item 2 @}'
    """

    def __init__(self, dict, *args, **kwargs):
        """
        Set ``dict`` dictionary for replace operations.
        Keys must be an url.
        Value must be macro (use ``modelurl.generate_macro`` function to get it).
        """
        super(ReplaceByDict, self).__init__(*args, **kwargs)
        self.source = dict
        self._dct = None
        self._lst = None
        self._regexp = None
    
    @property
    def dct(self):
        if self._dct is None:
            self._dct = {}
            for key, value in self.source.iteritems():
                self._dct[key.lower()] = value
        return self._dct

    @property
    def lst(self):
        """
        Return list with urls and macros.
        """
        if self._lst is None:
            self._lst = list(self.dct.iteritems())
            self._lst.sort(reverse=True)
        return self._lst

    @property
    def regexp(self):
        """
        Return regexp for all urls.
        """
        if self._regexp is None:
            self._regexp = re.compile(r'''(%s)(?=\s|[#?"'>]|$)''' % 
                '|'.join(['(%s)' % re.escape(key)
                    for key, value in self.lst]),
                re.IGNORECASE)
        return self._regexp

    @silentmethod
    def url(self, value):
        """
        Return macro for specified ``value``.
        """
        value = value.lower()
        try:
            return self.dct[value.lower()]
        except KeyError:
            raise DoesNotFoundException
    
    def text(self, value):
        """
        Replace urls in ``text`` with macros.
        """
        def replace(match):
            length = len(self.lst)
            for index, value in enumerate(match.groups()):
                if index == 0 or index > length:
                    continue
                if value is not None:
                    return self.lst[index - 1][1]
            return ''
        return self.regexp.sub(replace, value)

def render(func):
    """
    Replacement for NodeList.render to
    provide fetching objects for ReplaceByView
    
    # render_by_model_url flag must be already set  
    >>> hasattr(NodeList, 'render_by_model_url') 
    True

    >>> from time import sleep
    >>> from django.template import Template, Context
    
    # Thread without object_name
    >>> @threadmethod(return_immediately=True)
    ... def normal(before, after):
    ...     sleep(before)
    ...     template = Template('{{ page }}{{ item }}{{ data }}')
    ...     template.render(Context({'page': 1, 'item': 2, 'data': 3}))
    ...     sleep(after)
    ...     return 0
    ...

    # Thread with object_name 'page'
    >>> @threadmethod(return_immediately=True)
    ... def page(before, after):
    ...     local.modelurl_object_name = 'page'
    ...     sleep(before)
    ...     template = Template('{{ page }}{{ item }}{{ data }}')
    ...     template.render(Context({'page': 1, 'item': 2, 'data': 3}))
    ...     sleep(after)
    ...     return local.modelurl_object
    ...

    # Thread with object_name 'item'
    >>> @threadmethod(return_immediately=True)
    ... def item(before, after):
    ...     local.modelurl_object_name = 'item'
    ...     sleep(before)
    ...     template = Template('{{ page }}{{ item }}{{ data }}')
    ...     template.render(Context({'page': 1, 'item': 2, 'data': 3}))
    ...     sleep(after)
    ...     return local.modelurl_object
    ...

    # Thread with object_name 'page' and number of render calls
    >>> @threadmethod(return_immediately=True)
    ... def calls(before, after):
    ...     local.modelurl_object_name = 'page'
    ...     sleep(before)
    ...     template = Template('{{ item }}{{ data }}')
    ...     template.render(Context({'item': 1, 'data': 2}))
    ...     template = Template('{{ page }}{{ item }}{{ data }}')
    ...     template.render(Context({'page': 3, 'item': 4, 'data': 5}))
    ...     template = Template('{{ page }}{{ item }}{{ data }}')
    ...     template.render(Context({'page': 6, 'item': 7, 'data': 8}))
    ...     sleep(after)
    ...     return local.modelurl_object
    
    # Start them all
    >>> ti = item(0.4, 0.1)
    >>> tg = page(0.3, 0.2)
    >>> tn = normal(0.2, 0.3)
    >>> tc = calls(0.1, 0.4)
    >>> ti.join()
    >>> tg.join()
    >>> tn.join()
    >>> tc.join()
    >>> tn.result
    0
    >>> tg.result
    1
    >>> ti.result
    2
    >>> tc.result
    3
    """
    if not getattr(settings, 'MODELURL_VIEWS', []):
        return func
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
    
# Create lock to update NodeList only once
lock = threading.Lock()
lock.acquire()
if not hasattr(NodeList, 'render_by_model_url'):
    # Register another render function to provide ReplaceByView
    # It will be more correctly to wrap Template.render
    # but django.test.instrumented_test_render does not call it
    # so we will wrap NodeList.render
    NodeList.render = render(NodeList.render)
    NodeList.render_by_model_url = True
lock.release()

@threadmethod()
def object_from_view(path, query, object_name):
    local.modelurl_object_name = object_name
    try:
        response = local_response_unthreaded(path, query)
        if response.status_code != 200:
            raise DoesNotFoundException
    except:
        raise DoesNotFoundException
    try:
        return local.modelurl_object
    except AttributeError:
        raise DoesNotFoundException

class ReplaceByView(BaseReplace):
    """
    Replace urls with macros using calling of view for specified url 
    and retrieve object from context.
    
    >>> replace = ReplaceByView()
    
    >>> replace.url('/page_by_id/1')
    u'{@ example.models.Page 1 @}'

    >>> replace.url('/page_by_id/11')
    u'{@ example.models.Page 11 @}'

    >>> replace.url('/page_by_id/12')
    Traceback (most recent call last):
        ...
    DoesNotFoundException

    >>> replace.url('/notfound')
    Traceback (most recent call last):
        ...
    DoesNotFoundException

    >>> replace.url('/response')
    Traceback (most recent call last):
        ...
    DoesNotFoundException

    >>> replace.url('/page_by_id/1#anchor')
    u'{@ example.models.Page 1 @}#anchor'

    >>> replace.url('/page_by_id/1?query')
    u'{@ example.models.Page 1 @}?query'

    >>> replace.url('/page_by_id/1/')
    Traceback (most recent call last):
        ...
    DoesNotFoundException

    >>> replace.url('http://another.com/page_by_id/1')
    Traceback (most recent call last):
        ...
    ForeignException
    
    >>> replace.url('/item_by_barcode/second')
    u'{@ example.models.Item 2 @}'
    
    >>> replace.url('/item_by_id/2')
    u'{@ example.models.Item 2 @}'
    """
    
    def __init__(self, check_sites=[], check_schemes=['http', ],
        send_query=False, *args, **kwargs):
        super(ReplaceByView, self).__init__(*args, **kwargs)
        self.views = {}
        for setting in getattr(settings, 'MODELURL_VIEWS', []):
            self.views[importpath(setting['view'])] = setting
        self.check_sites = [value.lower() for value in check_sites]
        self.check_schemes = [value.lower() for value in check_schemes]
        self.send_query = send_query

    @silentmethod
    def url(self, value):
        if MACRO_RE.match(value):
            raise AlreadyMacroException
        scheme, authority, path, query, fragment = urlsplit(value)
        if not scheme and not authority and not path:
            raise NoPathException
        if (scheme and scheme.lower() not in self.check_schemes) or\
            (authority and authority.lower() not in self.check_sites):
            raise ForeignException
        resolver = RegexURLResolver(r'^/', settings.ROOT_URLCONF)
        try:
            callback, callback_args, callback_kwargs = resolver.resolve(path)
        except Exception:
            raise DoesNotFoundException
        try:
            setting = self.views[callback]
        except KeyError:
            raise UnregisteredException
        obj = object_from_view(path, query, setting['context'])
        path = macro(obj)
        if setting.get('remove_query', False):
            query = None
        value = urljoin(None, None, path, query, fragment)
        return value
