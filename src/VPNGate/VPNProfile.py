
class VPNProfile:
	"""Represents system VPN profile."""

	def __init__(self, name='none', uuid='none'):
		self.name = name
		self.uuid = uuid

	def __str__(self) -> str:
		return f"VPNProfile('{self.name}', {self.uuid})"
