from awsflow.templates.step import config_step_task


def CONFIG_STEP_SLACK(params=[]):
    return config_step_task(name='slack-message', task_name='awsflow.slack', task_params=params)
