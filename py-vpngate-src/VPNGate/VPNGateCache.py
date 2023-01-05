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
from .Constants import *


class VPNGateCache:
	"""Manages local VPN cache"""

	global VPNGATE_CACHE_FILENAME, VPNGATE_TEMP_CACHE_FILENAME, VPNGATE_UNAVAILABLE_FILTER_FILENAME

	def __init__(self):
		self.work_dir = get_file_dirname(__file__)
		self.cache_filepath = None
		self.vpns = []
		self.unavailable_vpns = []

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

		if not dont_update and not self.is_cache_valid():
			if not self._download_cache():
				return False

		self._load_cache_entries()
		self._filter_unavailable_vpns()

		logging.debug(f"Cache manager initialized (working directory is '{self.work_dir}')")
		return True

	def shutdown(self) -> None:
		self._save_unavailable_vpns()

		try:
			if not self.is_cache_valid():
				os.remove(self.cache_filepath)
		except Exception:
			pass

		logging.debug('Cache manager shut down')

	def reset_unavailable_vpns(self):
		self.vpns.extend(self.unavailable_vpns)
		self.unavailable_vpns.clear()
		self._save_unavailable_vpns()

	def set_unavailable(self, vpn: VPN, unavailable: bool=True):
		self.unavailable_vpns.append(vpn)
		self._save_unavailable_vpns()

		if vpn in self.vpns:
			self.vpns.remove(vpn)

	def is_cache_valid(self) -> bool:
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

			vpns_updated = 0
			vpns_added = 0
			for new in new_vpns:
				old = self.find(new.host)
				if old == new:
					continue
				elif old != None:
					self.vpns.remove(old)
					vpns_updated += 1
				else:
					vpns_added += 1
				self.vpns.append(new)

			self.vpns = list(set(self.vpns))

			with open(os.path.join(self.work_dir, VPNGATE_CACHE_FILENAME), 'w') as cache:
				cache.write("HostName,IP,Score,Ping,Speed,CountryLong,CountryShort,NumVpnSessions,Uptime,TotalUsers,TotalTraffic,LogType,Operator,Message,OpenVPN_ConfigData_Base64\n")
				for vpn in self.vpns:
					cache.write(vpn.dump() + '\n')

			logging.info(
				f"Successfully updated vpn list. " +\
				f"{vpns_added} Added, {vpns_updated} updated. {len(self.vpns)} In total."
			)

			try:
				os.remove(VPNGATE_TEMP_CACHE_FILENAME)
			except Exception:
				logging.debug(f"Failed to remove '{VPNGATE_TEMP_CACHE_FILENAME}'")

	def save_config(self, host: str, filepath: str) -> bool:
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
		return next((v for v in self.vpns if v.host == host), None)

	def _load_cache_entries(self, vpnlist=None, filename=None) -> bool:
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
			logging.debug(f"Failed to load cache. " + '\n'.join(traceback.format_exception_only(__exc=e, value=None)))
			return False
		return True

	def _download_cache(self, filename=None) -> bool:
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

	def _filter_unavailable_vpns(self):
		vpns_by_host = {vpn.host: vpn for vpn in self.vpns}

		self.unavailable_vpns.clear()
		try:
			with open(os.path.join(self.work_dir, VPNGATE_UNAVAILABLE_FILTER_FILENAME)) as file:
				unavailable_hosts = [host.strip() for host in file.readlines()]

				for host in unavailable_hosts:
					if host in vpns_by_host:
						self.unavailable_vpns.append(vpns_by_host[host])
						self.vpns.remove(vpns_by_host[host])

		except OSError as e:
			self._save_unavailable_vpns()

	def _save_unavailable_vpns(self):
		with open(os.path.join(self.work_dir, VPNGATE_UNAVAILABLE_FILTER_FILENAME), 'w') as file:
			file.write('\n'.join((vpn.host for vpn in self.unavailable_vpns)) + '\n')
