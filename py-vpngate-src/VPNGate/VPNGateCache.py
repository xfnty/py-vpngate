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
VPNGATE_TEMP_CACHE_FILENAME = '.vpngate_temp_cache'


class VPNGateCache:
	"""Manages local cache with all the VPN parameters."""

	global VPNGATE_CACHE_FILENAME

	def __init__(self):
		self.work_dir = get_file_dirname(__file__)
		self.cache_filepath = None
		self.vpns = None

	def init(self, work_dir: str=None, dont_update: bool=False) -> bool:
		"""
		Checks whether the cache is valid and if not downloads a new one.

		Parameters:
			dont_update: do not download cache if it doesn't exist

		Throws:
			Usually don't
		"""

		if work_dir is not None:
			self.work_dir = work_dir
		self.cache_filepath = os.path.join(work_dir, VPNGATE_CACHE_FILENAME)
		self.vpns = []

		if not dont_update and not self.is_cache_valid():
			if not self._download_cache():
				return False

		self._load_cache_entries()

		logging.debug(f"Cache manager initialized (working directory is '{self.work_dir}')")
		return True

	def shutdown(self) -> None:
		"""No Throw"""

		try:
			if not self.is_cache_valid():
				os.remove(self.cache_filepath)
		except Exception:
			pass

		logging.debug('Cache manager shut down')

	def get_inactive_list(self) -> list:
		raise NotImplementedError()

	def reset_inactive_list(self):
		raise NotImplementedError()

	def make_inactive(self, vpn: VPN):
		raise NotImplementedError()

	def make_active(self, vpn: VPN):
		raise NotImplementedError()

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
			return False
		return True

	def update(self):
		"""Downloads a new cache."""

		global VPNGATE_TEMP_CACHE_FILENAME, VPNGATE_CACHE_FILENAME

		logging.debug(f"Updating cache...")

		if not self.is_cache_valid() or not self._load_cache_entries():
			# Cache does not exists, download a new one
			if not self._download_cache():
				logging.error('Failed to download cache')
				return

			if not self.is_cache_valid():
				logging.error('Cache is invalid after update')
				return

			elif not self._load_cache_entries():
				logging.error('Failed to load cache entries')
				return

			logging.info(f"Downloaded {len(self.vpns)} new VPN profiles")
		else:
			# Load existing cache and add new entries from the downloaded one
			if not self._download_cache(VPNGATE_TEMP_CACHE_FILENAME):
				logging.error('Old cache exists but failed to download a new one')
				return

			new_vpns = []
			if not self._load_cache_entries(new_vpns, VPNGATE_TEMP_CACHE_FILENAME):
				logging.error('Old cache exists but failed to load a new one')

			vpns_to_add = []
			vpn_hostnames = [vpn.host for vpn in self.vpns]
			for new in new_vpns:
				if new.host not in vpn_hostnames:
					vpns_to_add.append(new)
			self.vpns.extend(vpns_to_add)

			with open(os.path.join(self.work_dir, VPNGATE_CACHE_FILENAME), 'a') as cache:
				for vpn in vpns_to_add:
					cache.write(vpn.dump() + '\n')

			logging.info(
				f"Downloaded {len(vpns_to_add)} new VPN profiles. " +\
				f"{len(self.vpns)} in total"
			)

			try:
				os.remove(VPNGATE_TEMP_CACHE_FILENAME)
			except Exception:
				logging.debug(f"Failed to remove '{VPNGATE_TEMP_CACHE_FILENAME}'")

	def save_config(self, host: str, filepath: str) -> bool:
		"""
		Returns:
			bool: whether VPN config was successfully found and saved

		No Throw
		"""

		logging.debug(f"Saving config for '{host}' to '{filepath}' ...")

		try:
			vpn = self.find(host=host)
			if vpn is None:
				logging.debug(f"Could not find host '{host}'")
				return False
			vpn.config.save(filepath)
			logging.debug(F"Saved OpenVPN config for host '{host}' to '{filepath}'")
		except Exception as e:
			try:
				os.remove(filepath)
			except FileNotFoundError:
				logging.debug(f"Failed to remove '{filepath}'")
			logging.debug(f"Failed to save config for host '{host}' to '{filepath}'")
			return False

		logging.debug(f"Config saved to '{filepath}'")
		return True

	def find(self, host: str) -> VPN:
		"""
		Returns:
			VPN
			None

		No Throw
		"""
		
		return next((v for v in self.vpns if v.host == host), None)

	def _load_cache_entries(self, vpnlist=None, filename=None) -> bool:
		"""
		Reads cache and loads VPNs into 'self.vpns' list.

		No Throw
		"""

		if filename is None:
			filename = os.path.join(self.work_dir, self.cache_filepath)

		vpns = []
		try:
			with open(filename) as file:
				vpns = [VPN.from_cache_entry(e) for e in list(csv.DictReader(file))]
				if vpnlist is None:
					self.vpns = vpns
				else:
					vpnlist.extend(vpns)
		except Exception as e:
			logging.debug(f"Failed to load cache. Exception:\n{''.join(traceback.format_exception(e))}")
			return False
		return True

	def _download_cache(self, filename=None) -> bool:
		"""
		Downloads and saves VPNGate list locally.

		No Throw
		"""

		global VPNGATE_API_URL

		logging.debug(f"Downloading cache from '{VPNGATE_API_URL}'")

		if filename is None:
			filename = os.path.join(self.work_dir, self.cache_filepath)

		resp = make_request(VPNGATE_API_URL)

		if resp is None:
			logging.debug(f"Response is None")
			return False

		try:
			text = bytes.decode(resp, encoding='utf-8')
			text = text[text.index('\n')+2:text.rindex('*')-1] # Remove '*vpn_servers\n#' and '*\n' at the end
			with open(filename, 'w') as file:
				file.write(text)
		except Exception as e:
			logging.debug(f"Failed to process response content")
			logging.debug(f"Exception:\n{traceback.format_exception(e)}")
			try:
				os.remove(filename)
			except Exception:
				logging.debug(f"Failed to remove '{filename}'")
			return False

		logging.debug(f"Cache saved to '{filename}'")
		return True
