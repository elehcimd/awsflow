def config_step_task(name, task_name, task_params=[], on_failure='TERMINATE_CLUSTER'):
    """
    Returns a Python dict representing the step.

    :param name: semantic name of the task
    :param task_name: task name, identifies executable
    :param task_params: task parameters
    :param on_failure:  either "CONTINUE" or "TERMINATE_CLUSTER"
    :return:
    """
    return {
        'Name': name,
        'ActionOnFailure': on_failure,
        'HadoopJarStep': {
            'Jar': 'command-runner.jar',
            'Args': ['/usr/local/bin/{task_name}'.format(task_name=task_name)] + task_params
        }
    }
