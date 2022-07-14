from .NetworkingUtils import *
from .VPN import *


def best_vpn_by_speed(vpns: [VPN], count=3) -> [VPN]:
	"""Sorts VPN list by host's average bandwidth."""
	return sorted(vpns, key=lambda v: -v.speed)[:min(count, len(vpns))]

def best_vpn_by_ping(vpns: [VPN], count=1) -> [VPN]:
	return sorted(vpns, key=lambda v: ping(v.ip))[:min(count, len(vpns))]
