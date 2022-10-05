import logging
import traceback
import urllib.request
import socket


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


def try_connect(ip: str, port: int, timeout=0.5) -> bool:
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		try:
			s.settimeout(timeout)
			s.connect((ip, port))
		except Exception as e:
			return False
		s.close()
	return True
