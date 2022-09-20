import hashlib
import json
import ssl
import subprocess
import urllib.request
from pathlib import Path

from prefect import flow, task
from prefect.task_runners import SequentialTaskRunner
from prefect_shell import shell_run_command

from env import call_ansa_py, jfile, kfile, s3_url


@flow
def run_dyna():
    run_kfile = Path(kfile)
    dyna_dir_str = (run_kfile.parent).as_posix()
    solver = f'{Path.home()}/LS-DYNA/13.0/smp-dyna_s'
    i = run_kfile.as_posix()
    command = f'cd {dyna_dir_str};\
        {solver} i={i}  ncpu=8 memory=1024m d=nodump'
    return shell_run_command(command=command, return_all=True)


@task
def call_ansa(jfile):
    command = ['ansa',
               '-exec',
               f"load_script: '{call_ansa_py}'",
               '-exec',
               f"main('{jfile}')",
               '-nogui']
    return subprocess.run(command)


@flow(task_runner=SequentialTaskRunner())
def pull_to_trigger():
    ssl._create_default_https_context = ssl._create_unverified_context
    is_triggered, is_file = False, Path(jfile).is_file()
    with urllib.request.urlopen(s3_url) as resp:
        remote_config = resp.read()
    if is_file:
        with open(jfile, 'rb') as frb:
            remote_config_md5 = hashlib.md5(remote_config).hexdigest()
            local_config_md5 = hashlib.md5(frb.read()).hexdigest()
            is_triggered = remote_config_md5 != local_config_md5
    if not is_file or is_triggered:
        new_config = json.loads(remote_config.decode("utf-8"))
        with open(jfile, 'w') as fw:
            json.dump(new_config, fw)
        call_ansa(jfile)
        if Path(kfile).is_file():
            run_dyna()
