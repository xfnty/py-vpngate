import enum


class VPNBackend:
	def create_profile(config: str) -> bool:
		raise NotImplementedError()

	def remove_profile(config: str) -> bool:
		raise NotImplementedError()

	def get_error() -> str:
		return ''