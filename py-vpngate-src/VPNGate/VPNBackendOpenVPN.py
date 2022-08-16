import logging
from .VPN import *
from .VPNConfig import *
from .VPNProfile import *
from .VPNBackend import *


class VPNBackendOpenVPN:
	def init(self, work_dir: str=None) -> bool:
		raise NotImplementedError('OpenVPN backend is not implemented yet')

	def get_name(self) -> str:
		raise NotImplementedError('OpenVPN backend is not implemented yet')
		
	def get_profiles(self) -> [VPNProfile]:
		raise NotImplementedError('OpenVPN backend is not implemented yet')

	def get_profile(self, name: str) -> VPNProfile:
		raise NotImplementedError('OpenVPN backend is not implemented yet')

	def create_profile(config: VPNConfig) -> bool:
		raise NotImplementedError('OpenVPN backend is not implemented yet')

	def remove_profile(profile: VPNProfile) -> bool:
		raise NotImplementedError('OpenVPN backend is not implemented yet')

	def connect(profile: VPNProfile, timeout: int=5) -> bool:
		raise NotImplementedError('OpenVPN backend is not implemented yet')

	def disconnect(profile: VPNProfile) -> bool:
		raise NotImplementedError('OpenVPN backend is not implemented yet')
