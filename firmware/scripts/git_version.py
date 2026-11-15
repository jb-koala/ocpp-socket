"""Inyecta el hash de commit en el build para que la placa lo imprima al bootear (etapa 8)."""
import subprocess

Import("env")  # noqa: F821


def git(*args):
    try:
        return subprocess.check_output(["git", *args], stderr=subprocess.DEVNULL).decode().strip()
    except Exception:
        return "unknown"


commit = git("rev-parse", "--short=12", "HEAD")
dirty = "-dirty" if git("status", "--porcelain") else ""
env.Append(CPPDEFINES=[("GIT_COMMIT", env.StringifyMacro(commit + dirty))])
