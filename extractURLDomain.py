import logging
from urllib.parse import urlparse

def extractURLDomain(url):
	"""
	Extracts the domain name from a given URL.
	For example: 'https://www.google.com/' would return 'google'
	
	Args:
		url (str): The URL to extract the domain name from.
	
	Returns:
		str: The domain name of the given URL.
	"""
	
	logging.debug(f'Getting domain from "{url}"')
	try:
		if not isinstance(url, str):
			logging.exception(f'Input is not a string.')
			raise TypeError("Input must be a string.")
		
		parsed_url = urlparse(url)
		domain = parsed_url.netloc.split(".")
		
		if domain[0] == 'www':
			domain = domain[1]
		else:
			domain = domain[0]
		logging.debug(f'Got domain "{domain}"')
		return domain
	
	except Exception as e:
		logging.exception(f"Error extracting domain from {url}: {repr(e)}")
		return None