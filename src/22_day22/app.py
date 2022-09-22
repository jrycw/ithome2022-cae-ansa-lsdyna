import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import pandas as pd
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from env import MAX_CONCURRENT_LIMIT, ST_AUTO_REFRESH_INTERVAL
from helpers import (
    _create_task_id,
    convert_df,
    get_csv_filename,
    get_solver_dir,
    parse_dyna_folder,
    parse_task_cmd,
    tk_2_wsl2,
)
from mappings import (
    emogi_mapping,
    solver_precision_mapping,
    solver_type_mapping,
    solver_version_pool,
)
from schemas import Task, TaskStatus

# st-begins
st.set_page_config('stem (WSL2 local)',  layout='wide')
st.header('stem (WSL2 local)')

# st-autorefresh
count = st_autorefresh(interval=ST_AUTO_REFRESH_INTERVAL,
                       key="awesomestemproject")

# st-cache
if 'tasks' not in st.session_state:
    st.session_state['tasks'] = []

if 'sentinel' not in st.session_state:
    st.session_state['sentinel'] = object()

if 'insertable_idx' not in st.session_state:
    st.session_state['insertable_idx'] = 0

# retrieve-cache


def get_tasks():
    return st.session_state.tasks


def get_sentinel():
    return st.session_state.sentinel


def get_insertable_idx():
    return st.session_state.insertable_idx


# config
# tk
# https://github.com/streamlit/streamlit/issues/1019
root = tk.Tk()
root.withdraw()
# Make folder picker dialog appear on top of other windows
root.wm_attributes('-topmost', 1)


# getters


def _get_task_attr(_attr):
    tasks = get_tasks()
    return [task.dict()[_attr] for task in tasks]


def get_task_ids():
    return _get_task_attr('id')


def get_task_statuses():
    return _get_task_attr('status')


def get_task_by_id(task_id: str):
    tasks = get_tasks()
    for task in tasks:
        if task.id == task_id:
            return task


def _get_task_ids_by_status(status):
    tasks = get_tasks()
    return [task.id
            for task in tasks
            if task.status == status]


def get_staging_task_ids():
    return _get_task_ids_by_status(TaskStatus.staging)


def _get_task_by_status(status):
    tasks = get_tasks()
    return [task
            for task in tasks
            if task.status == status]


def get_staging_tasks():
    return _get_task_by_status(TaskStatus.staging)


def get_ds(tasks):
    ds = []
    keys = ('id', 'solver', 'deck', 'cores',
            'memory', 'consoles', 'status', 'emogi')
    for task in tasks:
        values = (task.id,
                  *parse_task_cmd(task.cmd),
                  task.status,
                  emogi_mapping.get(task.status).decode('utf-8'))
        ds.append(dict(zip(keys, values)))
    return ds

# sync


def sync_task_cp_status():
    '''
    cp.poll() is None means alive
    returncode=0 means successful for subprocess
    '''
    tasks = get_tasks()
    sentinel = get_sentinel()
    for task in tasks:
        cp = task.cp
        if cp != sentinel:
            if cp.poll() is None:
                task.status = TaskStatus.running
            else:
                if cp.returncode == 0:
                    task.status = TaskStatus.finished
                else:
                    task.status = TaskStatus.notOK


def sync_insertable_idx():
    tasks = get_tasks()
    idx = 0
    for task in tasks:
        if task.status == TaskStatus.staging:
            break
        idx += 1
    st.session_state['insertable_idx'] = idx


def st_sync():
    sync_task_cp_status()
    sync_insertable_idx()


# task-operators
def create_task_id():
    task_ids = get_task_ids()
    while True:
        task_id = _create_task_id()
        if task_id not in task_ids:
            break
    return task_id


def add_task(solver, deck, ncpu, memory, consoles):
    task_id = create_task_id()
    task_cmd = ' '.join(
        [solver, deck, ncpu, memory, consoles])
    task_cp = get_sentinel()
    task_data = {'id': task_id,
                 'cmd': task_cmd,
                 'cp': task_cp}
    task = Task(**task_data)

    tasks = get_tasks()
    tasks.append(task)
    return task


def add_tasks(solver, ncpu, memory, consoles, glob_ckbox):
    decks = []
    if not glob_ckbox:
        kfile = filedialog.askopenfilename(
            master=root,
            filetypes=[('LS-DYNA file', '.key .k .i .dyn dynain .key.gz .k.gz .i.gz .dyn.gz')])
        if kfile:
            deck = f'i={tk_2_wsl2(kfile)}'
            decks = [deck]
    elif glob_ckbox:
        kfolder = filedialog.askdirectory(
            master=root)
        if kfolder:
            for kfile in Path(kfolder).glob('**/*k'):
                deck = f'i={tk_2_wsl2(kfile.as_posix())}'
                decks.append(deck)
    for deck in decks:
        add_task(solver, deck, ncpu, memory, consoles)


def run_task(task):
    dyna_folder = parse_dyna_folder(task.cmd)
    cp = subprocess.Popen(['wsl', '--cd', dyna_folder, '-e', *task.cmd.split()],
                          creationflags=subprocess.CREATE_NEW_CONSOLE)
    task.cp = cp


def remove_task(task):
    tasks = get_tasks()
    try:
        tasks.remove(task)
    except ValueError:
        pass


def move_task(move_id, target_idx):
    move_task = get_task_by_id(move_id)
    if move_task is not None:
        inserted_idx = target_idx-1
        be_inserted_task = tasks[inserted_idx]
        conds = (inserted_idx >= get_insertable_idx(),
                 move_id != be_inserted_task.id)
        if all(conds):
            tasks.remove(move_task)
            tasks.insert(inserted_idx, move_task)
        else:
            st.warning(f'Invalid operation.Nothing happened!')
    else:
        st.warning('No tasks can be moved now')


# main
st_sync()
tasks = get_tasks()

RUN = st.checkbox('RUN')
if RUN:
    len_run_statuses = sum(1 for status in get_task_statuses()
                           if status == TaskStatus.running)
    if len_run_statuses < MAX_CONCURRENT_LIMIT:
        for task in tasks:
            if task.status == TaskStatus.staging:
                run_task(task)
                break

ADD_TASKS = st.sidebar
with ADD_TASKS:
    ADD_TASKS_FORM = st.form("add-tasks-form")
    with ADD_TASKS_FORM:
        solver_version_ = st.selectbox(
            'LS-DYNA version', solver_version_pool)
        solver_type_ = solver_type_mapping.get(st.selectbox(
            'LS-DYNA solver type', solver_type_mapping.keys()))

        solver_precision_ = solver_precision_mapping.get(st.selectbox(
            'LS-DYNA solver precision', solver_precision_mapping.keys()))
        ncpu_ = st.slider('LS-DYNA cores', 1, 24, 2)
        memory_ = st.slider('Memory(Mb)', 200, 2000, 200, 100)
        consoles_ = st.multiselect('Consoles', ['d=nodump'], ['d=nodump'])
        solver_dir = get_solver_dir()
        solver_name = solver_type_ + '-dyna_' + solver_precision_

        solver = '/'.join([solver_dir,  solver_version_, solver_name])
        ncpu = f'ncpu={ncpu_}'
        memory = f'memory={memory_}m'
        consoles = ' '.join(consoles_) if consoles_ else ''
        glob_ckbox = st.checkbox('Get *.k recursively (same config)', True)
        add_tasks_button = st.form_submit_button('🔑 Add task(s)')
        if add_tasks_button:
            if not RUN:
                add_tasks(solver, ncpu, memory, consoles, glob_ckbox)
            else:
                st.warning('Please uncheck RUN button first')

README = st.expander('README')
with README:
    col_st_auto_fresh_interval, col_max_concurrent_limit, * \
        _ = st.columns((1, 1, 4))
    col_st_auto_fresh_interval.metric(
        'Auto-refresh interval', f'{ST_AUTO_REFRESH_INTERVAL} ms')
    col_max_concurrent_limit.metric(
        'Max concurrent limit', f'{MAX_CONCURRENT_LIMIT} tasks')
    st.markdown(
        'open powershell terminal and set up 3 environment variables.')
    st.code('''setx LSTC_LICENSE "network"''')
    st.code('''setx LSTC_LICENSE_SERVER "192.168.0.5"''')
    st.code('''setx WSLENV "LSTC_LICENSE/u:LSTC_LICENSE_SERVER/u"''')
    st.markdown(
        f'Uncheck **RUN** before add, remove, move tasks. If **RUN** is checked, stem will continuously wait for tasks.')


REFRESH = st.container()
with REFRESH:
    refresh_button = st.button('Refresh')
    if refresh_button:
        st_sync()


PERFORM_TASKS, DASHBOARD = st.columns((1, 3))
with PERFORM_TASKS:
    REMOVE_TASKS, REMOVE_TASKS_FORM = st.container(), st.form('remove-tasks-form')
    with REMOVE_TASKS:
        with REMOVE_TASKS_FORM:
            s_removed_task_ids = st.multiselect('Select tasks to be removed',
                                                get_staging_task_ids())
            removed_task_button = st.form_submit_button('Remove tasks')
            if removed_task_button:
                if not RUN:
                    s_removed_tasks = [get_task_by_id(s_remove_task_id)
                                       for s_remove_task_id in s_removed_task_ids]
                    if s_removed_tasks:
                        for s_removed_task in s_removed_tasks:
                            remove_task(s_removed_task)
                    else:
                        st.warning(f'Invalid operation.Nothing happened!')
                else:
                    st.warning('Please uncheck RUN button first')

    MOVE_TASK, MOVE_TASK_FORM = st.container(), st.form('move-task-form')
    with MOVE_TASK:
        with MOVE_TASK_FORM:
            move_id = st.selectbox('Move the selected task :',
                                   get_staging_task_ids())

            target_idx = st.number_input('To position :',
                                         1,
                                         len(get_tasks()))

            move_task_button = st.form_submit_button('Move task')
            if move_task_button:
                if not RUN:
                    if move_id and target_idx:
                        move_task(move_id, target_idx)
                    else:
                        st.warning('Invalid input')
                else:
                    st.warning('Please uncheck RUN button first')

with DASHBOARD:
    ds = get_ds(tasks)
    if ds:
        with st.empty():
            df = pd.DataFrame(ds, index=range(1, len(ds)+1))
            st.dataframe(df)
        st.download_button(label="Export to CSV",
                           data=convert_df(df),
                           file_name=get_csv_filename(),
                           mime='text/csv')
