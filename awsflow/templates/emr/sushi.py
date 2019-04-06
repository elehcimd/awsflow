from awsflow.config import AWS_S3_LOG_URI, AWS_EC2_KEYNAME, AWS_EMR_MANAGED_MASTER_SECURITY_GROUP, \
    AWS_EMR_MANAGED_SLAVE_SECURITY_GROUP, AWS_EC2_SUBNET_IDS
from awsflow.templates.bootstrap.add_awsflow import CONFIG_BOOTSTRAP_AWSFLOW
from awsflow.templates.step.add_jupyter import CONFIG_STEP_JUPYTER
from awsflow.templates.step.slack import CONFIG_STEP_SLACK
from awsflow.version import __version__ as version

# Available instance types for EMR clusters:
# https://aws.amazon.com/emr/pricing/
EC2_INSTANCE_TYPE = "r4.2xlarge"

# At least 1 EMR cores required
EC2_CORES_COUNT = 8

# This works decently in the eu-central-1 zone, might get cheaper/more expensive in other data centers
EC2_BID_PRICE = 0.31

CONFIG_EMR_SUSHI = {

    'Name': 'sushi',

    'LogUri': AWS_S3_LOG_URI,
    'ReleaseLabel': 'emr-5.21.0',
    'Instances': {
        "InstanceFleets": [
            {
                "Name": "Master",
                "InstanceFleetType": "MASTER",
                "TargetOnDemandCapacity": 1,
                "InstanceTypeConfigs": [
                    {
                        "InstanceType": EC2_INSTANCE_TYPE,
                        "EbsConfiguration": {
                            "EbsBlockDeviceConfigs": [
                                {
                                    "VolumeSpecification": {
                                        "VolumeType": "gp2",
                                        "SizeInGB": 100,
                                    },
                                    "VolumesPerInstance": 1,
                                }
                            ]
                        },
                    }
                ],
            },
            {
                "Name": "Core",
                "InstanceFleetType": "CORE",
                "TargetSpotCapacity": EC2_CORES_COUNT,
                "InstanceTypeConfigs": [
                    {
                        "InstanceType": EC2_INSTANCE_TYPE,
                        "EbsConfiguration": {
                            "EbsBlockDeviceConfigs": [
                                {
                                    "VolumeSpecification": {
                                        "VolumeType": "gp2",
                                        "SizeInGB": 100,
                                    },
                                    "VolumesPerInstance": 1,
                                }
                            ]
                        },
                    }
                ],
                "LaunchSpecifications": {
                    "SpotSpecification": {
                        "TimeoutDurationMinutes": 60,
                        "TimeoutAction": "SWITCH_TO_ON_DEMAND",
                    }
                },
            },
        ],
        "Ec2KeyName": AWS_EC2_KEYNAME,
        'KeepJobFlowAliveWhenNoSteps': True,
        'TerminationProtected': False
    },

    'BootstrapActions': [
        CONFIG_BOOTSTRAP_AWSFLOW,
    ],

    'Applications': [{'Name': 'Ganglia'}, {'Name': 'Hadoop'}, {'Name': 'Spark'}, {'Name': 'Zeppelin'}],

    'Steps': [
        CONFIG_STEP_JUPYTER,
        CONFIG_STEP_SLACK(['--if-master', '--cluster-ready'])
    ],

    'Configurations': [
        {
            "Classification": "spark-env",
            "Properties": {},
            "Configurations": [
                {
                    "Classification": "export",
                    "Properties": {
                        "PYSPARK_PYTHON": "python36",
                    },
                    "Configurations": []
                }
            ]
        },

        {
            "Classification": "zeppelin-env",
            "Properties": {},
            "Configurations": [
                {
                    "Classification": "export",
                    "Properties": {
                        "ZEPPELIN_NOTEBOOK_S3_BUCKET": "{s3bucket}",
                        "ZEPPELIN_NOTEBOOK_S3_USER": "{s3prefix}/zeppelin",
                        "ZEPPELIN_NOTEBOOK_STORAGE": "org.apache.zeppelin.notebook.repo.S3NotebookRepo",

                    },
                    "Configurations": []
                }
            ]
        },

        {
            "Classification": "spark-defaults",
            "Properties": {
                "spark.serializer": "org.apache.spark.serializer.KryoSerializer",
            }
        },
        {
            "Classification": "spark",
            "Properties": {
                "maximizeResourceAllocation": "true",

            }
        },

    ],

    "ServiceRole": "EMR_DefaultRole",
    "JobFlowRole": "EMR_EC2_DefaultRole",
    "VisibleToAllUsers": True,
    "Tags": [{"Key": "awsflow", "Value": str(version)}],
    "ScaleDownBehavior": "TERMINATE_AT_TASK_COMPLETION",
    "EbsRootVolumeSize": 10,

}

# Optional conf to handle EMR security groups and EC2 subnet IDs
if AWS_EMR_MANAGED_MASTER_SECURITY_GROUP:
    CONFIG_EMR_SUSHI["Instances"]["EmrManagedMasterSecurityGroup"] = AWS_EMR_MANAGED_MASTER_SECURITY_GROUP
if AWS_EMR_MANAGED_SLAVE_SECURITY_GROUP:
    CONFIG_EMR_SUSHI["Instances"]["EmrManagedSlaveSecurityGroup"] = AWS_EMR_MANAGED_SLAVE_SECURITY_GROUP
if AWS_EC2_SUBNET_IDS:
    CONFIG_EMR_SUSHI["Instances"]["Ec2SubnetIds"] = AWS_EC2_SUBNET_IDS
