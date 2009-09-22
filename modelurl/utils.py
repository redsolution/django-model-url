def generate_marco(model, id, function=None):
    """
    Return marco string for specified ``model`` and ``id``.
    You can specified function to be called to get absolute url.
    """
    if function:
        return '{@ %s.%s %s %s @}' % (model.__module__, model.__name__, id, function)
    else:
        return '{@ %s.%s %s @}' % (model.__module__, model.__name__, id)
