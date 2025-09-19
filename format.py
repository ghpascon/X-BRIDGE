import asyncio
import os
import sys
from typing import List

POETRY = "poetry"
CONCURRENCY = int(os.environ.get("FORMAT_CONCURRENCY", "6"))
SHOW_TOOL_OUTPUT = True


def find_python_files(root_path: str) -> List[str]:
    """Recursively collect .py files from root_path."""
    python_files: List[str] = []
    for root, _, files in os.walk(root_path):
        for file_name in files:
            if file_name.endswith(".py"):
                full_path = os.path.join(root, file_name)
                python_files.append(full_path)
    return python_files


async def run_cmd(args: List[str], cwd: str) -> tuple[bool, str]:
    """Run a command asynchronously. Returns (success, combined_output)."""
    proc = await asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=cwd,
    )
    stdout_b, stderr_b = await proc.communicate()
    stdout = stdout_b.decode(errors="ignore").strip()
    stderr = stderr_b.decode(errors="ignore").strip()
    ok = proc.returncode == 0
    combined = "\n".join([s for s in (stdout, stderr) if s])
    return ok, combined


async def process_file(file_path: str, cwd: str, sem: asyncio.Semaphore) -> bool:
    """Run isort -> black -> flake8 sequentially for a single file inside a semaphore."""
    async with sem:
        print(f"\nRunning checks on: {file_path}")
        # isort
        ok, out = await run_cmd([POETRY, "run", "isort", file_path], cwd)
        if not ok:
            print(f"[isort FAIL] {file_path}\n{out}")
            return False
        elif SHOW_TOOL_OUTPUT and out:
            print(out)

        # black
        ok, out = await run_cmd([POETRY, "run", "black", file_path], cwd)
        if not ok:
            print(f"[black FAIL] {file_path}\n{out}")
            return False
        elif SHOW_TOOL_OUTPUT and out:
            print(out)

        # flake8
        ok, out = await run_cmd([POETRY, "run", "flake8", file_path], cwd)
        if not ok:
            print(f"[flake8 FAIL] {file_path}\n{out}")
            return False
        elif SHOW_TOOL_OUTPUT and out:
            print(out)

        return True


async def amain() -> int:
    repo_root = os.path.dirname(os.path.abspath(__file__))
    files = find_python_files(repo_root)

    if not files:
        print("No Python files found.")
        return 0

    sem = asyncio.Semaphore(CONCURRENCY)
    tasks = [asyncio.create_task(process_file(fp, repo_root, sem)) for fp in files]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    failures = 0
    for f, res in zip(files, results):
        if isinstance(res, Exception):
            failures += 1
            print(f"[ERROR] {f}: {res}")
        elif not res:
            failures += 1

    print(f"\nCompleted with {failures} failure(s) across {len(files)} file(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(amain())
    except KeyboardInterrupt:
        exit_code = 130
    sys.exit(exit_code)
