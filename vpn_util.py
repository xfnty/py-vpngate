import util
requests = util.try_import('requests')
from os import path, system
from shutil import which
import os
import base64
import argparse
import csv
import subprocess


API_URL = 'https://www.vpngate.net/api/iphone'
VPN_CACHE_FILEPATH = '.vpngate_cache'
VPN_LIST = list()



def get_vpn_cache_entries_count() -> list:
	global VPN_LIST
	return len(VPN_LIST)



def make_request(url: str) -> object:
	resp = None
	try:
		resp = requests.get(url)
	except Exception as e:
		print(f"Request failed:\n  '{url}'\n  {str(e)}")
		return False
	if not resp:
		print(f"Request failed:\n  '{url}'\n  Code: {resp.status_code}")
		return False
	return resp



def download_vpn_cache() -> bool:
	global VPN_CACHE_FILEPATH, API_URL
	
	print('Updating VPN cache...')
	resp = make_request(API_URL)
	
	if not resp:
		return False

	try:
		with open(VPN_CACHE_FILEPATH, 'wt') as file:
			text = bytes.decode(resp.content, encoding='utf-8')
			# Remove '*vpn_servers\n#' and '*\n' at the end
			file.write(text[text.index('\n')+2:text.rindex('*')-1])
	except Exception as e:
		print(f'Failed to download VPN cache: {str(e)}')



def parse_vpn_cache(verbose = True) -> list:
	try:
		with open(VPN_CACHE_FILEPATH) as file:
			return list(csv.DictReader(file))
	except Exception as e:
		if verbose:
			print(f"Failed to parse '{VPN_CACHE_FILEPATH}': {str(e)}")
	return list()



def update_vpn_cache(update_cache = False, verbose = True):
	global VPN_CACHE_FILEPATH, VPN_LIST

	if not path.exists(VPN_CACHE_FILEPATH) or update_cache:
		download_vpn_cache()

	VPN_LIST = parse_vpn_cache(verbose)
	return VPN_LIST



def format_vpn_entry(vpn: dict):
	return "{:<20}- {} {:>6}ms {:>14} {:>4} sessions".format(
			vpn['HostName'],
			vpn['CountryShort'],
			vpn['Ping'],
			util.format_bytes(int(vpn['TotalTraffic'])),
			vpn['NumVpnSessions']
		)
