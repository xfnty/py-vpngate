import os
import sys
import logging
import traceback
from VPNGate.VPNGateApp import * 
from VPNGate.FormatUtils import * 


if __name__ == '__main__':
	try:
		app = VPNGateApp()
		app.run(work_dir=get_file_dirname(__file__))
	except Exception as e:
		app.close()
		logging.critical('Unhandled exception:\n' + '\n'.join(traceback.format_exception(e)))
	except KeyboardInterrupt:
		print()
	app.close()
else:
	print("Don't use 'main.py' as a library")
