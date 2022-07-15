from VPNGate.VPNGateApp import * 
from VPNGate.FormatUtils import * 
import os

if __name__ == '__main__':
	app = VPNGateApp()

	try:
		app.run(work_dir=get_file_dirname(__file__))
	except Exception as e:
		app.close()
		raise e
	except KeyboardInterrupt:
		print()
	app.close()

else:
	print("Don't use 'main.py' as a library")
