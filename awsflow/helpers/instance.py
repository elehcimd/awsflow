import json

import boto3


def is_master():
    """
    Returns true if executed on the AWS EMR master node
    :return:
    """
    with open('/mnt/var/lib/info/instance.json', 'r') as f:
        data = f.read()
        return json.loads(data)['isMaster']


def get_extraInstanceData():
    """
    Get info about the current EMR cluster as dict.
    E.g.: "region", "jobFlowId"

    :return: dict with all EMR cluster properties
    """
    with open('/mnt/var/lib/info/extraInstanceData.json', 'r') as f:
        data = f.read()
        return json.loads(data)


def get_region_name():
    """
    Return EMR cluster region as string
    :return:
    """
    return get_extraInstanceData()['region']


def get_cluster_id():
    """
    Return EMR cluster id as string
    :return:
    """
    return get_extraInstanceData()['jobFlowId']


def get_public_master_dns_name():
    """
    Return the EMR public master dns name
    :return:
    """
    region_name = get_region_name()
    cluster_id = get_cluster_id()

    client = boto3.client('emr', region_name=region_name)
    desc = client.describe_cluster(ClusterId=cluster_id)
    return desc['Cluster']['MasterPublicDnsName']
