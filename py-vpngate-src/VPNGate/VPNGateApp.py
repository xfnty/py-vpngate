import os
import sys
import logging
import argparse
import traceback
from sys import argv
from .VPNManager import *
from .VPNGateCache import *
from .VPNSuggestions import *
from .FormatUtils import *
from .FilesystemUtils import *

from .VPNBackendNmcli import *
from .VPNBackendOpenVPN import *
from .VPNBackendPowershell import *


APP_VPN_PROFILE_NAME = 'VPNGate Profile'
APP_LOG_FILENAME = 'vpngate.log'


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
			'powersh': VPNBackendPowershell,
			'ovpn': VPNBackendOpenVPN,
			None: None
		}

		backends_str = ', '.join([f"'{k}'" for k in self.backend_bindings if k is not None])

		self.arg_parser = argparse.ArgumentParser(
			prog='vpngate',
			description='Parses public VPN lists and gives best VPN suggestions.',
			epilog=f"Log file is saved to '{self.log_path}'"
		)
		self.arg_parser.add_argument('-l', dest='print_list', action='store_true', help=f"list cached VPN servers")
		self.arg_parser.add_argument('-u', dest='update_cache', action='store_true', help=f"update VPN list cache")
		self.arg_parser.add_argument('-b', dest='suggest_best', action='store_true', help=f"show VPNs with highest speed")
		self.arg_parser.add_argument('-cb', dest='connect_best', action='store_true', help=f"find best VPN and connect to it. You can always press Ctrl+C to abort the operation")
		self.arg_parser.add_argument('-c', metavar='HOSTNAME', dest='hostname_to_connect', const=None, help=f"connect to the VPN host")
		self.arg_parser.add_argument('-p', metavar='HOSTNAME', dest='hostname_to_show', const=None, help=f"show more information about specified host")
		self.arg_parser.add_argument('-s', metavar='HOSTNAME', dest='save_config_hostname', const=None, help=f"save OpenVPN config for the given server")
		self.arg_parser.add_argument('-t', metavar='TIMEOUT', dest='timeout', type=int, help=f"specify a timeout for the commands")
		self.arg_parser.add_argument('-r', dest='remove_profile', action='store_true', help=f"Remove '{APP_VPN_PROFILE_NAME}' from VPN settings")
		self.arg_parser.add_argument('--use', metavar='BACKEND', dest='backend', const=None, help=f"Specify backend for connecting to VPN. Avavilable backends are {backends_str}. OS Specific is used by default.")
		self.args = None
		
		self.cache = VPNGateCache()
		self.vpn_manager = VPNManager()

	def run(self):
		arg_str = ' '.join([os.path.basename(argv[0])] + argv[1:])
		logging.debug(f"##### App start: '{arg_str}'")

		if not self._init_stuff():
			return

		logging.debug(f"CWD is '{self.work_dir}'")

		if self.args.remove_profile:
			self._remove_profile()
			return

		if self.args.update_cache or (not self.cache.is_cache_valid() and len(argv) > 1):
			self.cache.update()

		if self.args.save_config_hostname is not None:
			self._save_config(self.args.save_config_hostname)

		elif self.args.connect_best:
			self._connect_best(self.args.timeout)

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
			self.cache.shutdown()
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

		if not self.cache.init(work_dir=self.work_dir, dont_update=True):
			logging.error("Failed to initialize cache")
			return False

		if self.args.backend not in self.backend_bindings:
			logging.error(f"Unknown VPN backend '{self.args.backend}'. See help message for available backends.")
			return False
		backend_instance = None if self.args.backend is None else self.backend_bindings[self.args.backend]()
		if not self.vpn_manager.init(backend=backend_instance, work_dir=self.work_dir):
			logging.error("Failed to initialize VPN manager")
			return False

		return True

	def _print_list(self):
		print(*self.cache.vpns, sep='\n')

	def _suggest_best(self):
		print(*best_vpn_by_speed(self.cache.vpns), sep='\n')

	def _connect_best(self, timeout=None):
		global APP_VPN_PROFILE_NAME

		timeout = 5 if timeout is None else timeout
		profile = None
		try:
			for i, vpn in enumerate(best_vpn_by_speed(self.cache.vpns, count=len(self.cache.vpns))):
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

				# Only to rename existing profile
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

	def _save_config(self, host: str):
		filepath = os.path.join(os.getcwd(), host + '.ovpn')
		if self.cache.save_config(
				host=host,
				filepath=filepath):
			logging.info(f"Config saved to '{filepath}'")

	def _show_host(self, host: str):
		vpn = self.cache.find(host)
		if vpn != None:
			vpn.print_description()
		else:
			logging.error(f"Could not find VPN entry for '{host}'")

	def _connect(self, host: str, timeout=None):
		global APP_VPN_PROFILE_NAME

		timeout = 5 if timeout is None else timeout
		filepath = host + '.ovpn'
		vpn = self.cache.find(host=host)

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
