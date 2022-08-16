import logging
from .VPN import *
from .VPNConfig import *
from .VPNProfile import *
from .VPNBackend import *


# MSDN:
#	https://docs.microsoft.com/en-us/windows-server/remote/remote-access/vpn/vpn-device-tunnel-config
#
# StackExchange:
#	https://superuser.com/questions/1092847/create-a-vpn-connection-on-windows-command-line


class VPNBackendPowershell:
	def init(self, work_dir: str=None) -> bool:
		raise NotImplementedError("PowerShell backend doesn't work right now. Use OpenVPN instead.")

	def get_name(self) -> str:
		raise NotImplementedError("PowerShell backend doesn't work right now. Use OpenVPN instead.")
		
	def get_profiles(self) -> [VPNProfile]:
		raise NotImplementedError("PowerShell backend doesn't work right now. Use OpenVPN instead.")

	def get_profile(self, name: str) -> VPNProfile:
		raise NotImplementedError("PowerShell backend doesn't work right now. Use OpenVPN instead.")

	def create_profile(profile: VPNProfile) -> bool:
		raise NotImplementedError("PowerShell backend doesn't work right now. Use OpenVPN instead.")

	def remove_profile(profile: VPNProfile) -> bool:
		raise NotImplementedError("PowerShell backend doesn't work right now. Use OpenVPN instead.")

	def connect(profile: VPNProfile, timeout: int=5) -> bool:
		raise NotImplementedError("PowerShell backend doesn't work right now. Use OpenVPN instead.")

	def disconnect(profile: VPNProfile, timeout: int=5) -> bool:
		raise NotImplementedError("PowerShell backend doesn't work right now. Use OpenVPN instead.")
