from .NetworkingUtils import *
from .VPN import *
from .VPNManager import *
import concurrent.futures
import socket


def best_vpn_by_speed(vpns: [VPN], count=3) -> [VPN]:
	"""Sorts VPN list by host's average bandwidth."""

	return sorted(vpns, key=lambda v: -v.speed)[:min(count, len(vpns))]


def best_vpn_by_ping(vpns: [VPN], count=1, max_workers=50, timeout=3) -> [VPN]:
	def test_connection(vpn: VPN) -> (VPN, float):
		try:
			#print(f'-> {vpn.ip}')
			sock = socket.create_connection((vpn.ip, 80), timeout=timeout)
			sock.close()
		except Exception as e:
			#print(f"Connection to '{vpn.ip}' failed: {e.__class__.__name__}: {str(e)}")
			pass
		return (vpn, -1)

	results = []
	with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
		try:
			futures = [pool.submit(test_connection, vpn) for vpn in vpns]

			for future in concurrent.futures.as_completed(futures):
				results.append(future.result())
		except KeyboardInterrupt:
			pool.shutdown(wait=False)

	results = map(lambda r: r[0], sorted(filter(lambda r: r[1] >= 0, results), key=lambda r: r[1]))
	return list(results)
