import requests

def makeURLRequest(url: str, params: dict = {}, headers: dict = {}):
    """
    Sends a GET request to a URL endpoint with optional query parameters and headers.
    
    Args:
        request_base (str): The URL endpoint to send the request to.
        paramaters (dict, optional): A dictionary of query parameters to include in the request. Defaults to {}.
        headers (dict, optional): A dictionary of headers to include in the request. Defaults to {}.
    
    Returns:
        dict or None: A dictionary of the response data, or None if the request fails.
    """
    try:
        response = requests.get(url, params = params, headers = headers)
        response.raise_for_status() #raise an HTTPError for 4xx and 5xx status codes
        return response
    except requests.exceptions.RequestException as e:
        raise e
    except Exception as e:
        raise e