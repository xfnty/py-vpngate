from VPNGate.VPNGateApp import * 


if __name__ == '__main__':
	app = VPNGateApp()

	try:
		app.run()
	except KeyboardInterrupt:
		print()
	finally:
		app.close()

else:
	print("Don't use 'main.py' as module")
