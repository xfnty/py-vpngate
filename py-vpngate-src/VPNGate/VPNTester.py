from .VPN import *
from .NetworkingUtils import *


class VPNTestSummary:
	def __init__(self):
		self.available = None
		self.ping = None
		self.bandwidth = None


class VPNTester:
	def test_vpn(self, vpn: VPN, timeout: int=5) -> VPNTestSummary:
		raise NotImplementedError()
