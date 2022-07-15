import csv
import base64
import os
from .VPN import *
from .VPNConfig import *
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
		"""
		Checks whether the cache is valid and if not downloads a new one.

		Parameters:
			dont_update: do not download cache if it doesn't exist

		Throws:
			Any kind of exception
		"""

		if not dont_update and not self.is_cache_valid():
			self._download_cache()
		self._load_cache_entries()

	def shutdown(self):
		"""No Throw"""
		try:
			if not self.is_cache_valid():
				os.remove(self.cache_filepath)
		except Exception:
			pass

	def is_cache_valid(self) -> bool:
		"""
		Warning! This method doesn't check whether the cache is a valid CSV file.

		No Throw
		"""

		if not os.path.exists(self.cache_filepath):
			return False
		try:
			with open(self.cache_filepath) as file:
				contents = file.read()
				if contents.isspace() or contents == '':
					return False
		except Exception as e:
			# raise e
			return False
		return True

	def update(self):
		"""Downloads a new cache."""

		self._download_cache()
		if not self._load_cache_entries():
			print('Failed to load cache entries')
		if not self.is_cache_valid():
			print('Cache is invalid after update')

	def save_config(self, host: str, filepath: str) -> bool:
		"""
		Returns:
			bool: whether VPN config was successfully found and saved

		Throws:
			Any kind of exception
		"""

		try:
			vpn = self.find(host=host)
			if vpn is None:
				return False
			vpn.config.save(filepath)
		except Exception as e:
			try:
				os.remove(filepath)
			except FileNotFoundError:
				pass
			raise e
		return True

	def find(self, host: str) -> VPN:
		"""
		Returns:
			VPN
			None

		No Throw
		"""
		
		return next((v for v in self.vpns if v.host == host), None)

	def _load_cache_entries(self) -> bool:
		"""
		Reads cache and loads VPNs into 'self.vpns' list.

		Throws:
			File IO related exceptions
			CSV parsing related exceptions
		"""

		try:
			with open(self.cache_filepath) as file:
				self.vpns = [VPN.from_cache_entry(e) for e in list(csv.DictReader(file))]
		except Exception as e:
			raise e
			return False
		return True

	def _download_cache(self):
		"""
		Downloads and saves VPNGate list locally.

		Throws:
			Network related exceptions
			File IO related exceptions
			Encoding related exceptions
		"""

		global VPNGATE_API_URL
		resp = make_request(VPNGATE_API_URL, )
		text = bytes.decode(resp.content, encoding='utf-8')
		text = text[text.index('\n')+2:text.rindex('*')-1] # Remove '*vpn_servers\n#' and '*\n' at the end
		with open(self.cache_filepath, 'w') as file:
			file.write(text)
