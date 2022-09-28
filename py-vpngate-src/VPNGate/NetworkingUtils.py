import logging
import traceback
import urllib.request


def make_request(url: str, verbose=True) -> object:
	"""
	Parameters:
		verbose: if set, funciton will print error messages

	Returns:
		Response
		None

	No Throw
	"""

	req = None
	load = None
	try:
		req = urllib.request.urlopen(url)
		if req is None:
			return None
		load = req.read()
	except Exception as e:
		if verbose:
			logging.error(f"Request to '{url}' failed")
			if req is not None:
				logging.debug(f"Request details: status={req.status} reason={req.reason}")
			logging.debug(f"Exception:\n{''.join(traceback.format_exception(e))}")
		return None
	return load
