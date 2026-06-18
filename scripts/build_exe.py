"""
poetry run python build_exe.py
"""

# Remove build directory after completion
import shutil
import os

import PyInstaller.__main__
from PyInstaller.utils.hooks import collect_all, collect_submodules
import tomli

# === USER CONFIGURATION ===
EXE_PATH = 'TEMP'  # Base folder to store builds
ENTRY_SCRIPT = 'main.py'  # Main script
APP_NAME = 'main'  # Final executable name
EXTRA_FOLDERS = [
	'app',
	'examples',
	'docs',
]  # Extra folders to include in the build

# === Icon path (platform dependent) ===
if os.name == 'nt':
	icon_file = 'logo.ico'
else:
	icon_file = 'logo.png'  # PyInstaller on Linux usually uses PNG

try:
	icon_path = os.path.abspath(os.path.join('app', 'static', 'icons', icon_file))
except Exception as e:
	print(f'[WARN] Could not find icon file: {e}')
	icon_path = None

# === Define output folder ===
output_dir = EXE_PATH
work_dir = os.path.join(output_dir, 'build')

# Create folders if they don't exist
os.makedirs(output_dir, exist_ok=True)
os.makedirs(work_dir, exist_ok=True)

# === Extra hidden imports ===
manual_hidden = [
	'uvicorn.config',
	'uvicorn.main',
	'uvicorn.loops.auto',
]


# === Collect submodules for serial and serial_asyncio ===
def safe_collect_submodules(pkg_name):
	try:
		subs = collect_submodules(pkg_name)
		print(f'[INFO] Found {pkg_name} submodules: {subs}')
		return subs
	except Exception as e:
		print(f'[WARN] Could not collect {pkg_name} submodules: {e}')
		return []


serial_tools_hidden = safe_collect_submodules('serial.tools')
serial_asyncio_hidden = safe_collect_submodules('serial_asyncio')

# Merge all hidden imports
all_manual_hidden = manual_hidden + serial_tools_hidden + serial_asyncio_hidden


# === Helper functions ===
def read_poetry_dependencies(file_path='pyproject.toml'):
	with open(file_path, 'rb') as f:
		data = tomli.load(f)
	packages = []

	project_deps = data.get('project', {}).get('dependencies', [])

	if project_deps:
		for dep in project_deps:
			pkg = dep.split(' ', 1)[0].split('[', 1)[0]
			packages.append(pkg)

	else:
		poetry_deps = data.get('tool', {}).get('poetry', {}).get('dependencies', {})

		for pkg in poetry_deps.keys():
			if pkg.lower() == 'python':
				continue

			packages.append(pkg)

	print('\n[INFO] Packages found:')
	for pkg in packages:
		print(f'  - {pkg}')

	return packages


def collect_all_from_packages(packages):
	datas, binaries, hiddenimports = [], [], []
	for pkg in packages:
		try:
			d, b, h = collect_all(pkg)
			datas += d
			binaries += b
			hiddenimports += h
		except Exception as e:
			print(f"[WARN] Failed to collect '{pkg}': {e}")
			exit()
	return datas, binaries, hiddenimports


# === Read packages from pyproject.toml ===
packages = read_poetry_dependencies()
datas, binaries, hiddenimports = collect_all_from_packages(packages)


# === Add extra folders as data (cross-platform) ===
extra_data = []
for folder in EXTRA_FOLDERS:
	os.makedirs(folder, exist_ok=True)
	if os.path.exists(folder):
		if os.name == 'nt':
			# Windows: use ; as separator
			extra_data.append(f'{folder}{os.sep};{folder}')
		else:
			# Linux: use : as separator
			extra_data.append(f'{folder}{os.sep}:{folder}')


# === Run PyInstaller ===

# === Platform-specific options ===
opts = [
	ENTRY_SCRIPT,
	f'--name={APP_NAME}',
	'--onefile',
	f'--icon={icon_path}' if icon_path else '',
	f'--distpath={output_dir}',
	f'--workpath={work_dir}',
	'--noconfirm',
]
if os.name == 'nt':
	opts.append('--noconsole')

opts += [f'--hidden-import={h}' for h in hiddenimports + all_manual_hidden]
opts += [f'--add-data={d}' for d in extra_data]

PyInstaller.__main__.run(opts)


try:
	shutil.rmtree(work_dir)
	print(f'[INFO] Removed build directory: {work_dir}')
except Exception as e:
	print(f'[WARN] Could not remove build directory: {e}')
