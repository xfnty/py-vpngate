import argparse
from sys import argv
from .VPNStats import *
from .VPNGateCache import *
from .VPNManager import *


class VPNGateApp:
	"""*silence*"""

	def __init__(self):
		self.arg_parser = argparse.ArgumentParser(
			prog='vpngate',
			description='Parses public VPN lists and gives best VPN suggestions.',
		)
		self.arg_parser.add_argument('-l', dest='print_list', action='store_true', help=f"list cached VPN servers")
		self.arg_parser.add_argument('-u', dest='update_cache', action='store_true', help=f"update VPN list cache")
		self.arg_parser.add_argument('-b', dest='suggest_best', action='store_true', help=f"show VPNs with lowest ping")
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
			print(*best_vpn_by_speed(self.cache.vpns), sep='\n')

		elif self.args.print_list:
			print(*self.cache.vpns, sep='\n')

		elif self.args.hostname_to_show != None:
			vpn = self.cache.find(self.args.hostname_to_show)
			if vpn != None:
				vpn.print_description()

		elif not self.args.update_cache:
			self.arg_parser.print_help()

	def close(self):
		self.vpn_manager.shutdown()
		pass
