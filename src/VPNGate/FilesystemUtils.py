import os


def get_file_dirname(script_filepath: str) -> str:
	return os.path.dirname(os.path.realpath(script_filepath))
