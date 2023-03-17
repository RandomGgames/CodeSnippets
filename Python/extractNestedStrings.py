def extractNestedStrings(iterable):
    """
    Recursively extracts strings from an arbitrary nested structure of dictionaries and lists.
    
    Args:
        iterable (dict or list or str): The nested structure to extract strings from.
    
    Returns:
        list: A list of unique strings found in the input structure.
    """
    strings = []
    if type(iterable) is dict:
        for value in iterable.values():
            strings += extractNestedStrings(value)
    elif type(iterable) is list:
        for item in iterable:
            strings += extractNestedStrings(item)
    elif type(iterable) is str:
        if iterable not in strings:
            strings.append(iterable)
    return strings
