import csv
import base64
import os
from .VPN import VPN
from .NetworkingUtils import *
from .FormatUtils import *


VPNGATE_API_URL = 'https://www.vpngate.net/api/iphone'


class VPNGateCache:
	"""Manages local cache with all the VPN parameters."""

	def __init__(self, cache_path='./.vpngate_cache'):
		self.cache_filepath = cache_path
		self.vpns = []
		pass

	def init(self, dont_update=False):
		"""Checks whether the cache is valid and if not downloads a new one."""

		if not dont_update and not self.is_cache_valid():
			self._download_cache()
		self._load_cache_entries()

	def shutdown(self):
		if not self.is_cache_valid():
			os.remove(self.cache_filepath)

	def is_cache_valid(self) -> bool:
		"""Warning! This method doesn't check whether the cache is a valid CSV file."""

		if not os.path.exists(self.cache_filepath):
			return False
		with open(self.cache_filepath) as file:
			contents = file.read()
			if contents.isspace() or contents == '':
				return False
		return True

	def update(self):
		"""Downloads a new cache."""

		self._download_cache()
		self._load_cache_entries()

	def save_config(self, host: str, filepath: str) -> bool:
		try:
			vpn = self.find(host=host)
			if vpn is None:
				print(f"Unknown VPN host name '{host}'")
				return False
			with open(filepath, 'wb') as file:
				file.write(base64.b64decode(vpn.config_base64))
		except Exception as e:
			os.remove(filepath)
			raise e
		return True

	def find(self, host: str) -> VPN:
		return next((v for v in self.vpns if v.host == host), None)

	def _load_cache_entries(self) -> bool:
		try:
			with open(self.cache_filepath) as file:
				self.vpns = [VPN.from_cache_entry(e) for e in list(csv.DictReader(file))]
		except Exception as e:
			# raise e
			return False
		return True

	def _download_cache(self):
		global VPNGATE_API_URL
		resp = make_request(VPNGATE_API_URL, )
		text = bytes.decode(resp.content, encoding='utf-8')
		text = text[text.index('\n')+2:text.rindex('*')-1] # Remove '*vpn_servers\n#' and '*\n' at the end
		with open(self.cache_filepath, 'w') as file:
			file.write(text)
