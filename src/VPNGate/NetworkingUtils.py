try:
	import requests
except Exception:
	print(f"Module 'requests' is not installed")
	print(f"You can install it by running")
	print(f"pip install requests")
	quit()


def make_request(url: str, verbose=True) -> object:
	"""
	Parameters:
		verbose: if set, funciton will print error messages

	Returns:
		Response
		None

	No Throw
	"""

	resp = None
	try:
		resp = requests.get(url)
	except Exception as e:
		if verbose:
			print(f"Request failed:\n  '{url}'\n  {str(e)}")
		return None
	if not resp:
		if verbose:
			print(f"Request failed:\n  '{url}'\n  status code: {resp.status_code}")
		return None
	return resp


def ping(addr: str, count=1, timeout=1) -> float:
	"""
	Throws:
		Network related exceptions
	"""

	raise NotImplementedError('ping() is not implemented yet')
