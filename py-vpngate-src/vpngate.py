import os
import sys
import logging
import traceback
from VPNGate.VPNGateApp import * 
from VPNGate.FormatUtils import * 


if __name__ == '__main__':
	try:
		app = VPNGateApp(work_dir=get_file_dirname(__file__))
		app.run()
	except Exception as e:
		print()
		exceptions = traceback.format_exception(e)
		logging.critical(f"Caught unhandled exception:\n" + '\n'.join(exceptions))
	except KeyboardInterrupt:
		print()
	app.close()
else:
	print("Don't use 'main.py' as a library")
