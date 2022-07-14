try:
	import requests
except Exception:
	print(f"Module 'requests' is not installed")
	print(f"You can install it by running")
	print(f"pip install requests")
	quit()


def make_request(url: str, verbose=True) -> object:
	resp = None
	try:
		resp = requests.get(url)
	except Exception as e:
		if verbose:
			print(f"Request failed:\n  '{url}'\n  {str(e)}")
		return False
	if not resp:
		if verbose:
			print(f"Request failed:\n  '{url}'\n  status code: {resp.status_code}")
		return False
	return resp


def ping(addr: str, count=1, timeout=1) -> float:
	raise Exception('ping(...) is not implemented yet')
