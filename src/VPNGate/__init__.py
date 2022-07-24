import logging


_console_formatter = logging.Formatter('%(message)s')
_file_formatter = logging.Formatter('(%(asctime)s) %(levelname)s: %(message)s')

_ch = logging.StreamHandler()
_ch.setLevel(logging.INFO)
_ch.setFormatter(_console_formatter)

_fh = logging.FileHandler('./vpngate.log', mode='w')
_fh.setLevel(logging.NOTSET)
_fh.setFormatter(_file_formatter)

logging.basicConfig(
	level=logging.DEBUG,
	handlers=[_ch, _fh]
)
