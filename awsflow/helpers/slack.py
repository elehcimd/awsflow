from slackclient import SlackClient

from awsflow.config import SLACK_API_TOKEN, SLACK_BOTNAME, SLACK_CHANNEL


def post(message, api_token=SLACK_API_TOKEN, channel=SLACK_CHANNEL):
    """
    Post slack message
    :param message: message to post
    :param api_token: slack api token
    :param channel: channel to post to
    :return:
    """

    if not SLACK_CHANNEL:
        return

    sc = SlackClient(api_token)
    sc.api_call(
        "chat.postMessage",
        as_user=True,
        channel=channel,
        text=message,
        user=SLACK_BOTNAME
    )
