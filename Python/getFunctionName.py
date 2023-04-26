import inspect

def getFunctionName():
	"""
	Get the name of the current function.
	
	Returns:
		str: The name of the current function.
	"""
	return inspect.currentframe().f_back.f_code.co_name