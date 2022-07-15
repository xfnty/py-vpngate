from .VPN import *
from .VPNConfig import *
import os


class VPNProfile:
	"""Represents system VPN profile."""
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
		"""
		No Throw
		"""

		pass

	def shutdown(self):
		"""
		No Throw
		"""

		self._nmcli_log.close()
		os.remove(self._nmcli_log_path)
		pass

	def get_profiles(self) -> [VPNProfile]:
		"""
		Retrieves all system VPN profiles.
		
		Returns:
			list: list of the VPN profiles

		No Throw
		"""

		raise NotImplementedError('Not implemented yet')

	def get_profile(self, name: str) -> VPNProfile:
		"""
		Retrieves all system VPN profiles.
		
		Returns:
			VPN
			None

		No Throw
		"""

		raise NotImplementedError('Not implemented yet')

	def create_openvpn(self, config: VPNConfig, name: str=None) -> VPNProfile:
		"""
		Creates system VPN profile.

		Returns:
			VPNProfile: profile is succeded
			None: if something went wrong

		Throws:
			OSError
		"""

		raise NotImplementedError('Not implemented yet')

	def remove(self, profile: VPNProfile) -> bool:
		"""
		Removes system VPN profile.

		No Throw
		"""

		raise NotImplementedError('Not implemented yet')

	def connect(self, profile: VPNProfile) -> bool:
		"""
		Tries to connect to system VPN profile.
		
		Returns:
			bool - success status

		No Throw
		"""

		raise NotImplementedError('Not implemented yet')

	def disconnect(self, profile: VPNProfile) -> bool:
		"""
		Disconnects system VPN profile.

		No Throw
		"""

		raise NotImplementedError('Not implemented yet')

	def modify(self, profile: VPNProfile, property: str, value: str) -> bool:
		"""
		Tries to modify system VPN profile.

		No Throw
		"""

		raise NotImplementedError('Not implemented yet')
