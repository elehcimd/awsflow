from awsflow.tools.emr import logging
from awsflow.version import __version__


def hello_world(event, context):
    """
    Test function, does nothing
    :param event: AWS lambdas function event
    :param context: AWS lambdas function context
    :return:
    """

    message = 'event={} context={}'.format(event, context)
    logging.info('Hello World! Message is {}'.format(message))
    return {
        'parameters': message,
        'awsflow-version': __version__
    }
