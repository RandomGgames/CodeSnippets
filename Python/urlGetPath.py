from urllib.parse import urlparse

def urlGetPath(url):
    """
    Returns the path component of a given URL.
    
    Args:
        url (str): A string representing a URL.
    
    Returns:
        str: The path component of the URL.
    """
    return urlparse(url).path