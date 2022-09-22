import getpass
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import streamlit as st


def get_disk_id(one_path):
    # ex: C => c
    return str(one_path)[0].lower()


def tk_2_wsl2(one_path, my_sep='/'):
    '''
    C:/Users/username/Desktop/LS_DYNA/airbag_deploy.k
    => /mnt/c/Users/username/Desktop/LS_DYNA/airbag_deploy.k
    '''
    disk_id = get_disk_id(one_path)
    return f'/mnt/{disk_id}/' + '/'.join(one_path.split(my_sep)[1:])


def parse_dyna_folder(cmd):
    _, i, *_ = cmd.split()
    return Path(i[2:]).parent.as_posix()  # ignore 'i=


def parse_task_cmd(task_cmd):
    solver_, deck_, ncpu, memory, *consoles = task_cmd.split()
    *_, solver_ver, solver_name = solver_.split('/')
    solver = '_'.join([solver_name[:3], solver_name[-1],  solver_ver])
    deck = '/'.join(deck_.split('/')[-2:])
    ncpu = ncpu.split('=')[-1]
    memory = memory.split('=')[-1]
    return solver, deck, ncpu, memory, consoles


def _create_task_id(n=8):
    return str(uuid4().hex)[:n]


@st.cache
def get_win_user():
    return getpass.getuser()


@st.cache
def get_solver_dir():
    '''
    C:\\Users\\username\\Desktop\\LS_DYNA\\program
    '''
    cwd = os.getcwd()
    disk_id = get_disk_id(cwd)
    win_user = get_win_user()
    return f'/mnt/{disk_id}/Users/{win_user}/Desktop/LS_DYNA/program'


@st.cache
def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8')


def get_csv_filename():
    return datetime.now().strftime('%Y%m%d_%H%M%S') + '.csv'
