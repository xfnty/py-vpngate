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
			print(f"Request failed:\n  '{url}'\n  Code: {resp.status_code}")
		return False
	return resp
