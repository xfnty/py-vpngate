from .NetworkingUtils import *
from .VPN import *
from .VPNManager import *


def best_vpn_by_speed(vpns: [VPN], count=3) -> [VPN]:
	"""Sorts VPN list by host's average bandwidth."""

	return sorted(vpns, key=lambda v: -v.speed)[:min(count, len(vpns))]


def best_vpn_by_ping(vpns: [VPN], count=1) -> [VPN]:
	return sorted(vpns, key=lambda v: ping(v.ip))[:min(count, len(vpns))]


def filter_vpn_by_connectable(vpns: [VPN], vpn_manager: VPNManager, count=1) -> [VPN]:
	"""Creates system VPN profile for every VPN entry and tries to connect to it."""

	global TMP_VPN_CONFIG_FILEPATH

	def key(vpn: VPN) -> bool:
		profile = vpn_manager.create_openvpn(
			config=vpn.config,
			name='VPNGate Temp Profile'
		)

		if profile is None:
			return False
		if not vpn_manager.connect(profile):
			return False
		vpn_manager.disconnect(profile)
		vpn_manager.remove(profile)
		return True

	return list(filter(key, vpns))
