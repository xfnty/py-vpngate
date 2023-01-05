from .FormatUtils import *
from .VPNConfig import *


class VPN:
	"""Holds common information about VPN host."""

	def __init__(
			self,
			host='none',
			ip='none',
			country_short='none',
			country_long='none',
			ping=-1,
			traffic=-1,
			sessions=-1,
			speed=-1,
			uptime=-1,
			description='none',
			operator='none',
			config_base64=''):
		self.host = host
		self.ip = ip
		self.country_short = country_short
		self.country_long = country_long
		self.ping = ping
		self.traffic = traffic
		self.sessions = sessions
		self.speed = speed
		self.uptime = uptime
		self.operator = operator
		self.description = description
		self.config = VPNConfig(text_base64=config_base64)

	def from_cache_entry(entry: dict):
		return VPN(
			entry['HostName'],
			entry['IP'],
			entry['CountryShort'],
			entry['CountryLong'],
			int(entry['Ping']) if entry['Ping'].isnumeric() else -1,
			int(entry['TotalTraffic']) if entry['TotalTraffic'].isnumeric() else -1,
			int(entry['NumVpnSessions']) if entry['NumVpnSessions'].isnumeric() else -1,
			int(entry['Speed']) if entry['Speed'].isnumeric() else -1,
			int(entry['Uptime']) if entry['Uptime'].isnumeric() else -1,
			entry['Message'],
			entry['Operator'],
			entry['OpenVPN_ConfigData_Base64']
		)

	def print_description(self):
		print('{:<15} {}'.format('Host name:', self.host))
		print('{:<15} {}'.format('IP:', self.ip))
		print('{:<15} {} ms'.format('Ping:', self.ping))
		print('{:<15} {}ps'.format('Speed:', format_bytes(self.speed)))
		print('{:<15} {}'.format('Up time:', self.uptime))
		print('{:<15} {}'.format('VPN sessions:', self.sessions))
		print('{:<15} {}'.format('Total traffic:', format_bytes(self.traffic)))
		print('{:<15} {}'.format('Country:', self.country_long))
		print('{:<15} {}'.format('Operator:', self.operator))
		print('{:<15} {}'.format('Description:', self.description))

	def dump(self):
		config_base64 = bytes.decode(base64.b64encode(bytes(self.config.text, encoding='utf-8')), encoding='utf-8')
		return f"{self.host},{self.ip},0,{self.ping},{self.speed}," +\
			f"{self.country_long},{self.country_short},{self.sessions},{self.uptime},," +\
			f"{self.traffic},,{self.operator},," +\
			f"{config_base64}"

	def __str__(self):
		return "{:<20}- {} {:>4} ms {:>12}ps {:>4} sessions".format(
			self.host,
			self.country_short,
			str(self.ping),
			str(format_bytes(self.speed)),
			str(self.sessions)
		)

	def __eq__(self, other: object) -> bool:
		if not (hasattr(other, 'host') and hasattr(other, 'ip') and hasattr(other, 'config')):
			return False
		return self.host == other.host and self.ip == other.ip and self.config == other.config

	def __ne__(self, other: object) -> bool:
		if not (hasattr(other, 'host') and hasattr(other, 'ip') and hasattr(other, 'config')):
			return True
		return self.host != other.host or self.ip != other.ip or self.config != other.config

	def __hash__(self) -> int:
		return hash(self.config.__hash__())