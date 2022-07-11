from vpn_util import *
from nmcli_util import *
from util import ping, format_bytes


PAGE_SIZE = 5
ARGS = None
ARG_PARSER = None



def list_vpns(vpns: list):
	for vpn in sorted(vpns, key=lambda vpn: vpn['CountryShort']):
		print(format_vpn_entry(vpn))
	print(f'Total {len(vpns)} VPNs')



def list_lowest_ping(vpns: list):
	vpns = sorted(vpns, key=lambda vpn: 1000 if not vpn['Ping'].isnumeric() else int(vpn['Ping']))
	
	print('VPNs with lowest ping:')
	for i in range(3):
		print(f'  {format_vpn_entry(vpns[i])}')



def save_openvpn_config(vpns: list, hostname: str, verbose=True) -> str:
	if hostname == '':
		print('Empty profile name is given')
		return None

	vpn = next((v for v in vpns if v['HostName'] == hostname), None)
	if vpn == None:
		print(f"Can not find profile for '{hostname}'")
		return None

	try:
		filepath = f"{vpn['HostName']}.ovpn"
		with open(filepath, 'wb') as file:
			file.write(base64.b64decode(vpn['OpenVPN_ConfigData_Base64']))
		if verbose:
			print(f"OpenVPN config saved to '{filepath}'")
		return filepath
	except Exception as e:
		print(f"Failed to save '{filepath}': {str(e)}")

	return None



def connect_using_nmcli(openvpn_config_filepath: str) -> bool:
	connection_name = openvpn_config_filepath[:openvpn_config_filepath.rindex('.')]

	vpn_settings_names, vpn_settings_uuids = nmcli_get_vpn_settings()

	if connection_name in vpn_settings_names:
		print(f"VPN setting '{connection_name}' already exists. Deleting...")
		nmcli_delete_setting(vpn_settings_uuids[vpn_settings_names.index(connection_name)])
	
	print(f"Creating '{connection_name}' VPN setting...")
	if not nmcli_import_setting(connection_name, openvpn_config_filepath):
		return False

	print('Connecting to VPN...')
	if not nmcli_enable_connection(connection_name):
		return False

	return True



def connect_using_openvpn(openvpn_config_filepath: str) -> bool:
	print('Connecting using just OpenVPN is not implemented yet')
	return False



def connect_vpn(vpns: list, hostname: str):
	openvpn_config_filepath = save_openvpn_config(vpns, hostname, verbose=False)
	if openvpn_config_filepath == None:
		return

	if which('nmcli') is not None:
		if connect_using_nmcli(openvpn_config_filepath):
			print(f"Ping to google.com: {ping('google.com', count=3)} ms")
	elif which('openvpn') is not None:
		connect_using_openvpn(openvpn_config_filepath)
	else:
		print('OpenVPN is not installed')

	os.remove(openvpn_config_filepath)



def show_hostname(vpns: list, hostname: str):
	vpn = next((v for v in vpns if v['HostName'] == hostname), None)
	if vpn == None:
		print(f"Can not find VPN with name '{hostname}'")
		return
	print('{:<15} {}'.format('Host name:', vpn['HostName']))
	print('{:<15} {}'.format('IP:', vpn['IP']))
	print('{:<15} {} ms'.format('Ping:', vpn['Ping']))
	print('{:<15} {}'.format('Speed:', format_bytes(int(vpn['Speed']))))
	print('{:<15} {}'.format('Up time:', vpn['Uptime']))
	print('{:<15} {}'.format('VPN sessions:', vpn['NumVpnSessions']))
	print('{:<15} {}'.format('Total users:', vpn['TotalUsers']))
	print('{:<15} {}'.format('Total traffic:', format_bytes(int(vpn['TotalTraffic']))))
	print('{:<15} {}'.format('Log type:', vpn['LogType']))
	print('{:<15} {}'.format('Operator:', vpn['Operator']))
	print('{:<15} {}'.format('Description:', vpn['Message']))



def main():
	global ARGS, ARG_PARSER
	
	vpns = update_vpn_cache(ARGS.should_update)

	if ARGS.print_list:
		list_vpns(vpns)
	elif ARGS.connect_hostname != None:
		connect_vpn(vpns, ARGS.connect_hostname)
	elif ARGS.profile_name != None:
		save_openvpn_config(vpns, ARGS.profile_name)
	elif ARGS.show_best:
		list_lowest_ping(vpns)
	elif ARGS.show_hostname != None:
		show_hostname(vpns, ARGS.show_hostname)
	else:
		ARG_PARSER.print_help()



if __name__ == '__main__':
	global VPN_CACHE_FILEPATH

	try:
		epilog = f"VPN cache '{VPN_CACHE_FILEPATH}' does not exist."
		if path.exists(VPN_CACHE_FILEPATH):
			epilog = f"VPN cache '{VPN_CACHE_FILEPATH}' contains {len(parse_vpn_cache(verbose=False))} entries."

		ARG_PARSER = argparse.ArgumentParser(
			prog='list-vpn',
			description='Parses public VPN lists and gives best VPN suggestions.',
			epilog=epilog
		)
		ARG_PARSER.add_argument('-l', dest='print_list', action='store_true', help=f"list cached VPN servers")
		ARG_PARSER.add_argument('-u', dest='should_update', action='store_true', help=f"update VPN list cache")
		ARG_PARSER.add_argument('-b', dest='show_best', action='store_true', help=f"show VPNs with lowest ping")
		ARG_PARSER.add_argument('-d', metavar='HOSTNAME', dest='profile_name', const=None, help=f"save OpenVPN config for given server")
		ARG_PARSER.add_argument('-c', metavar='HOSTNAME', dest='connect_hostname', const=None, help=f"connect to known VPN server using its hostname")
		ARG_PARSER.add_argument('-s', metavar='HOSTNAME', dest='show_hostname', const=None, help=f"show more information about specified host")
		ARGS = ARG_PARSER.parse_args()
		main()
	except KeyboardInterrupt:
		print()
