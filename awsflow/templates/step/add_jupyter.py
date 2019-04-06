from awsflow.templates.step import config_step_task

# add Jupyter with S3 persistence
CONFIG_STEP_JUPYTER = config_step_task(name='install-jupyter-s3', task_name='awsflow.add.jupyter',
                                       task_params=['--bucket', '{s3bucket}', '--prefix', '{s3prefix}/jupyter'])

# add Jupyter without S3 notebook persistence
CONFIG_STEP_JUPYTER_LOCAL = config_step_task(name='install-jupyter-local', task_name='awsflow.add.jupyter')
