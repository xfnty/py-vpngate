from .VPN import *
from .VPNConfig import *
from .VPNProfile import *
from .ExecutionUtils import *
from .FilesystemUtils import *
import os


VPNGATE_NMCLI_OUTPUT_FILENAME = '.vpngate_nmcli_output'


class VPNManager:
	"""Wrapper around 'nmcli' utility"""

	def __init__(self):
		self.work_dir = get_file_dirname(__file__)
		self._nmcli_log_path = None
		self._nmcli_log = None

	def init(self, work_dir=None):
		global VPNGATE_NMCLI_OUTPUT_FILENAME
		
		if work_dir is not None:
			self.work_dir = work_dir
		self._nmcli_log_path = os.path.join(work_dir, VPNGATE_NMCLI_OUTPUT_FILENAME)
		self._nmcli_log = open(self._nmcli_log_path, 'w')

	def shutdown(self):
		"""
		No Throw
		"""

		try:
			self._nmcli_log.close()
			os.remove(self._nmcli_log_path)
		except FileNotFoundError:
			pass

	def get_profiles(self) -> [VPNProfile]:
		"""
		Retrieves all system VPN profiles.
		
		Returns:
			list: list of the VPN profiles

		No Throw
		"""

		def parse_stdout(stdout: str) -> [VPNProfile]:
			vpn_settings_names = []
			vpn_settings_uuids = []
			lines = [line for line in stdout.split('\n') if 'vpn' in line]
			for line in lines:
				words = [word for word in line.split(' ') if word != '']
				uuid = words[-3]
				vpn_settings_uuids.append(uuid)
				uuid_start = line[:line.index(uuid)].rindex(' ')
				vpn_settings_names.append(line[:uuid_start].strip())
			profiles = []
			for tup in zip(vpn_settings_names, vpn_settings_uuids):
				profiles.append(VPNProfile(tup[0], tup[1]))
			return profiles

		execution = exec('nmcli', 'connection', 'show')
		if not execution.succeded or self._nmcli_error_detected(execution.stdout):
			return []
		try:
			return parse_stdout(execution.stdout)
		except Exception:
			return []

	def get_profile(self, name: str) -> VPNProfile:
		"""
		Retrieves all system VPN profiles.
		
		Returns:
			VPN
			None
		"""

		return next((p for p in self.get_profiles() if p.name == name), None)

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

	def _nmcli_error_detected(self, stdout: str) -> bool:
		return 'Error' in stdout
