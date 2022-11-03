from .VPN import *
from .NetworkingUtils import *
from .VPNManager import *
from .Constants import *


class VPNTestSummary:
	def __init__(self, available=False):
		self.available = available


class VPNTester:
	def __init__(self, vpn_manager: VPNManager):
		self.vpn_manager = vpn_manager

	def test_vpn(self, vpn: VPN, timeout: int=1) -> VPNTestSummary:
		return VPNTestSummary(try_connect(vpn.ip, 443, timeout=timeout))

	def test_vpn_with_vpnmanager(self, vpn: VPN, timeout: int=5) -> VPNTestSummary:
		# Duplicate from VPNGateApp.py:276
		profile = self.vpn_manager.create_profile(
			config=vpn.config, name=APP_VPN_PROFILE_NAME
		)

		summ = VPNTestSummary(available=False)

		if profile is None:
			return summ

		if self.vpn_manager.connect(profile, timeout=timeout):
			summ.available = True

		self.vpn_manager.disconnect(profile)
		self.vpn_manager.remove(profile)

		return summ
