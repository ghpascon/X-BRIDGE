import tomli
from app import __version__
from pathlib import Path


def get_toml_version():
	toml_path = Path(__file__).parent.parent / 'pyproject.toml'
	with open(toml_path, 'rb') as f:
		data = tomli.load(f)
		return data['project']['version']
	raise RuntimeError('Version not found in pyproject.toml')


def test_version_matches_toml():
	toml_version = get_toml_version()
	assert (
		__version__ == toml_version
	), f'App version {__version__} != pyproject.toml version {toml_version}'
