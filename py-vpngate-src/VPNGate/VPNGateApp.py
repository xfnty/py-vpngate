import argparse
from .VPNGateCache import *


class VPNGateApp:
	def __init__(self):
		self.arg_parser = argparse.ArgumentParser(
			prog='vpngate',
			description='Parses public VPN lists and gives best VPN suggestions.',
		)
		self.arg_parser.add_argument('-l', dest='print_list', action='store_true', help=f"list cached VPN servers")
		self.arg_parser.add_argument('-u', dest='update_cache', action='store_true', help=f"update VPN list cache")
		self.arg_parser.add_argument('-b', dest='suggest_best', action='store_true', help=f"show VPNs with lowest ping")
		self.arg_parser.add_argument('-d', metavar='HOSTNAME', dest='save_config_hostname', const=None, help=f"save OpenVPN config for given server")
		#self.arg_parser.add_argument('-c', metavar='HOSTNAME', dest='connect_hostname', const=None, help=f"connect to known VPN server using its hostname")
		self.arg_parser.add_argument('-s', metavar='HOSTNAME', dest='hostname_to_show', const=None, help=f"show more information about specified host")
		self.args = None

		self.cache = VPNGateCache()


	def run(self):
		self.args = self.arg_parser.parse_args()
		
		just_updated = not self.cache.is_updated()
		if not self.cache.init():
			return

		if not just_updated and self.args.update_cache:
			self.cache.update()

		elif self.args.save_config_hostname != None:
			self.cache.save_config(self.args.save_config_hostname)

		elif self.args.suggest_best:
			for vpn in self.cache.get_suggestions():
				print(str(vpn))

		elif self.args.print_list:
			for vpn in self.cache.entries():
				print(str(vpn))

		elif self.args.hostname_to_show != None:
			vpn = self.cache.find(self.args.hostname_to_show)
			if vpn != None:
				vpn.print_description()

		else:
			self.arg_parser.print_help()


	def close(self):
		pass
