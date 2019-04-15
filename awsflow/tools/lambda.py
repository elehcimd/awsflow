import argparse
import os
from shutil import make_archive
from tempfile import mkdtemp

import boto3
from fabric.api import local

from awsflow.config import AWS_DEFAULT_REGION, AWS_ROLE, AWS_LAMBDA_MEMORYSIZE, AWS_LAMBDA_TIMEOUT, \
    AWS_LAMBDA_RUNTIME
from awsflow.helpers.log import logger, fatal
from awsflow.version import __version__

logging = logger.setup()

# Disable boto INFO logging, that is quite annoying
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)


# Lambda client
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/lambda.html


def task_list():
    cli = boto3.client('lambda')
    funcs = cli.list_functions()
    logging.info("Lambda functions:")
    for func in funcs["Functions"]:
        logging.info("{CodeSize}\t{LastModified}\t{Runtime}\t{FunctionName}".format(**func))


def build_archive(mod, cache):
    """
    Build archive of lambda function
    :param mod: filename containing the lambda function
    :param cache: cache key, set it to None to disable cache
    :return: contents of ZIP archive
    """

    mod_pathname = os.path.abspath(os.path.dirname(__file__) + "/../lambdas/{}.py".format(mod))
    awsflow_basedir = os.path.abspath(os.path.dirname(__file__) + "/../../")

    pkg_dir_suffix = ".lambda"

    if cache:
        # Instead of generating a new temporary directory, reuse the existing one if existing,
        # so that we can avoid re-downloading all the dependencies again. this saves lots of time.
        # The cache is valid for any lamda function defined internally in the awsflow package.
        pkg_dir = "/tmp/awsflow{}-{}".format(pkg_dir_suffix, cache)

        # check if package directory is empty.
        pkg_dir_empty = not os.path.exists(pkg_dir)

        # make sure that the directory exists.
        local("mkdir -p {}".format(pkg_dir))
    else:
        pkg_dir = mkdtemp(pkg_dir_suffix)

    logging.info("Assembling archive for lambda function ...")

    local('cp {mod_pathname} {pkg_dir}'.format(mod_pathname=mod_pathname, pkg_dir=pkg_dir))

    if not cache or pkg_dir_empty:
        local('pip-3.6 install {awsflow_basedir} --find-links {awsflow_basedir} --target {pkg_dir} --upgrade'.format(
            awsflow_basedir=awsflow_basedir, pkg_dir=pkg_dir))
    else:
        logging.info("Using cached package directory")

    local('cp -r {awsflow_basedir}/awsflow {pkg_dir}'.format(awsflow_basedir=awsflow_basedir,
                                                             pkg_dir=pkg_dir))
    make_archive(base_name=pkg_dir, format='zip', root_dir=pkg_dir)

    logging.info("Archive ready.")

    archive_contents = open('{}.zip'.format(pkg_dir), "rb").read()

    if not cache:
        local("rm -rf {pkg_dir}.zip {pkg_dir}".format(pkg_dir=pkg_dir))

    return archive_contents


def task_delete(name):
    """
    Delete lambda function
    :param name: function name or ARN
    :return:
    """

    cli = boto3.client('lambda')

    try:
        cli.delete_function(FunctionName=name)
    except Exception as e:
        fatal("Operation failed: {}".format(e))

    logging.info("Operation completed.")


def task_create(mod, func, cache):
    """
    Build archive of lambda function, and deploy it
    :param modname: filename containing it
    :param funcname: name of function
    :param region: region where it should be created and deployed
    :return:
    """

    cli = boto3.client('lambda')

    archive_contents = build_archive(mod, cache)

    try:
        res = cli.create_function(Handler="{mod}.{func}".format(mod=mod, func=func),
                                  FunctionName=func,
                                  Runtime=AWS_LAMBDA_RUNTIME,
                                  Role=AWS_LAMBDA_ROLE,
                                  Code={"ZipFile": archive_contents},
                                  Timeout=AWS_LAMBDA_TIMEOUT,
                                  MemorySize=AWS_LAMBDA_MEMORYSIZE
                                  )
    except Exception as e:
        fatal("Operation failed: {}".format(e))

    logging.info("Operation completed: {}".format(res["FunctionArn"]))


def task_update(mod, func, cache):
    """
    Update existing lambda function
    :param modname: filename containing it
    :param funcname: name of function
    :param region: region where it should be created and deployed
    :param fast: if true, download all dependencies again from scratch
    :return:
    """

    cli = boto3.client('lambda')

    archive_contents = build_archive(mod, cache)

    try:
        res = cli.update_function_code(FunctionName=func,
                                       ZipFile=archive_contents)
    except Exception as e:
        fatal("Operation failed: {}".format(e))

    logging.info("Operation completed: {}".format(res["FunctionArn"]))


def main():
    """
    Application entry point
    :return:
    """

    parser = argparse.ArgumentParser(description="AWS Lambda admin tool v{}".format(__version__))
    parser.add_argument('task', choices=['list', 'create', 'update', 'delete'])
    parser.add_argument('--region', default=AWS_DEFAULT_REGION, help="region to consider")
    parser.add_argument('--include', action='append', help="include Python script")
    parser.add_argument('--mod', help="module name")
    parser.add_argument('--func', help="function name")
    parser.add_argument('--name', help="function to delete")
    parser.add_argument('--cache', help="cache key")

    args = parser.parse_args()

    if args.include:
        for pathname in args.include:
            logging.info('Including {} ...'.format(pathname))
            exec(open(pathname).read(), globals())

    elif args.task == 'list':
        task_list()

    elif args.task == 'create':

        if args.mod is None or args.func is None:
            fatal("create task requires --mod or --func")

        task_create(args.mod, args.func, args.cache)

    elif args.task == 'update':

        if args.mod is None or args.func is None:
            fatal("update task requires --mod or --func")

        task_update(args.mod, args.func, args.cache)

    elif args.task == 'delete':

        if args.name is None:
            fatal("delete task requires --name")

        task_delete(args.name)

    else:
        fatal("Task not recognized")


if __name__ == "__main__":
    main()
