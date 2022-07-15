import subprocess
import time


class ExecutionResult:
	"""Holds STDOUT of the process and its exit status."""

	def __init__(self, succeded, stdout=''):
		self.stdout = stdout
		self.succeded = succeded

	def __nonzero__(self) -> bool:
		return self.succeded

	def __str__(self) -> str:
		return f"Execution {'succeded' if self.succeded else 'failed'}" +\
			f"\nstdout:\n{self.stdout}"


def exec(*args: list, timeout=10) -> ExecutionResult:
	"""
	Executes given commands and waits for them to finish.

	No Throw
	"""
	output = ''
	try:
		output = subprocess.check_output(' '.join(args), shell=True, stderr=subprocess.STDOUT, timeout=timeout)
		return ExecutionResult(True, output.decode('utf-8'))
	except Exception as e:
		#raise e
		return ExecutionResult(False, output)
	
	"""
	stdout = ''
	#try:
	result = subprocess.check_output(
		args,
		shell=True#,
		#stderr=subprocess.STDOUT
	)
	stdout = '' if result is None else result.decode('utf-8')
	return ExecutionResult(True, stdout)
	#except Exception as e:
	#	return ExecutionResult(False, stdout)
	"""
