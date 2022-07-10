from util import exec, ExecutionResult
import subprocess

NMCLI_TMP_FILEPATH = './.nmcli_out'
NMCLI_TMP_FILE = open(NMCLI_TMP_FILEPATH, 'w')
NMCLI_VPN_PLUGIN = 'openvpn'



def nmcli_get_vpn_settings() -> (list, list):
	global NMCLI_TMP_FILE

	show_res = exec(['nmcli', 'connection', 'show'], stdout=NMCLI_TMP_FILE)
	
	if not show_res:
		print(f"Failed to get VPN connections list\n  nmcli output: '{NMCLI_TMP_FILEPATH}'")
		return tuple([list(), list()])

	vpn_settings_names = []
	vpn_settings_uuids = []

	lines = [line for line in show_res.stdout.split('\n') if 'vpn' in line]
	for line in lines:
		words = [word for word in line.split(' ') if word != '']
		uuid = words[-3]
		vpn_settings_uuids.append(uuid)
		uuid_start = line[:line.index(uuid)].rindex(' ')
		vpn_settings_names.append(line[:uuid_start].strip())

	return vpn_settings_names, vpn_settings_uuids



def nmcli_delete_setting(uuid: str):
	global NMCLI_TMP_FILE
	
	if not exec(['nmcli', 'connection', 'delete', uuid], stdout=NMCLI_TMP_FILE):
		print(f'Failed to run nmcli:\n  {str(e)}\n  nmcli output: \'{NMCLI_TMP_FILEPATH}\'')
		return



def nmcli_import_setting(name: str, file: str) -> bool:
	global NMCLI_TMP_FILE, NMCLI_VPN_PLUGIN

	create_result = exec(['nmcli', 'connection', 'import', 'type', NMCLI_VPN_PLUGIN, 'file', file], NMCLI_TMP_FILE)
	
	if not create_result:
		print(f'Failed to run nmcli:\n  {str(e)}\n  nmcli output: \'{NMCLI_TMP_FILEPATH}\'')
		return False
	return True



def nmcli_enable_connection(name: str) -> bool:
	global NMCLI_TMP_FILE

	connect_result = exec(['nmcli', 'connection', 'up', name], NMCLI_TMP_FILE)

	if not connect_result:
		print(f'Failed to run nmcli:\n  nmcli output: \'{NMCLI_TMP_FILEPATH}\'')
		print('Removing VPN connection settings...')

		delete_result = exec(['nmcli', 'connection', 'delete', name], NMCLI_TMP_FILE)
		
		if not delete_result:
			print(f'Failed to run nmcli:\n  nmcli output: \'{NMCLI_TMP_FILEPATH}\'')
			print('Removing VPN connection settings...')
		return False
	return True
