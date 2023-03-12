import inspect

def myfunc():
	print(inspect.currentframe().f_code.co_name)
	return

myfunc()