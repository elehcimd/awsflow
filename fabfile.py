import importlib
import os
import sys
import time

import fabric
from fabric.api import local
from fabric.decorators import task

# make sure that we import the awsflow package from this directory
sys.path = ["."] + sys.path
from awsflow.config import AWS_S3_BASE, PKG_WHEEL_FNAME
from config import TCP_PORT_PROXY

# disable "Done." output
fabric.state.output.status = False

# Initialise project directory and name
project_dir = os.path.abspath(os.path.dirname(__file__))
project_name = os.path.basename(project_dir)

# Change directory to directory containing this script
os.chdir(project_dir)


def get_version():
    """
    Get version of awsflow
    :return:
    """

    return sys.modules[project_name].version.__version__


def inc_version():
    """
    Increment micro release version (in 'major.minor.micro') in version.py and re-import it.
    Major and minor versions must be incremented manually in  version.py.
    """

    importlib.import_module(project_name + ".version")

    current_version = get_version()

    values = list(map(lambda x: int(x), current_version.split('.')))
    values[2] += 1

    new_version = '{}.{}.{}'.format(values[0], values[1], values[2])

    with open('version.py', 'w') as f:
        f.write('__version__ = "{}"\n'.format(new_version))
    with open('{project_name}/version.py'.format(project_name=project_name), 'w') as f:
        f.write('__version__ = "{}"\n'.format(new_version))

    sys.modules[project_name].version.__version__ = new_version

    print('Increased minor version: {} => {}'.format(current_version, new_version))


def timeit(f):
    """
    Log execution time of function
    :param f: function
    :return: none
    """

    def timed(*args, **kw):
        """
        Measure execution time for function
        """
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()

        print('[elapsed_time={}s]'.format(int(te - ts)))
        return result

    return timed


@task
def test(params=''):
    """
    Run all tests.
    :param params: parameters to py.test
    :return:
    """
    local('py.test {}'.format(params))


@task
def test_sx(params=''):
    """
    Run all tests printing output and terminating tests at first failure.
    :param params: parameters to py.test
    :return:
    """
    local('py.test -sx {}'.format(params))


@task
def test_pep8():
    """
    Run only pep8 test
    :return:
    """
    local('py.test {project_name}/tests/test_pep8.py'.format(project_name=project_name))


@task
def fix_pep8():
    """
    Fix a few common and easy PEP8 mistakes
    :return:
    """
    local('autopep8 --select E251,E303,W293,W291,W391 --aggressive --in-place --recursive {project_name}'.format(
        project_name=project_name))


def docker_exec(cmdline):
    """
    Execute command in running docker container
    :param cmdline: command to be executed
    """
    local('docker exec -ti {project_name} {cmdline}'.format(cmdline=cmdline, project_name=project_name))


@task
def build(options=''):
    """
    Build docker image
    """
    local('docker build {options} -t {project_name} .'.format(options=options, project_name=project_name))


@task
def start():
    """
    Start docker container
    """

    kill()
    local(
        'docker run --rm --name {project_name} -p {tcp_port_proxy}:8157 -d -ti -v {project_dir}:/shared/awsflow -v ~/.aws:/root/.aws -v ~/.ssh:/root/.ssh -t {project_name}'.format(
            project_dir=project_dir, project_name=project_name, tcp_port_proxy=TCP_PORT_PROXY))

    # Install package in develop mode: the code in /code is mapped to the installed package.
    docker_exec('python3 setup.py develop')


@task
def kill():
    """
    Stop docker container
    """
    local('docker kill {project_name} 2>/dev/null || true'.format(project_name=project_name))


@task
def shell():
    """
    Execute command in docker container
    """
    docker_exec('/bin/bash')


@task
def pkg_build():
    """
    Build Python package in dist/ directory
    :return:
    """

    clean()
    inc_version()
    local('python3 setup.py sdist bdist_wheel')


@task
def pkg_deploy(host=None):
    """
    Deploy package to AWS S3
    :return:
    """

    pkg_build()
    local('aws s3 cp dist/{pkg_wheel_fname} {aws_s3base}/'.format(pkg_wheel_fname=PKG_WHEEL_FNAME,
                                                                  aws_s3base=AWS_S3_BASE).format(version=get_version()))

    print("Operation completed: {project_name} {version} deployed!".format(project_name=project_name,
                                                                           version=get_version()))


@task
def clean():
    """
    Rempove temporary files
    """
    local('rm -rf .cache .eggs *.egg-info build dist .pytest_cache $(find . | grep __pycache__)')
