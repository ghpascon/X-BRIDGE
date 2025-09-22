# To run with Poetry:
# poetry run python build_exe.py


import os
import PyInstaller.__main__
from PyInstaller.utils.hooks import collect_all, collect_submodules

# === USER CONFIGURATION ===
EXE_PATH = "C:/Users/DELL/Desktop/PYTHON_BUILDS"  # Base folder to store builds
ENTRY_SCRIPT = "main.py"  # Main script
APP_NAME = "main"  # Final executable name
EXTRA_FOLDERS = ["app"]  # Extra folders to include in the build

# === Define output folder ===
host_folder = os.path.basename(os.getcwd())  # name of the current working directory
output_dir = os.path.join(EXE_PATH, host_folder)

# Create folders if they don't exist
os.makedirs(output_dir, exist_ok=True)

# === Extra hidden imports ===
manual_hidden = [
    "uvicorn.config",
    "uvicorn.main",
    "uvicorn.loops.auto",
]


# === Collect submodules for serial and serial_asyncio ===
def safe_collect_submodules(pkg_name):
    try:
        subs = collect_submodules(pkg_name)
        print(f"[INFO] Found {pkg_name} submodules: {subs}")
        return subs
    except Exception as e:
        print(f"[WARN] Could not collect {pkg_name} submodules: {e}")
        return []


serial_tools_hidden = safe_collect_submodules("serial.tools")
serial_asyncio_hidden = safe_collect_submodules("serial_asyncio")

# Merge all hidden imports
all_manual_hidden = manual_hidden + serial_tools_hidden + serial_asyncio_hidden


# === Helper functions ===
def read_poetry_dependencies(file_path="pyproject.toml"):
    import tomli  # Python 3.11+

    with open(file_path, "rb") as f:
        data = tomli.load(f)
    deps = data.get("project", {}).get("dependencies", [])
    packages = []
    for dep in deps:
        # Remove extras and versions, keep only the package name
        pkg = dep.split(" ", 1)[0].split("[", 1)[0]
        packages.append(pkg)
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

# === Add extra folders as data ===
extra_data = [f"{folder}{os.sep};{folder}" for folder in EXTRA_FOLDERS if os.path.exists(folder)]


# === Run PyInstaller ===
PyInstaller.__main__.run(
    [
        ENTRY_SCRIPT,
        f"--name={APP_NAME}",
        "--onefile",
        "--noconsole",
        f"--distpath={output_dir}",          # Executable output
        f"--workpath={output_dir}/build",    # Build folder
    ]
    + [f"--hidden-import={h}" for h in hiddenimports + all_manual_hidden]
    + [f"--add-data={d}" for d in extra_data]
)

