import subprocess


class ExecutionResult:
	"""Holds STDOUT of the process and its exit status."""

	def __init__(self, succeded, stdout=''):
		self.stdout = stdout
		self.succeded = succeded

	def __nonzero__(self) -> bool:
		return self.succeded

	def __str__(self) -> str:
		return f"Execution {'succeded' if self.succeded else 'failed'}" +\
			'' if self.succeded else f'\nError:\n{self.stdout}'


def exec(*args: list) -> ExecutionResult:
	"""
	Executes given commands and waits for them to finish.

	No Throw
	"""
	
	stdout = ''
	try:
		result = subprocess.check_output(
			args,
			shell=False,
			stderr=subprocess.STDOUT
		)
		stdout = '' if result is None else result.decode('utf-8')
		return ExecutionResult(True, stdout)
	except Exception as e:
		return ExecutionResult(False, stdout)
