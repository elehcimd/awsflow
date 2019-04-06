from awsflow.templates.step import config_step_task

CONFIG_STEP_UPDATE_AWSFLOW = config_step_task(name='update-awsflow', task_name='awsflow.update',
                                              task_params=['--version', '{version}'])
