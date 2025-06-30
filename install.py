import subprocess
from shutil import which


def install() -> None:
	subprocess.run([ which('pip'), 'install', '-r', 'requirements.txt', '-q' ])
