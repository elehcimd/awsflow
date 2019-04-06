import argparse

from fabric.api import local

from awsflow.config import AWS_S3_PKG, PKG_WHEEL_FNAME
from awsflow.version import __version__


def update_pkg(version):
    """
    Install the specified version of the awsflow packge
    :param version:
    :return:
    """

    local("aws s3 cp {pkg} /tmp".format(pkg=AWS_S3_PKG.format(version=version)))
    local("sudo pip-3.6 uninstall -y awsflow")
    local("sudo pip-3.6 install /tmp/{pkg_wheel_fname}".format(
        pkg_wheel_fname=PKG_WHEEL_FNAME.format(version=version)))


def main():
    parser = argparse.ArgumentParser(description="Update the installed AWSFlow package")
    parser.add_argument('--version', default=__version__)

    args = parser.parse_args()

    update_pkg(args.version)


if __name__ == "__main__":
    main()
