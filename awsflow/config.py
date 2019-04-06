# awsflow package filename template
PKG_WHEEL_FNAME = "awsflow-{version}-py3-none-any.whl"

# AWS role used for Lambda functions
AWS_LAMBDA_ROLE = None

# SSH keyfile downloaded from AWS to ssh into the master node
AWS_SSH_KEY_PATHNAME = '~/.ssh/yourkeypair.pem'

# default AWS region
AWS_DEFAULT_REGION = 'eu-central-1'

# AWS S3 bucket, used to form the URI of the awsflow package
AWS_S3_BUCKET = "yours3bucket"

# AWS S3 prefix, used to form URI of the awsflow package
AWS_S3_PREFIX = "awsflow/pkg"

# base AWS S3 URI for awsflow packages
AWS_S3_BASE = "s3://{bucket}/{prefix}".format(bucket=AWS_S3_BUCKET, prefix=AWS_S3_PREFIX)

# URI of awsflow package
AWS_S3_PKG = "{aws_s3base}/{pkg_wheel_fname}".format(aws_s3base=AWS_S3_BASE, pkg_wheel_fname=PKG_WHEEL_FNAME)

# URI used to store logs
AWS_S3_LOG_URI = "s3n://{}/awsflow/logs/emr/".format(AWS_S3_BUCKET)

# AWS EC2 keyname
AWS_EC2_KEYNAME = "yourkeypair"

# timeout to complete lambda functions (in seconds)
AWS_LAMBDA_TIMEOUT = 20

# Limit of Megabytes to execute lambda functions
AWS_LAMBDA_MEMORYSIZE = 512

# Runtime environment to execute lambda functions
AWS_LAMBDA_RUNTIME = "python3.6"

# EMR security groups. Set them to None to disable them.
AWS_EMR_MANAGED_MASTER_SECURITY_GROUP = None
AWS_EMR_MANAGED_SLAVE_SECURITY_GROUP = None

# AWS EC2 subnet IDs. Set it to [] to disable it.
AWS_EC2_SUBNET_IDS = []

# default logging level
LOG_LEVEL = "INFO"

# Slack integration. It can be disabled setting SLACK_CHANNEL to None.
SLACK_CHANNEL = None
SLACK_BOTNAME = "awsflow"
SLACK_API_TOKEN = None
