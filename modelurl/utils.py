import re

def generate_marco(model, id, function=None):
    """
    Return marco string for specified ``model`` and ``id``.
    You can specified function to be called to get absolute url.
    """
    if function:
        return '{@ %s.%s %s %s @}' % (model.__module__, model.__name__, id, function)
    else:
        return '{@ %s.%s %s @}' % (model.__module__, model.__name__, id)
    
class Replace(object):
    """
    Class to replace urls with macros.
    """

    def __init__(self, dict):
        """
        Set ``dict`` dictionary for replace operations.
        Keys must be an url.
        Value must be macro (use ``generate_marco`` function to get it).
        """
        self.source = dict
        self.dict = None
        self.list = None
        self.regexp = None
    
    def get_dict(self):
        if self.dict is None:
            self.dict = {}
            for key, value in self.source.iteritems():
                self.dict[key.lower()] = value
        return self.dict

    def get_list(self):
        """
        Return list with urls and macros.
        """
        if self.list is None:
            self.list = list(self.get_dict().iteritems())
        return self.list

    def get_regexp(self):
        """
        Return regexp for all urls.
        """
        if self.regexp is None:
            self.regexp = re.compile('|'.join(['(%s)' % re.escape(key)
                for key, value in self.get_list()]), re.IGNORECASE)
        return self.regexp

    def url(self, value):
        """
        Return marco for specified ``value``.
        Or raise KeyError exception if there is no marco for ``value``.
        """
        return self.get_dict()[value.lower()]
    
    def text(self, value):
        """
        Replace urls in ``text`` with marcos.
        """
        def replace(match):
            for index, value in enumerate(match.groups()):
                if value is not None:
                    return self.get_list()[index]
            return ''
        return self.get_regexp().sub(replace, value)
