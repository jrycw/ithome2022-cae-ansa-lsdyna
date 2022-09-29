import subprocess
from pathlib import Path

from env import ANSAPATH


def run():
    api_file = (Path(__file__).parent / 'api.py').as_posix()
    cmd = []
    cmd.append(Path(ANSAPATH).as_posix())
    cmd.append('-nogui')
    cmd.append('-exec')
    cmd.append(f'"load_script: {api_file}"')
    cmd = ' '.join(str(entry) for entry in cmd)
    cp = subprocess.Popen(cmd, stdin=subprocess.PIPE, shell=True)
    print(f'{cp=}')


if __name__ == '__main__':
    run()
