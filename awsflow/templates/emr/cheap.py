from awsflow.config import AWS_S3_LOG_URI, AWS_EC2_KEYNAME
from awsflow.templates.bootstrap.add_awsflow import CONFIG_BOOTSTRAP_AWSFLOW
from awsflow.version import __version__ as version

# Available instance types for EMR clusters:
# https://aws.amazon.com/emr/pricing/
EC2_INSTANCE_TYPE = "m4.large"

# At least 1 EMR cores required
EC2_CORES_COUNT = 1

# This works decently in the eu-central-1 zone, might get cheaper/more expensive in other data centers
EC2_BID_PRICE = 0.1

CONFIG_EMR_CHEAP = {

    'Name': 'cheap',

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

    'Steps': [],

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
