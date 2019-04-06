def config_bootstrap_task(name, task_name='mytask', task_params=[]):
    """
    Generate bootstrap block that executes an awsflow task
    :param name: name of bootstrap
    :param task_name: name of the executable
    :param task_params: parameters of task
    :return: dict defining the boostrap task
    """
    return {
        'Name': name,
        'ScriptBootstrapAction': {
            'Path': 'file:///usr/local/bin/{}'.format(task_name),
            'Args': task_params
        }
    }


def config_bootstrap_bash(name, commands):
    """
    Generate bootstrap block that executes a bash script defined by a set of commands, joined together
    :param name: name of bootstrap action
    :param commands: commands to chain together
    :return:
    """
    return {
        'Name': name,
        'ScriptBootstrapAction': {
            'Path': 'file:///bin/bash',
            'Args': ['-c', ' && '.join(commands)]
        }
    }
