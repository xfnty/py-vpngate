import os
import sys
import logging
import argparse
import traceback
import urllib.request
from sys import argv

from .VPNTester import *
from .VPNManager import *
from .VPNGateCache import *
from .VPNSuggestions import *

from .FormatUtils import *
from .FilesystemUtils import *

from .VPNBackendNmcli import *
from .VPNBackendOpenVPN import *
from .VPNBackendPowershell import *

from .Constants import *


class VPNGateApp:
	"""*silence*"""

	def __init__(self, work_dir=None):
		self.log_path = None
		self.work_dir = get_file_dirname(__file__)
		if work_dir is not None:
			self.work_dir = work_dir

		self._setup_logging()

		self.backend_bindings = {
			'nmcli': VPNBackendNmcli,
			#'powersh': VPNBackendPowershell,
			#'ovpn': VPNBackendOpenVPN,
			None: None
		}

		backends_str = ', '.join([f"'{k}'" for k in self.backend_bindings if k is not None])

		self.arg_parser = argparse.ArgumentParser(
			prog='vpngate',
			description='Parses public VPN lists and gives best VPN suggestions.',
			epilog=f"log file is saved to '{self.log_path}'"
		)
		self.arg_parser.add_argument(
			'-l',
			dest='print_list', action='store_true',
			help=f"list cached VPN servers"
		)
		self.arg_parser.add_argument(
			'-u',
			dest='update_vpn_cache', action='store_true',
			help=f"update VPN cache"
		)
		self.arg_parser.add_argument(
			'-ur',
			dest='download_vpn_cache', action='store_true',
			help=f"Download daily updated VPN cache from GitHub releases"
		)
		self.arg_parser.add_argument(
			'-b',
			dest='suggest_best', action='store_true',
			help=f"show VPNs with highest speed"
		)
		self.arg_parser.add_argument(
			'-cb',
			dest='connect_best', action='store_true', 
			help=f"find best VPN and connect to it. " + 
			f"You can always press Ctrl+C to abort the operation"
		)
		self.arg_parser.add_argument(
			'-c',
			metavar='HOSTNAME', dest='hostname_to_connect', const=None, 
			help=f"connect to specified VPN host"
		)
		self.arg_parser.add_argument(
			'-f',
			dest='filter_vpn_cache', action='store_true', 
			help=f"filter VPNs by availability using TCP and VPN backend"
		)
		self.arg_parser.add_argument(
			'-rf',
			dest='reset_filter', action='store_true', 
			help=f"move VPN entries from filtered cache to active"
		)
		self.arg_parser.add_argument(
			'-p',
			metavar='HOSTNAME', dest='hostname_to_show', const=None, 
			help=f"show more information about specified host"
		)
		self.arg_parser.add_argument(
			'-s',
			metavar='HOSTNAME', dest='save_config_hostname', const=None, 
			help=f"save OpenVPN config for the given server"
		)
		self.arg_parser.add_argument(
			'-t',
			metavar='TIMEOUT', dest='timeout', type=int, 
			help=f"specify a timeout for the commands"
		)
		self.arg_parser.add_argument(
			'-r',
			dest='remove_profile', action='store_true', 
			help=f"remove '{APP_VPN_PROFILE_NAME}' from VPN settings"
		)
		self.arg_parser.add_argument(
			'--use', 
			metavar='BACKEND', dest='backend', const=None, 
			help=f"specify backend for connecting to VPN. " + 
			f"Avavilable backends are {backends_str}. OS Specific is used by default."
		)
		self.args = None
		
		self.vpn_cache = VPNGateCache()
		self.vpn_manager = VPNManager()
		self.vpn_tester = VPNTester(self.vpn_manager)

	def run(self):
		arg_str = ' '.join([os.path.basename(argv[0])] + argv[1:])
		logging.debug(f"##### App start: '{arg_str}'")

		if not self._init_stuff():
			return

		logging.debug(f"CWD is '{self.work_dir}'")

		if self.args.remove_profile:
			self._remove_profile()
			return

		if self.args.download_vpn_cache:
			self._download_cache()
		elif self.args.update_vpn_cache or (not self.vpn_cache.is_cache_valid() and len(argv) > 1):
			self.vpn_cache.update()

		if self.args.save_config_hostname is not None:
			self._save_config(self.args.save_config_hostname)
		elif self.args.connect_best:
			self._connect_best(self.args.timeout)
		elif self.args.filter_vpn_cache:
			self._filter_vpn_cache(self.args.timeout)
		elif self.args.reset_filter:
			self._reset_filter()
		elif self.args.suggest_best:
			self._suggest_best()
		elif self.args.print_list:
			self._print_list()
		elif self.args.hostname_to_show is not None:
			self._show_host(self.args.hostname_to_show)
		elif self.args.hostname_to_connect is not None:
			self._connect(self.args.hostname_to_connect, self.args.timeout)
		elif len(argv) == 1:
			self.arg_parser.print_usage()


	def close(self):
		"""
		Close the app.

		No Throw
		"""

		try:
			self.vpn_manager.shutdown()
			self.vpn_cache.shutdown()
		except Exception:
			pass

		logging.debug(f"### closed")

	def _init_stuff(self) -> bool:
		try:
			self.args = self.arg_parser.parse_args()
		except Exception as e:
			logging.error(f"Failed to parse arguments")
			logging.debug(f"Exception:\n{traceback.format_exception(e)}")
			return False

		if not self.vpn_cache.init(work_dir=self.work_dir, dont_update=True):
			logging.error("Failed to initialize vpn_cache")
			return False

		if self.args.backend not in self.backend_bindings:
			logging.error(f"Unknown VPN backend '{self.args.backend}'. See help message for available backends.")
			return False
		backend_instance = None if self.args.backend is None else self.backend_bindings[self.args.backend]()
		if not self.vpn_manager.init(backend=backend_instance, work_dir=self.work_dir):
			logging.error("Failed to initialize VPN manager")
			return False

		return True

	def _download_cache(self):
		print('Downloading VPN list ...', flush=True)
		response = urllib.request.urlopen(VPNGATE_RELEASED_CACHE)
		filepath = os.path.join(self.work_dir, VPNGATE_CACHE_FILENAME)
		with open(filepath, 'wb') as file:
			file.write(response.read())

	def _print_list(self):
		print(*sorted(self.vpn_cache.vpns, key=lambda vpn: vpn.country_short), sep='\n')

	def _suggest_best(self):
		print(*best_vpn_by_speed(self.vpn_cache.vpns), sep='\n')

	def _connect_best(self, timeout=None):
		timeout = 5 if timeout is None else timeout
		global APP_VPN_PROFILE_NAME

		profile = None
		try:
			for i, vpn in enumerate(best_vpn_by_speed(self.vpn_cache.vpns, count=len(self.vpn_cache.vpns))):
				profile = self.vpn_manager.create_profile(
					config=vpn.config,
					name='VPNGate Temp Profile'
				)

				if profile is None:
					logging.error(f"invalid profile '{vpn.host}'")
					continue

				logging.info(f"connecting to '{vpn.host}'")
				if not self.vpn_manager.connect(profile, timeout=timeout):
					continue

				self.vpn_manager.disconnect(profile)
				self.vpn_manager.remove(profile)

				# Only to rename existing profile in network manager
				logging.info(f"connection to '{vpn.host}' established. Finishing")
				profile = self.vpn_manager.create_profile(
					config=vpn.config,
					name=APP_VPN_PROFILE_NAME)
				if profile is None or not self.vpn_manager.connect(profile, timeout=timeout + 5):
					logging.error(f"connection to '{vpn.host}' feailed. Something went wrong")
					continue
				
				logging.info(f"connected to '{vpn.host}'")
				break
		except KeyboardInterrupt:
			self.vpn_manager.disconnect(profile)
			self.vpn_manager.remove(profile)
			print()

	def _filter_vpn_cache(self, timeout=None):
		timeout = 10 if timeout is None else timeout
		start_vpn_count = len(self.vpn_cache.vpns)
		i = 0
		while i < len(self.vpn_cache.vpns):
			vpn = self.vpn_cache.vpns[i]

			msg = "{:<28}".format(f"[{i}/{len(self.vpn_cache.vpns)}] {vpn.host}")

			tcp_ok = self.vpn_tester.test_vpn(vpn, timeout=0.5).available
			if not tcp_ok:
				self.vpn_cache.set_unavailable(vpn)
				logging.info(msg)
				continue

			vpn_ok = self.vpn_tester.test_vpn_with_vpnmanager(vpn, timeout=timeout).available
			if not vpn_ok:
				self.vpn_cache.set_unavailable(vpn)
				logging.info(msg)
				continue

			i += 1
			logging.info(msg + " online")
				

	def _reset_filter(self):
		unavailable_vpn_count = len(self.vpn_cache.unavailable_vpns)
		self.vpn_cache.reset_unavailable_vpns()

	def _save_config(self, host: str):
		filepath = os.path.join(os.getcwd(), host + '.ovpn')
		if self.vpn_cache.save_config(
				host=host,
				filepath=filepath):
			logging.info(f"Config saved to '{filepath}'")

	def _show_host(self, host: str):
		vpn = self.vpn_cache.find(host)
		if vpn != None:
			vpn.print_description()
		else:
			logging.error(f"Could not find VPN entry for '{host}'")

	def _connect(self, host: str, timeout=None):
		global APP_VPN_PROFILE_NAME

		timeout = 5 if timeout is None else timeout
		filepath = host + '.ovpn'
		vpn = self.vpn_cache.find(host=host)

		if vpn is None:
			logging.error(f"Unknown VPN host '{host}'")
			return

		profile = self.vpn_manager.create_profile(
			config=vpn.config, name=APP_VPN_PROFILE_NAME
		)

		if profile is None:
			logging.error(f"Failed to create VPN profile '{APP_VPN_PROFILE_NAME}'")
			return

		logging.info(f"Connecting to '{profile.name}'...")
		if self.vpn_manager.connect(profile, timeout=timeout):
			logging.info(f"Connection established")
		else:
			self.vpn_manager.disconnect(profile)
			self.vpn_manager.remove(profile)
			logging.error(f"Failed")

	def _remove_profile(self):
		global APP_VPN_PROFILE_NAME

		profile = self.vpn_manager.get_profile(APP_VPN_PROFILE_NAME)
		if profile is None:
			return

		self.vpn_manager.disconnect(profile)
		self.vpn_manager.remove(profile)

	def _setup_logging(self):
		global APP_LOG_FILENAME

		_console_formatter = logging.Formatter('%(message)s')
		_file_formatter = logging.Formatter("%(message)s (At %(filename)s:%(lineno)d)")

		_ch = logging.StreamHandler()
		_ch.setLevel(logging.INFO)
		_ch.setFormatter(_console_formatter)

		self.log_path = os.path.join(self.work_dir, APP_LOG_FILENAME)

		_fh = logging.FileHandler(self.log_path, mode='a')
		_fh.setLevel(logging.NOTSET)
		_fh.setFormatter(_file_formatter)

		logging.basicConfig(
			level=logging.NOTSET,
			handlers=[_ch, _fh]
		)
