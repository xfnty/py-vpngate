from .VPN import *
import base64


class VPNConfig:
	"""Holds VPN config file contents."""

	def __init__(self, text='', text_base64=None):
		if text_base64 is None:
			self.text = text
		else:
			self.text = bytes.decode(base64.b64decode(text_base64), encoding='utf-8')

	def save(self, filepath: str):
		"""
		Save VPN config.

		Throws:
			File IO related exceptions
		"""

		with open(filepath, 'w') as file:
			file.write(self.text)

	def from_file(filepath: str) -> object:
		"""
		Load VPN config from file.

		Returns:
			VPNConfig
			None

		Throws:
			File IO related exceptions
		"""

		with open(filepath) as file:
			content = file.read()
			if contents.isspace() or contents == '':
				return None
			return VPNConfig(text=content)

	def __eq__(self, other: object) -> bool:
		if not hasattr(other, 'text'):
			return False
		return self.text == other.text

	def __ne__(self, other: object) -> bool:
		if not hasattr(other, 'text'):
			return True
		return self.text != other.text

	def __hash__(self) -> int:
		return hash(self.text)