import csv
import base64
from os import path, remove
from VPNGate.NetworkingUtils import *
from VPNGate.FormatUtils import *


VPNGATE_API_URL = 'https://www.vpngate.net/api/iphone'


class VPN:
	def __init__(
			self,
			host='none',
			ip='none',
			country_short='none',
			ping=-1,
			traffic=-1,
			sessions=-1,
			speed=-1,
			uptime=-1,
			description='none',
			operator='none',
			config_base64='',
			):
		self.host = host
		self.ip = ip
		self.country_short = country_short
		self.ping = ping
		self.traffic = traffic
		self.sessions = sessions
		self.speed = speed
		self.uptime = uptime
		self.operator = operator
		self.description = description
		self.config_base64 = config_base64

	def from_cache_entry(entry: dict):
		return VPN(
			entry['HostName'],
			entry['IP'],
			entry['CountryShort'],
			int(entry['Ping']),
			int(entry['TotalTraffic']),
			int(entry['NumVpnSessions']),
			int(entry['Speed']),
			int(entry['Uptime']),
			entry['Message'],
			entry['Operator'],
			entry['OpenVPN_ConfigData_Base64']
		)
	
	def print_description(self):
		print('{:<15} {}'.format('Host name:', self.host))
		print('{:<15} {}'.format('IP:', self.ip))
		print('{:<15} {} ms'.format('Ping:', self.ping))
		print('{:<15} {}'.format('Speed:', format_bytes(self.speed)))
		print('{:<15} {}'.format('Up time:', self.uptime))
		print('{:<15} {}'.format('VPN sessions:', self.sessions))
		print('{:<15} {}'.format('Total traffic:', format_bytes(self.traffic)))
		print('{:<15} {}'.format('Operator:', self.operator))
		print('{:<15} {}'.format('Description:', self.description))

	def __str__(self):
		return "{:<20}- {} {:>4} ms {:>12} {:>4} sessions".format(
			self.host,
			self.country_short,
			str(self.ping),
			str(format_bytes(self.traffic)),
			str(self.sessions)
		)



class VPNGateCache:
	def __init__(self):
		self.cache_filepath = './.vpngate_cache'
		self.cache_entries = []
		pass


	def init(self, verbose=True) -> bool:
		if not self.is_updated():
			self.update(verbose)
		try:
			file = open(self.cache_filepath)
			if not file:
				raise Exception('invalid cache file')
			if not self._parse_cache(file, verbose):
				file.close()
				return False
			file.close()
		except Exception as e:
			if verbose:
				print(f"Failed to open cache file: {str(e)}")
			return False
		return True


	def update(self, verbose=True) -> bool:
		try:
			file = open(self.cache_filepath, 'w')
			if not self._download_vpn_list(file, verbose):
				file.close()
				return False
			file.close()
		except Exception as e:
			print(f"Failed to update cache: {str(e)}")
			return False
		return True
	
	
	def is_updated(self) -> bool:
		if not path.exists(self.cache_filepath):
			return False
		try:
			with open(self.cache_filepath) as file:
				if not self._parse_cache(file) or len(self.cache_entries) == 0:
					file.close()
					return False
		except Exception as e:
			return False
		return True


	def save_config(self, hostname: str, output_filepath=None, verbose=True) -> bool:
		if output_filepath == None:
			output_filepath = hostname + '.ovpn'
		try:
			vpn = self.find(host=hostname)
			if vpn == None:
				raise Exception(f"VPN entry was not found")
			with open(output_filepath, 'wb') as file:
				file.write(base64.b64decode(vpn.config_base64))
		except Exception as e:
			if verbose:
				print(f"Failed to save OpenVPN config: {str(e)}")
			remove(output_filepath)
			return False
		if verbose:
			print(f"Config saved to '{output_filepath}'")
		return True


	def get_suggestions(self, count=3, verbose=True) -> [VPN]:
		self.cache_entries.sort(key=lambda v: v.ping if v.ping > 0 else 1000)
		return self.cache_entries[:count]


	def entries(self) -> [VPN]:
		return self.cache_entries


	def _parse_cache(self, file: object, verbose=True) -> bool:
		try:
			self.cache_entries = [VPN.from_cache_entry(e) for e in list(csv.DictReader(file))]
		except Exception as e:
			if verbose:
				print(f"Failed to parse cache: {str(e)}")
			return False
		return True


	def find(self, host: str) -> VPN:
		return next((v for v in self.cache_entries if v.host == host), None)


	def _download_vpn_list(self, file: object, verbose=True) -> bool:
		global VPNGATE_API_URL
		if verbose:
			print('Retrieving VPN list...')
		resp = make_request(VPNGATE_API_URL, verbose)
		if not resp:
			return False
		try:
			text = bytes.decode(resp.content, encoding='utf-8')
			# Remove '*vpn_servers\n#' and '*\n' at the end
			file.write(text[text.index('\n')+2:text.rindex('*')-1])
		except Exception as e:
			if verbose:
				print(f'Failed to store VPN cache: {str(e)}')
			return False
		return True
