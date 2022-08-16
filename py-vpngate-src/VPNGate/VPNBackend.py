from .VPN import *
from .VPNConfig import *
from .VPNProfile import *
from .FilesystemUtils import *


class VPNBackend:
	def __init__(self):
		self.work_dir = get_file_dirname(__file__)

	def init(self, work_dir: str=None) -> bool:
		raise NotImplementedError()

	def get_name(self) -> str:
		raise NotImplementedError()

	def get_profiles(self) -> [VPNProfile]:
		raise NotImplementedError()

	def get_profile(self, name: str) -> VPNProfile:
		raise NotImplementedError()

	def create_profile(config: VPNConfig) -> bool:
		raise NotImplementedError()

	def remove_profile(profile: VPNProfile) -> bool:
		raise NotImplementedError()

	def connect(profile: VPNProfile, timeout: int=5) -> bool:
		raise NotImplementedError()

	def disconnect(profile: VPNProfile) -> bool:
		raise NotImplementedError()
