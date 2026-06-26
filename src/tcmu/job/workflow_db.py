import os
import platformdirs
from typing import List, Tuple, Dict
import tcmu
from filelock import FileLock


CACHEDIR = platformdirs.user_cache_dir(appname="tcmu", appauthor="TheoCheMVU", ensure_exists=True)
DBDIR = os.path.join(CACHEDIR, 'workflow_DBs')
os.makedirs(DBDIR, exist_ok=True)

@tcmu.cache
def make_path(workflow: str, active: bool = True, remote: bool = False, lock: bool = False):
    if remote:
        if active:
            return os.path.join('.cache', 'tcmu', workflow, 'active.csv')
        else:
            return os.path.join('.cache', 'tcmu', workflow, 'archive.csv')

    path = os.path.join(DBDIR, workflow)
    os.makedirs(path, exist_ok=True)
    if active:
        path = os.path.join(path, 'active.csv')
    else:
        path = os.path.join(path, 'archive.csv')

    if lock:
        path += '.lock'
        return FileLock(path)

    else:
        if not os.path.exists(path):
            with open(path, 'w+'):
                ...

        return path


#### BASIC FUNCTIONS

def archive(workflow: str, hsh: str):
    data = read(workflow, hsh)
    delete(workflow, hsh)
    write(workflow, hsh, active=False, **data)


def write(workflow: str, hsh: str, active: bool = True, **kwargs):
    s = f'{hsh}'
    for k, v in kwargs.items():
        s += f', {k}={v}'
    s += '\n'

    with make_path(workflow, active=active, lock=True):
        with open(make_path(workflow, active=active), 'a') as db:
            db.write(s)


def read(workflow: str, hsh: str, active: bool = True) -> dict:
    '''
    Get the status of a workflow with specific args and kwargs.
    '''
    # default status is unknown
    for _hsh, data in read_all(workflow, active=active).items():
        if hsh == _hsh:
            return data
    return {}


def parse_line(line: str) -> Tuple[str, dict]:
    '''
    Read information from a line from the database.
    '''
    # the hsh is always the first entry
    hsh = line.split(',')[0]
    data = {}
    # read anything after the hash
    for part in line.split(',')[1:]:
        parts = part.split('=')
        if len(parts) == 2:
            k, v = parts
            data[k.strip()] = v.strip()
        else:
            k = parts[0]
            v = None
            data[k.strip()] = None

    # return the hash and data separately
    return hsh, data


def read_all(workflow: str, active: bool = True) -> Dict[str, dict]:
    '''
    Return all lines that are in the database.
    '''
    with make_path(workflow, active=active, lock=True):
        with open(make_path(workflow, active=active)) as db:
            lines = db.readlines()

    # parse the lines we found
    parsed_lines = [parse_line(line) for line in lines]
    # and construct a dictionary
    return {hsh: data for hsh, data in parsed_lines}

def read_remote(workflow: str, server: tcmu.connect.Connection, active: bool = True) -> Dict[str, dict]:
    '''
    Return all lines that are in the database.
    '''
    file = server.download(make_path(workflow, remote=True, active=active), 'workflows.csv.remote')

    with open('workflows.csv.remote') as db:
        lines = db.readlines()

    # parse the lines we found
    parsed_lines = [parse_line(line) for line in lines]
    # and construct a dictionary
    return {hsh: data for hsh, data in parsed_lines}

def update(workflow: str, hsh: str, active: bool = True, **kwargs) -> None:
    '''
    Update a record in the database associated with the given hash.
    '''
    data = read(workflow, hsh, active=active)
    data.update(kwargs)
    delete(workflow, hsh, active=active)
    write(workflow, hsh, active=active, **data)


def delete(workflow: str, hsh: str, active: bool = True) -> None:
    '''
    Delete records related to the given hash.
    '''
    with make_path(workflow, active=active, lock=True):
        with open(make_path(workflow, active=active)) as db:
            lines = db.readlines()

    new_lines = [line for line in lines if line.split(',')[0] != hsh]

    with make_path(workflow, active=active, lock=True):
        with open(make_path(workflow, active=active), 'w+') as db:
            for line in new_lines:
                db.write(line)


# #### CONVENIENCE FUNCTIONS

def get_workflow_names() -> List[str]:
    return [name for name in os.listdir(DBDIR) if os.path.isdir(os.path.join(DBDIR, name))]


def get_status(workflow: str, hsh: str) -> str:
    '''
    Get the status of a workflow with specific args and kwargs.
    '''
    # check if it is active:
    active_status = read(workflow, hsh, active=True).get('status', None)
    if active_status is not None:
        return active_status

    return read(workflow, hsh, active=False).get('status', None)



def can_skip(workflow: str, hsh: str, active: bool = True, server: tcmu.connect.Server = tcmu.connect.Local()) -> bool:
    '''
    Checks if a workflow with specific args and kwargs has finished.
    '''
    status = get_status(workflow, hsh)
    # if the status indicates the workflow already ran we can skip
    if status in ['SUCCESS', 'FAILED']:
        return True

    # if the workflow is still running we need to check if it
    # is being managed by slurm
    elif status == 'RUNNING':
        data = read(workflow, hsh)
        # if the workflow is managed by slurm it should have a slurm-job-id
        slurm_job_id = data.get('slurm_job_id', None)
        # if it does not we can assume it failed
        if slurm_job_id is None:
             return False

        # if it does, we need to check if it is in the queue
        sq = tcmu.slurm.squeue(server=server)
        # if it is being managed by slurm we can skip it
        # otherwise something went wrong and the status was not updated
        return slurm_job_id in sq['id']

    return False


def set_status(workflow: str, hsh: str, new_status: str) -> None:
    '''
    Checks if a workflow with specific args and kwargs has finished.
    '''
    update(workflow, hsh, status=new_status)


def set_running(workflow: str, hsh: str) -> None:
    '''
    Checks if a workflow with specific args and kwargs has finished.
    '''
    update(workflow, hsh, status='RUNNING')


def set_finished(workflow: str, hsh: str) -> None:
    '''
    Checks if a workflow with specific args and kwargs has finished.
    '''
    update(workflow, hsh, status='SUCCESS')


def set_failed(workflow: str, hsh: str) -> None:
    '''
    Checks if a workflow with specific args and kwargs has finished.
    '''
    update(workflow, hsh, status='FAILED')


if __name__ == '__main__':
    write('Example', 'test', hello='world', active=False)
    write('Example', 'test', hello='world2', active=False)
    update('Example', 'test', hello='world120', active=False)
    print(read('Example', 'test', active=False))
