import subprocess

subprocess.run(["alembic", "upgrade", "head"], check=True)
