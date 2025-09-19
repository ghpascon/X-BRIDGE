import asyncio
import importlib
import inspect
import logging
import os
import sys

from app.core.path import get_path


async def create_tasks(module_dir):
    package_path = os.path.abspath(get_path(module_dir))
    sys.path.insert(0, os.path.dirname(package_path))  # Ensure Python can locate the package
    package_name = os.path.basename(package_path)

    tasks = []

    for file in os.listdir(module_dir):
        full_path = os.path.join(module_dir, file)

        if file == "__pycache__":
            continue

        if os.path.isdir(full_path) and not file.startswith("."):
            # Recursively add tasks from subdirectories
            sub_tasks = await create_tasks(full_path)
            tasks.extend(sub_tasks)

        elif file.endswith(".py") and file != "__init__.py":
            module_name = f"{package_name}.{file[:-3]}"  # Convert to dot notation
            module = importlib.import_module(module_name)

            # Add all coroutine functions defined in the module
            for name, func in inspect.getmembers(module, inspect.iscoroutinefunction):
                if func.__module__ == module.__name__:
                    tasks.append(asyncio.create_task(func()))
                    logging.info(f"✅ Added {file} - {name}() -> tasks")

    return tasks
