import argparse
import os

from fabric.api import local

from awsflow.helpers.instance import is_master, get_public_master_dns_name
from awsflow.helpers.log import logger

logging = logger.setup()


def main():
    parser = argparse.ArgumentParser(description="Install and start Jupyter Lab")
    parser.add_argument('--bucket')
    parser.add_argument('--prefix')

    args = parser.parse_args()

    if not is_master():
        logging.info('Not master! nothing to do')
        return
    else:
        logging.info('Installing Jupyter notebook on master node')

    # change current directory, same that will be available in the shell from jupyter lab
    os.chdir("/home/hadoop/")

    # install required packages.
    # toolz and dask are reported as missing at startup of jupyterlab, so including them here.
    local("sudo pip-3.6 install jupyterlab==0.35.4 s3contents==0.1.12 toolz==0.9.0 dask==1.1.1")

    # configure jupyter notebook

    # ammissible configration options:
    # http://jupyter-notebook.readthedocs.io/en/stable/config.html
    jupyter_config = [
        'from s3contents import S3ContentsManager',
        'c = get_config()',
        'c.NotebookApp.open_browser = False',
        'c.NotebookApp.allow_root = True',
        'c.NotebookApp.token = ""',
        'c.NotebookApp.terminado_settings = {"shell_command": ["/bin/bash"]}',
        'c.NotebookApp.ip = "{dns_name}"'.format(dns_name=get_public_master_dns_name()), ]

    if args.bucket and args.prefix:
        jupyter_config += [
            'c.NotebookApp.contents_manager_class = "s3contents.S3ContentsManager"',
            'c.S3ContentsManager.bucket = "{}"'.format(args.bucket),
            'c.S3ContentsManager.prefix = "{}"'.format(args.prefix)
        ]

    local('mkdir -p /home/hadoop/.jupyter')

    with open('/home/hadoop/.jupyter/jupyter_notebook_config.py', 'w') as f:
        data = '\n'.join(jupyter_config) + '\n'
        f.write(data)

    # set startup Python script, executed before first cell of all notebooks
    jupyter_startup = [
        'import os',
        'import sys',
        'os.environ["PYSPARK_PYTHON"] = "python36"',
        'sys.path = ["/usr/lib/spark/python/", "/usr/lib/spark/python/lib/py4j-0.10.7-src.zip"] + sys.path'
    ]

    local('mkdir -p /home/hadoop/.ipython/profile_default/startup')

    with open('/home/hadoop/.ipython/profile_default/startup/00-first.py', 'w') as f:
        data = '\n'.join(jupyter_startup) + '\n'
        f.write(data)

    # kill existing running instances
    local("kill $(pgrep jupyter-lab) 2>/dev/null || echo")

    # start jupyter notebook in background, as 'hadoop' user. console output to logfile.
    local('nohup bash -c "/usr/local/bin/jupyter-lab 2>&1 | tee -ia /home/hadoop/jupyterlab.log" &')


if __name__ == "__main__":
    main()
