from awsflow.config import AWS_S3_PKG, PKG_WHEEL_FNAME
from awsflow.templates.bootstrap import config_bootstrap_bash
from awsflow.version import __version__

COMMANDS = ["aws s3 cp {pkg} /tmp".format(pkg=AWS_S3_PKG.format(version=__version__)),
            "sudo pip-3.6 install /tmp/{pkg_wheel_fname}".format(
                pkg_wheel_fname=PKG_WHEEL_FNAME.format(version=__version__))]

CONFIG_BOOTSTRAP_AWSFLOW = config_bootstrap_bash('install-pkg-awsflow', COMMANDS)
