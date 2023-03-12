import inspect

# =============================
# Usage directly in a function
# =============================
#Place this variable directly into a function to get its name:
inspect.currentframe().f_code.co_name
#Example usage:
def myfunc():
	print(f'Function Name: {inspect.currentframe().f_code.co_name}')
myfunc()
# -----------------------------


# ====================================
# Define a function to print the name
# ====================================
def get_function_name():
	"""
	Get the name of the current function.
	
	Returns:
		str: The name of the current function.
	"""
	return inspect.currentframe().f_back.f_code.co_name
#Example usage:
def testFunName():
	print(get_function_name())
testFunName()
# -----------------------------