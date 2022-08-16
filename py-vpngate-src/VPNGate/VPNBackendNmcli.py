import sys
import logging
import traceback
from .VPN import *
from .VPNConfig import *
from .VPNProfile import *
from .VPNBackend import *
from .ExecutionUtils import *
from .FilesystemUtils import *
from .FormatUtils import *


class VPNBackendNmcli(VPNBackend):
	def __init__(self):
		super().__init__()
		self.__error = ''

	def init(self, work_dir: str=None) -> bool:
		if work_dir is not None:
			self.work_dir = work_dir

		logging.debug(f"Backend CWD is '{self.work_dir}'")
			
		if sys.platform == 'win32' or sys.platform == 'cygwin':
			logging.debug("NMCLI backend is not supported on Windows")
			return False
		return True

	def get_name(self) -> str:
		return 'Network Manager CLI'

	def get_profiles(self) -> [VPNProfile]:
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
			logging.debug('Failed to GET system VPN profiles')
			logging.debug(f"nmcli output:\n{execution.stdout}")
			return []

		try:
			return parse_stdout(execution.stdout)
		except Exception as e:
			logging.debug('Failed to PARSE system VPN profiles.')
			logging.debug(f"Exception:\n{traceback.format_exception(e)}")
			return []

	def get_profile(self, name: str) -> VPNProfile:
		return next((p for p in self.get_profiles() if p.name == name), None)

	def create_profile(self, config: VPNConfig, name_to_create: str=None) -> VPNProfile:
		existing_profile = self.get_profile(name_to_create)
		if existing_profile is not None:
			self.remove_profile(existing_profile)

		filepath = os.path.join(self.work_dir, name_to_create + '.ovpn')
		config.save(filepath)

		execution = exec('nmcli', 'connection', 'import', 'type', 'openvpn', 'file', f"'{filepath}'")
		os.remove(filepath)

		if not execution.succeded or self._nmcli_error_detected(execution.stdout):
			logging.debug(f"Failed to create system VPN profile '{name_to_create}'")
			return None

		created_profile = self.get_profile(name_to_create)
		
		if created_profile is not None:
			logging.debug(f"Created VPN profile '{created_profile.name}'")
		else:
			logging.debug(f"Created VPN profile '{created_profile.name}' but could not read it")

		return created_profile


	def remove_profile(self, profile: VPNProfile) -> bool:
		execution = exec('nmcli', 'connection', 'delete', profile.uuid)
		succeded = execution.succeded and not self._nmcli_error_detected(execution.stdout)

		if not succeded:
			logging.debug(f"Failed to remove system VPN profile '{profile.name}'\n")
			logging.debug(f"nmcli output:\n{execution.stdout}")
		else:
			logging.debug(f"Removed VPN profile '{profile.name}'\n")

		return succeded

	def connect(self, profile: VPNProfile, timeout: int=5) -> bool:
		execution = exec('nmcli', 'connection', 'up', profile.uuid, timeout=timeout)
		succeded = execution.succeded and not self._nmcli_error_detected(execution.stdout)

		if not succeded:
			logging.debug(f"Failed to connect to system VPN profile '{profile.name}'")
			logging.debug(f"nmcli output:\n{execution.stdout}")
		else:
			logging.debug(f"Connected to '{profile.name}'")

		return succeded

	def disconnect(self, profile: VPNProfile) -> bool:
		logging.debug(f"Disconnecting system VPN profile '{profile.name}'...")
		execution = exec('nmcli', 'connection', 'down', profile.uuid)
		succeded = execution.succeded and not self._nmcli_error_detected(execution.stdout)

		if not succeded:
			logging.debug(f"Failed to disconnect system VPN profile '{profile.name}'\n")
			logging.debug(f"nmcli output:\n{execution.stdout}")
		else:
			logging.debug(f"Disconnected from '{profile.name}'")

		return succeded

	def _nmcli_error_detected(self, stdout: str) -> bool:
		return 'Error' in stdout
