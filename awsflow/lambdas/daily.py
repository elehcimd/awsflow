from datetime import datetime

from awsflow.config import AWS_DEFAULT_REGION
from awsflow.helpers.log import logger
from awsflow.helpers.slack import post as slack_post
from awsflow.tools.emr import task_create
from awsflow.version import __version__

logging = logger.setup()

# name of cluter template to use for daily Lambda function
EMR_CLUSTER_TEMPLATE_NAME = "cheap"


def start_emr(event, context):
    """
    Function creating daily an EMR cluster

    :param event: AWS lambda function event
    :param context: AWS lambda function context
    :return:
    """

    request_time = datetime.strptime(event['time'], "%Y-%m-%dT%H:%M:%SZ")

    cluster_id = task_create(region_name=AWS_DEFAULT_REGION,
                             template=EMR_CLUSTER_TEMPLATE_NAME,
                             params=[],
                             wait=False)

    msg = "Creating EMR cluster `{emr_cluster_template_name}`: request_time=`{request_time}` cluster_id=`{cluster_id}`".format(
        emr_cluster_template_name=EMR_CLUSTER_TEMPLATE_NAME, request_time=request_time, cluster_id=cluster_id)

    logging.info(msg)
    slack_post(msg)

    return {
        'request_time': str(request_time),
        'cluster_id': cluster_id,
        'awsflow-version': __version__
    }
