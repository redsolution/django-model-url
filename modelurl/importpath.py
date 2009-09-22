def importpath(path, error_text=None):
    """
    Import object by specified ``path``.
    If ``error_text`` is not None and import raise an error
    then will raise ImproperlyConfigured with user friendly text.
    """
    i = path.rfind('.')
    module, attr = path[:i], path[i+1:]
    try:
        return getattr(__import__(module, {}, {}, ['']), attr)
    except ImportError, error:
        if error_text is not None:
            from django.core.exceptions import ImproperlyConfigured
            raise ImproperlyConfigured('Error importing %s from %s: "%s"' % (error_text, path, error))
        else:
            raise error
