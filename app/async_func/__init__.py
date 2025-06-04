import asyncio
import os
import importlib
import inspect
import sys
from app.core.path import get_path

async def create_tasks(modulo_dir):
    package_path = os.path.abspath(get_path(modulo_dir))
    sys.path.insert(0, os.path.dirname(package_path))  # garante que o Python ache o pacote
    package_name = os.path.basename(package_path)

    tasks = []

    for arquivo in os.listdir(modulo_dir):
        full_path = os.path.join(modulo_dir, arquivo)

        if arquivo == "__pycache__":
            continue

        if os.path.isdir(full_path) and not arquivo.startswith('.'):
            # Recurse and add tasks from subdirectories
            sub_tasks = await create_tasks(full_path)
            tasks.extend(sub_tasks)

        elif arquivo.endswith(".py") and arquivo != "__init__.py":
            nome_modulo = f"{package_name}.{arquivo[:-3]}"  # nome em notação de ponto
            modulo = importlib.import_module(nome_modulo)

            for nome, func in inspect.getmembers(modulo, inspect.iscoroutinefunction):
                if func.__module__ == modulo.__name__:
                    tasks.append(asyncio.create_task(func()))
                    print(f"✅ Adicionado {arquivo} - {nome}() -> tasks")

    return tasks