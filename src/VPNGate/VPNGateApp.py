import argparse
from sys import argv
from .VPNSuggestions import *
from .VPNGateCache import *
from .VPNManager import *


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
		self.arg_parser.add_argument('-tb', dest='suggest_true_best', action='store_true', help=f"show VPNs that the utility is able to connect to")
		self.arg_parser.add_argument('--connect', metavar='HOSTNAME', dest='hostname_to_connect', const=None, help=f"connect to VPN host")
		self.arg_parser.add_argument('--save', metavar='HOSTNAME', dest='save_config_hostname', const=None, help=f"save OpenVPN config for given server")
		self.arg_parser.add_argument('--show', metavar='HOSTNAME', dest='hostname_to_show', const=None, help=f"show more information about specified host")
		self.args = None

		self.cache = VPNGateCache()
		self.vpn_manager = VPNManager()

	def run(self):
		self.args = self.arg_parser.parse_args()

		self.cache.init(dont_update=True)
		self.vpn_manager.init()

		if self.args.update_cache or (not self.cache.is_cache_valid() and len(argv) > 1):
			print('Downloading VPN list...')
			self.cache.update()

		if self.args.save_config_hostname != None:
			if self.cache.save_config(
					host=self.args.save_config_hostname,
					filepath=self.args.save_config_hostname + '.ovpn'):
				print(f"Saved to './{self.args.save_config_hostname}.ovpn'")

		elif self.args.suggest_best:
			print(*best_vpn_by_speed(self.cache.vpns, count=3), sep='\n')

		elif self.args.suggest_true_best:
			print(
				*filter_vpn_by_connectable(best_vpn_by_speed(self.cache.vpns), self.vpn_manager),
				sep='\n'
			)

		elif self.args.print_list:
			print(*self.cache.vpns, sep='\n')

		elif self.args.hostname_to_show is not None:
			vpn = self.cache.find(self.args.hostname_to_show)
			if vpn != None:
				vpn.print_description()

		elif self.args.hostname_to_connect is not None:
			global APP_VPN_PROFILE_NAME

			filepath = self.args.hostname_to_connect + '.ovpn'
			vpn = self.cache.find(host=self.args.hostname_to_connect)

			if vpn is None:
				print(f"Unknown VPN host '{self.args.hostname_to_connect}'")
				return

			print('Creating VPN profile...')
			profile = self.vpn_manager.create_openvpn(
				config=vpn.config, name=APP_VPN_PROFILE_NAME
			)

			if self.vpn_manager.connect(profile):
				print(f"Connected to '{profile.name}'")

		elif not self.args.update_cache:
			self.arg_parser.print_help()

	def close(self):
		self.vpn_manager.shutdown()
		self.cache.shutdown()
		pass
