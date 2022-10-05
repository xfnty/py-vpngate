from .VPN import *
from .NetworkingUtils import *


class VPNTestSummary:
	def __init__(self, available=False):
		self.available = available


class VPNTester:
	def test_vpn(self, vpn: VPN, timeout: int=5) -> VPNTestSummary:
		return VPNTestSummary(try_connect(vpn.ip, 443, timeout=timeout))

	def test_vpns(self, vpn_list: [VPN], timeout: int=5) -> {VPN: VPNTestSummary}:
		summary = {}
		for vpn in vpn_list:
			summary[vpn] = test_vpn(vpn, timeout)
		return summary
