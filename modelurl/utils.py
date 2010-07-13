"""
Utils to replace macro with url for specified objects.
And to replace urls with macro.
"""

import re
import threading

from django.conf import settings
from django.core.urlresolvers import RegexURLResolver
from django.template import NodeList
from django.utils.safestring import mark_safe

from urlmethods import urlsplit, urljoin, local_response_unthreaded
from urlmethods.threadmethod import threadmethod

from importpath import importpath

local = threading.local()

MACRO_RE = re.compile(r'{@\s*([.a-zA-Z]+)\s+(\S+)\s*@}')

CHECK_ELEMENTS = {
    'a': ['href', ],
    'area': ['href', ],
    'blockquote': ['cite', ],
    'del': ['cite', ],
    'img': ['src', 'longdesc', 'usemap', ],
    'ins': ['cite', ],
    'input': ['src', 'usemap', ],
    'form': ['action', ],
    'frame': ['src', 'longdesc', ],
    'iframe': ['src', 'longdesc', ],
    'link': ['href', ],
    'object': ['classid', 'codebase', 'data', 'usemap', ],
    'q': ['cite', ],
}

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

class ReplaceFailed(Exception):
    """
    Specified url can not be received.
    """

class ReplaceDone(Exception):
    """
    Specified url can not be transformed anymore.
    """

class ReplaceRedirect(Exception):
    """
    Redirect was found.
    """
    def __init__(self, target):
        self.target = target


class ReplaceByDict(object):
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
    u''

    >>> replace.url('/page_by_id/1/')
    u''

    >>> replace.url('/page_by_id/1?query')
    u''

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

    def url(self, value):
        """
        Return macro for specified ``value``.
        """
        value = value.lower()
        try:
            return self.dct[value.lower()]
        except KeyError:
            return u''

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
        response = local_response_unthreaded(path, query, False)
    except:
        raise ReplaceFailed
    if response.status_code in [301, 302]:
        raise ReplaceRedirect(response['Location'])
    if response.status_code != 200:
        raise ReplaceFailed
    try:
        return local.modelurl_object
    except AttributeError:
        raise ReplaceDone

@threadmethod()
def data_from_view(path, query):
    try:
        response = local_response_unthreaded(path, query, False)
    except:
        raise ReplaceFailed
    if response.status_code in [301, 302]:
        raise ReplaceRedirect(response['Location'])
    if response.status_code != 200:
        raise ReplaceFailed

class ReplaceByView(object):
    """
    Replace urls with macros using calling of view for specified url 
    and retrieve object from context.

    >>> replace = ReplaceByView()
    
    >>> replace.url('/page_by_id/1')
    u'{@ example.models.Page 1 @}'

    >>> replace.url('/page_by_id/11')
    u'{@ example.models.Page 11 @}'

    >>> replace.url('/page_by_id/12')
    u''

    >>> replace.url('/page_by_id/1#anchor')
    u'{@ example.models.Page 1 @}#anchor'

    >>> replace.url('/page_by_id/1?query')
    u'{@ example.models.Page 1 @}?query'

    >>> replace.url('/page_by_id/1/')
    u''

    >>> replace.url('http://another.com/page_by_id/1')
    'http://another.com/page_by_id/1'

    >>> replace.url('/item_by_barcode/second')
    u'{@ example.models.Item 2 @}'
    
    >>> replace.url('/item_by_id/2')
    u'{@ example.models.Item 2 @}'
    
    >>> replace.url('/item_by_id/12')
    u''
    
    >>> replace.url('/unavailable')
    u''

    >>> replace.url('/notfound')
    u''

    >>> replace.url('/response')
    '/response'

    >>> replace.url('/redirect_response')
    u'/response'
    
    >>> replace.url('/redirect_notfound')
    u''
    
    >>> replace.url('/redirect_redirect_response')
    u'/response'
    
    >>> replace.url('/redirect_cicle')
    u''
    
    >>> replace.url('/redirect_a_to_redirect_b_cicle')
    u''
    
    >>> replace.url('/redirect_page1')
    u'{@ example.models.Page 1 @}'
    
    >>> replace.url('/redirect_page12')
    u''
    
    >>> replace = ReplaceByView(check_unregistered=False)
    
    >>> replace.url('/unavailable')
    u''

    >>> replace.url('/notfound')
    '/notfound'

    >>> replace.url('/response')
    '/response'

    >>> replace.url('http://another.com/page_by_id/1')
    'http://another.com/page_by_id/1'

    >>> replace.html('<div>/page_by_id/1</div><a href="/page_by_id/1"><img src="/redirect_page1" /></a><a href="/unavailable"><a href="/response">inner</a></a>')
    u'<div>/page_by_id/1</div><a href="{@ example.models.Page 1 @}"><img src="{@ example.models.Page 1 @}" /></a><a href=""></a><a href="/response">inner</a>'
    """

    def __init__(self, check_sites=[], check_schemes=['http', ],
        check_unregistered=True, *args, **kwargs):
        """
        ``check_sites`` is list of site-names that are served by this server.
        Urls with such site name will be checked.
        
        ``check_schemes`` is list of schemes that are served by this server.
        Only urls with such scheme will be checked.
        
        ``check_unregistered`` indicates that unregistered views must be checked.
        If ``check_unregistered`` is True and view will not response
        function will return ''
        """
        super(ReplaceByView, self).__init__(*args, **kwargs)
        self.views = {}
        for setting in getattr(settings, 'MODELURL_VIEWS', []):
            self.views[importpath(setting['view'])] = setting
        self.check_sites = [value.lower() for value in check_sites]
        self.check_schemes = [value.lower() for value in check_schemes]
        self.check_unregistered = check_unregistered

    def url(self, value):
        """
        Return valid url or empty string.
        """
        resolver = RegexURLResolver(r'^/', settings.ROOT_URLCONF)
        checked = []
        try:
            while value not in checked:
                checked.append(value)
                if MACRO_RE.match(value):
                    if MACRO_RE.sub(MACRO_REPL, value):
                        raise ReplaceDone
                    else:
                        raise ReplaceFailed
                scheme, authority, path, query, fragment = urlsplit(value)
                if not scheme and not authority and not path:
                    raise ReplaceDone
                if (scheme and scheme.lower() not in self.check_schemes) or\
                    (authority and authority.lower() not in self.check_sites):
                    raise ReplaceDone
                try:
                    callback, callback_args, callback_kwargs = resolver.resolve(path)
                except Exception:
                    raise ReplaceFailed
                try:
                    try:
                        setting = self.views[callback]
                    except KeyError:
                        if self.check_unregistered:
                            data_from_view(path, query)
                        raise ReplaceDone
                    if setting.get('disable', False):
                        raise ReplaceFailed
                    obj = object_from_view(path, query, setting['context'])
                    path = macro(obj)
                    if setting.get('remove_query', False):
                        query = None
                    value = urljoin(None, None, path, query, fragment)
                    raise ReplaceDone
                except ReplaceRedirect, redirect:
                    value = redirect.target
                    scheme, authority, path, query, fragment = urlsplit(value)
                    if scheme == 'http' and authority == 'testserver':
                        value = urljoin(None, None, path, query, fragment)
            else:
                raise ReplaceFailed
        except ReplaceFailed:
            return u''
        except ReplaceDone:
            pass
        return value

    def html(self, value):
        """
        Return html with valid urls.
        """
        from BeautifulSoup import BeautifulSoup
        soup = BeautifulSoup(value)
        for element, attrs in CHECK_ELEMENTS.iteritems():
            for tag in soup.findAll(element):
                for attr in attrs:
                    try:
                        tag[attr] = self.url(tag[attr])
                    except KeyError:
                        pass
        return unicode(soup)
