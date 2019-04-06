# EMR bootstrap templates
from awsflow.helpers.templates import Templates
from awsflow.templates.bootstrap.add_awsflow import CONFIG_BOOTSTRAP_AWSFLOW

# EMR cluster templates
from awsflow.templates.emr.sushi import CONFIG_EMR_SUSHI
from awsflow.templates.emr.cheap import CONFIG_EMR_CHEAP

# EMR step templates
from awsflow.templates.step.add_jupyter import CONFIG_STEP_JUPYTER, CONFIG_STEP_JUPYTER_LOCAL
from awsflow.templates.step.slack import CONFIG_STEP_SLACK
from awsflow.templates.step.update_awsflow import CONFIG_STEP_UPDATE_AWSFLOW

# Register EMR cluster templates in global registry:
clusterTemplates = Templates()
clusterTemplates.register(CONFIG_EMR_SUSHI)
clusterTemplates.register(CONFIG_EMR_CHEAP)

# Register EMR step templates in global registry:
stepTemplates = Templates()
stepTemplates.register(CONFIG_STEP_JUPYTER)
stepTemplates.register(CONFIG_STEP_JUPYTER_LOCAL)
stepTemplates.register(CONFIG_STEP_SLACK())
stepTemplates.register(CONFIG_STEP_UPDATE_AWSFLOW)

# Register EMR bootstrap templates in global registry:
bootstrapTemplates = Templates()
bootstrapTemplates.register(CONFIG_BOOTSTRAP_AWSFLOW)
