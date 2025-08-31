import os

import PyInstaller.__main__
from PyInstaller.utils.hooks import collect_all, collect_submodules

# === CONFIGURAÇÕES DO USUÁRIO ===
ENTRY_SCRIPT = "main.py"  # Script principal
APP_NAME = "main"  # Nome do executável final
EXTRA_FOLDERS = ["app"]  # Pastas adicionais para incluir no build

# === Hidden imports adicionais ===
manual_hidden = [
    "uvicorn.config",
    "uvicorn.main",
    "uvicorn.loops.auto",
]


# === Coleta submódulos do serial e serial_asyncio ===
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

# Unifica todos os hidden imports
all_manual_hidden = manual_hidden + serial_tools_hidden + serial_asyncio_hidden


# === Funções auxiliares ===
def read_poetry_dependencies(file_path="pyproject.toml"):
    import tomli  # Python 3.11+

    with open(file_path, "rb") as f:
        data = tomli.load(f)
    deps = data.get("project", {}).get("dependencies", [])
    packages = []
    for dep in deps:
        # Remove extras e versões, pega só o nome do pacote
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
            print(f"[WARN] Falha ao coletar '{pkg}': {e}")
            exit()
    return datas, binaries, hiddenimports


# === Lê pacotes do pyproject.toml ===
packages = read_poetry_dependencies()
datas, binaries, hiddenimports = collect_all_from_packages(packages)

# === Adiciona pastas extras como dados ===
extra_data = [f"{folder}{os.sep};{folder}" for folder in EXTRA_FOLDERS if os.path.exists(folder)]

# === Executa o PyInstaller ===
PyInstaller.__main__.run(
    [ENTRY_SCRIPT, f"--name={APP_NAME}", "--onefile", "--console"]
    + [f"--hidden-import={h}" for h in hiddenimports + all_manual_hidden]
    + [f"--add-data={d}" for d in extra_data]
)

# Para rodar com Poetry:
# poetry run python build_exe.py
