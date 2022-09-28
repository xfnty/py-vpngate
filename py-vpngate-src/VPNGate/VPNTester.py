from .VPN import *
from .NetworkingUtils import *
from .VPNGateCache import *


class VPNTester:
	def __init__(self, cache: VPNGateCache):
		self.cache = cache