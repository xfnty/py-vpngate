

def try_import(module_name: str, pip_name: str = None):
	from importlib import import_module
	mod = import_module(module_name)
	if mod == None:
		print(f"Module '{module_name}' is not installed.")
		print('You can install it by running')
		print(f'  pip install {module_name if pip_name == None else pip_name}')
		quit()
	return mod


def format_bytes(b: int):
	b = float(b)
	Kb = float(1024)
	Mb = float(Kb ** 2) # 1,048,576
	Gb = float(Kb ** 3) # 1,073,741,824
	Tb = float(Kb ** 4) # 1,099,511,627,776

	if b < Kb:
		return '{0} {1}'.format(b,'bytes' if 0 == b > 1 else 'byte')
	elif Kb <= b < Mb:
		return '{0:.2f} Kb'.format(b / Kb)
	elif Mb <= b < Gb:
		return '{0:.2f} Mb'.format(b / Mb)
	elif Gb <= b < Tb:
		return '{0:.2f} Gb'.format(b / Gb)
	elif Tb <= b:
		return '{0:.2f} Tb'.format(b / Tb)


class ExecutionResult:
	def __init__(self, stdout="", error_code=-1):
		self.stdout = stdout
		self.error_code = error_code
	def __nonzero__(self):
		return self.error_code == 0


def exec(args: list, stdout=None) -> ExecutionResult:
	import subprocess
	try:
		proc = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		while proc.poll():
			pass
		out_text = bytes.decode(proc.stdout.read()) + '\n' + bytes.decode(proc.stderr.read())
		if stdout != None:
			stdout.write(out_text)
			stdout.flush()
		return ExecutionResult(out_text, 0 if 'Error' not in out_text and proc.returncode == None else -1)
	except Exception as e:
		print(f"Failed to run '{args[0]}': {str(e)}")
		return ExecutionResult(str(e), -1)


def ping(host: str, count: int = 1) -> float:
	if count == 0:
		return 0

	res = exec(['ping', '-c', str(count), host])
	
	if not res:
		print(f"Ping '{host}' failed")
		return 0

	ping_sum = 0
	try:
		lines = res.stdout.split('\n')
		for i in range(1, 1 + count):
			ping_sum += float(lines[i][lines[i].rindex('=')+1:lines[i].rindex(' ')])
	except Exception as e:
		print('Failed to parse ping output: ', str(e))
		return 0
	return round(ping_sum / count, 2)