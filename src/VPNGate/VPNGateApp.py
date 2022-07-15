import argparse
from sys import argv
from .VPNManager import *
from .VPNGateCache import *
from .VPNSuggestions import *
from .FormatUtils import *
from .FilesystemUtils import *


APP_VPN_PROFILE_NAME = 'VPNGate Profile'


class VPNGateApp:
	"""*silence*"""

	def __init__(self):
		self.arg_parser = argparse.ArgumentParser(
			prog='vpngate',
			description='Parses public VPN lists and gives best VPN suggestions.',
		)
		self.arg_parser.add_argument('-l', dest='print_list', action='store_true', help=f"list cached VPN servers")
		self.arg_parser.add_argument('-u', dest='update_cache', action='store_true', help=f"update VPN list cache")
		self.arg_parser.add_argument('-b', dest='suggest_best', action='store_true', help=f"show VPNs with highest speed")
		self.arg_parser.add_argument('-cb', dest='connect_best', action='store_true', help=f"find best VPN and connect to it. You can always press Ctrl+C to abort the operation")
		self.arg_parser.add_argument('-c', metavar='HOSTNAME', dest='hostname_to_connect', const=None, help=f"connect to VPN host")
		self.arg_parser.add_argument('-p', metavar='HOSTNAME', dest='hostname_to_show', const=None, help=f"show more information about specified host")
		self.arg_parser.add_argument('-s', metavar='HOSTNAME', dest='save_config_hostname', const=None, help=f"save OpenVPN config for given server")
		self.arg_parser.add_argument('-t', metavar='TIMEOUT', dest='timeout', type=int, help=f"specify timeout for connect commands")
		self.args = None
		self.work_dir = get_file_dirname(__file__)

		self.cache = VPNGateCache()
		self.vpn_manager = VPNManager()

	def run(self, work_dir=None):
		"""
		Launch the app.

		Throws:
			Any kind of exception
		"""

		if work_dir is not None:
			self.work_dir = work_dir

		self.args = self.arg_parser.parse_args()

		self.cache.init(work_dir, dont_update=True)
		self.vpn_manager.init(work_dir)

		if self.args.update_cache or (not self.cache.is_cache_valid() and len(argv) > 1):
			print('Downloading VPN list...')
			self.cache.update()

		if self.args.save_config_hostname != None:
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

		elif not self.args.update_cache:
			self.arg_parser.print_help()

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
				print('\r' + ' '*50 + f"\r[{i}] {vpn.host}: creating profile", end='', flush=True)

				profile = self.vpn_manager.create_openvpn(
					config=vpn.config,
					name='VPNGate Temp Profile')

				if profile is None:
					print('\r' + ' '*50 + f"\r[{i}] {vpn.host}: invalid profile", flush=True)
					continue

				print('\r' + ' '*50 + f"\r[{i}] {vpn.host}: connecting", end='', flush=True)
				if not self.vpn_manager.connect(profile, timeout=timeout):
					print('\r' + ' '*50 + f"\r[{i}] {vpn.host}: failed")
					continue

				self.vpn_manager.disconnect(profile)
				self.vpn_manager.remove(profile)

				# Only to rename existing profile
				print('\r' + ' '*50 + f"\r[{i}] {vpn.host}: established. Finishing", end='', flush=True)
				profile = self.vpn_manager.create_openvpn(
					config=vpn.config,
					name=APP_VPN_PROFILE_NAME)
				if profile is None or not self.vpn_manager.connect(profile, timeout=timeout + 5):
					print('\r' + ' '*50 + f"\r[{i}] {vpn.host}: something went wrong")
					continue
				
				print('\r' + ' '*50 + f"\r[{i}] {vpn.host}: connected")
				break
		except KeyboardInterrupt:
			self.vpn_manager.disconnect(profile)
			self.vpn_manager.remove(profile)
			print()

	def _save_config(self, host: str):
		filepath = os.path.join(self.work_dir, host + '.ovpn')
		if self.cache.save_config(
				host=host,
				filepath=filepath):
			print(f"Saved to '{filepath}'")

	def _show_host(self, host: str):
		vpn = self.cache.find(host)
		if vpn != None:
			vpn.print_description()

	def _connect(self, host: str, timeout=None):
		global APP_VPN_PROFILE_NAME

		timeout = 5 if timeout is None else timeout
		filepath = host + '.ovpn'
		vpn = self.cache.find(host=host)

		if vpn is None:
			print(f"Unknown VPN host '{host}'")
			return

		print(f"Creating VPN profile '{APP_VPN_PROFILE_NAME}'...")
		profile = self.vpn_manager.create_openvpn(
			config=vpn.config, name=APP_VPN_PROFILE_NAME
		)

		if profile is None:
			print('Failed')
			return

		print(f"Connecting to '{profile.name}'")
		if self.vpn_manager.connect(profile, timeout=timeout):
			print('done')
		else:
			print('failed')
			self.vpn_manager.disconnect(profile)
			self.vpn_manager.remove(profile)
