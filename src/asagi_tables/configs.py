from functools import cache
import os
import tomllib

conf_file = 'asagi.toml'
alt_conf_file = 'config.toml'

def _find_project_root() -> str | None:
	"""Find the project root by looking for asagi.tpl.toml or pyproject.toml"""
	# Start from this file's directory and walk up
	current = os.path.abspath(os.path.dirname(__file__))
	# Go up from src/asagi_tables/configs.py to project root
	# That's 2 levels up: src/asagi_tables -> src -> project root
	for _ in range(2):
		current = os.path.dirname(current)
		if os.path.exists(os.path.join(current, 'asagi.tpl.toml')) or os.path.exists(os.path.join(current, 'pyproject.toml')):
			return current
	return None

def load_config() -> dict:
	# First check current working directory (for backward compatibility)
	if os.path.exists(conf_file):
		config_path = os.path.abspath(conf_file)
		print(f'Using config file: {config_path}')
		return _load_config_toml(conf_file)
	elif os.path.exists(alt_conf_file):
		config_path = os.path.abspath(alt_conf_file)
		print(f'Using config file: {config_path}')
		return _load_config_toml(alt_conf_file)
	
	# Then check project root directory
	project_root = _find_project_root()
	if project_root:
		root_conf = os.path.join(project_root, conf_file)
		root_alt_conf = os.path.join(project_root, alt_conf_file)
		if os.path.exists(root_conf):
			config_path = os.path.abspath(root_conf)
			print(f'Using config file: {config_path}')
			return _load_config_toml(root_conf)
		elif os.path.exists(root_alt_conf):
			config_path = os.path.abspath(root_alt_conf)
			print(f'Using config file: {config_path}')
			return _load_config_toml(root_alt_conf)
	
	raise FileNotFoundError("No config file found in current working directory or project root")

@cache
def _load_config_toml(filename: str) -> dict:
	with open(filename, 'rb') as f:
		return tomllib.load(f)

conf = load_config()
db_conf = conf['db']
