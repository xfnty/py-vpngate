from .VPN import *
import os


class VPNProfile:
	def __init__(self, name='none', uuid='none'):
		self.name = name
		self.uuid = uuid


class VPNManager:
	"""Wrapper around 'nmcli' utility"""

	def __init__(self, log_path='./.vpngate_nmcli_log'):
		self._nmcli_log_path = log_path
		self._nmcli_log = open(self._nmcli_log_path, 'w')
		pass

	def init(self):
		
		pass

	def shutdown(self):
		self._nmcli_log.close()
		os.remove(self._nmcli_log_path)
		pass

	def get_profiles(self) -> [VPNProfile]:
		raise Exception('Not implemented yet')

	def get_profile(self, name: str) -> VPNProfile:
		raise Exception('Not implemented yet')

	def create_openvpn(self, config: str, name: str=None) -> bool:
		raise Exception('Not implemented yet')

	def remove(self, profile: VPNProfile) -> bool:
		raise Exception('Not implemented yet')

	def connect(self, profile: VPNProfile) -> bool:
		raise Exception('Not implemented yet')

	def disconnect(self, profile: VPNProfile) -> bool:
		raise Exception('Not implemented yet')

	def modify(self, profile: VPNProfile, property: str, value: str) -> bool:
		raise Exception('Not implemented yet')
