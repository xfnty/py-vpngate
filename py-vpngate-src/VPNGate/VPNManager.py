import os
import sys
import enum
import logging
import traceback
from .VPN import *
from .VPNConfig import *
from .VPNProfile import *
from .VPNBackend import *
from .VPNBackendNmcli import *
from .VPNBackendOpenVPN import *
from .VPNBackendPowershell import *
from .ExecutionUtils import *
from .FilesystemUtils import *


class VPNManager:
	def __init__(self):
		self.backend = None
		self.work_dir = get_file_dirname(__file__)

	def init(self, backend: VPNBackend=None, work_dir=None) -> bool:
		self.backend = backend
		if backend is None:
			self.backend = self.get_os_specific_backend()
		
		if not self.backend.init(work_dir=work_dir):
			logging.error(f"Backend '{self.backend.get_name()}' failed to initialize.")
			return False
		
		if work_dir is not None:
			self.work_dir = work_dir
		
		logging.debug(f"VPNManager initialized (working directory is '{self.work_dir}')")
		logging.debug(f"VPN Backend is '{self.backend.get_name()}'")

		return True

	def shutdown(self) -> None:
		logging.debug(f"VPNManager shut down")

	def get_profiles(self) -> [VPNProfile]:
		return self.backend.get_profiles()

	def get_profile(self, name: str) -> VPNProfile:
		return self.backend.get_profile(name)

	def create_profile(self, config: VPNConfig, name: str) -> VPNProfile:
		logging.debug(f"Creating system VPN profile '{name}'...")
		return self.backend.create_profile(config, name)

	def remove(self, profile: VPNProfile) -> bool:
		logging.debug(f"Removing system VPN profile '{profile.name}'...")
		return self.backend.remove_profile(profile)

	def connect(self, profile: VPNProfile, timeout=10) -> bool:
		logging.debug(f"Connecting to system VPN profile '{profile.name}'... (timeout={timeout})")
		return self.backend.connect(profile, timeout)

	def disconnect(self, profile: VPNProfile) -> bool:
		logging.debug(f"Disconnecting system VPN profile '{profile.name}'...")
		return self.backend.disconnect(profile)

	def get_os_specific_backend(self) -> VPNBackend:
		if sys.platform == 'win32' or sys.platform == 'cygwin':
			return VPNBackendPowershell()
		elif sys.platform == 'linux':
			return VPNBackendNmcli()
		else:
			return VPNBackendOpenVPN()
