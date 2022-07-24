import os
import csv
import base64
import logging
import traceback
from .VPN import *
from .VPNConfig import *
from .FormatUtils import *
from .NetworkingUtils import *
from .FilesystemUtils import *


VPNGATE_API_URL = 'https://www.vpngate.net/api/iphone'
VPNGATE_CACHE_FILENAME = '.vpngate_cache'


class VPNGateCache:
	"""Manages local cache with all the VPN parameters."""

	global VPNGATE_CACHE_FILENAME

	def __init__(self):
		self.work_dir = get_file_dirname(__file__)
		self.cache_filepath = None
		self.vpns = None

	def init(self, work_dir=None, dont_update=False):
		"""
		Checks whether the cache is valid and if not downloads a new one.

		Parameters:
			dont_update: do not download cache if it doesn't exist

		Throws:
			Any kind of exception
		"""

		if work_dir is not None:
			self.work_dir = work_dir
		self.cache_filepath = os.path.join(work_dir, VPNGATE_CACHE_FILENAME)
		self.vpns = []

		if not dont_update and not self.is_cache_valid():
			self._download_cache()
		self._load_cache_entries()

		logging.debug(f"Cache manager initialized (working directory is '{self.work_dir}')")

	def shutdown(self):
		"""No Throw"""

		try:
			if not self.is_cache_valid():
				os.remove(self.cache_filepath)
		except Exception:
			pass

		logging.debug('Cache manager shut down')

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

		logging.info(f"Updating cache...")

		if not self._download_cache():
			return
		elif not self._load_cache_entries():
			logging.error('Failed to load cache entries')
		elif not self.is_cache_valid():
			logging.error('Cache is invalid after update')
		else:
			logging.debug('Cache updated')

	def save_config(self, host: str, filepath: str) -> bool:
		"""
		Returns:
			bool: whether VPN config was successfully found and saved

		No Throw
		"""

		try:
			vpn = self.find(host=host)
			if vpn is None:
				return False
			vpn.config.save(filepath)
			logging.debug(F"Saved OpenVPN config for host '{host}' to '{filepath}'")
		except Exception as e:
			try:
				os.remove(filepath)
			except FileNotFoundError:
				pass
			logging.error(f"Failed to save config for host '{host}' to '{filepath}'")
			return False
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

		No Throw
		"""

		try:
			with open(self.cache_filepath) as file:
				self.vpns = [VPN.from_cache_entry(e) for e in list(csv.DictReader(file))]
		except Exception as e:
			return False
		return True

	def _download_cache(self) -> bool:
		"""
		Downloads and saves VPNGate list locally.

		No Throw
		"""

		global VPNGATE_API_URL

		logging.debug(f"Downloading cache from '{VPNGATE_API_URL}'")

		resp = make_request(VPNGATE_API_URL, )

		if resp is None:
			return False

		try:
			text = bytes.decode(resp.content, encoding='utf-8')
			text = text[text.index('\n')+2:text.rindex('*')-1] # Remove '*vpn_servers\n#' and '*\n' at the end
			with open(self.cache_filepath, 'w') as file:
				file.write(text)
		except Exception as e:
			logging.error(f"Failed to process response content")
			logging.debug(f"Exception:\n{traceback.format_exception(e)}")
			return False

		logging.debug(f"Cache saved to '{self.cache_filepath}'")
		return True
