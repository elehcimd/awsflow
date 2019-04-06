import argparse
import json
from time import sleep

import boto3
from fabric.api import local, settings

from awsflow.config import AWS_DEFAULT_REGION, AWS_SSH_KEY_PATHNAME
from awsflow.helpers.instance import get_public_master_dns_name
from awsflow.helpers.log import fatal
from awsflow.helpers.log import log_duration
from awsflow.helpers.log import logger
from awsflow.templates import clusterTemplates, stepTemplates, bootstrapTemplates
from awsflow.version import __version__

logging = logger.setup()

# Disable boto INFO logging, that is quite annoying
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)


# EMR client (resource interface doesnt exist):
# http://boto3.readthedocs.io/en/latest/reference/services/emr.html


def task_list_active(region_name):
    """
    Given a region, list active EMR clusters.
    :param region_name: name of the region. e.g., 'eu-central-1'
    :return:
    """

    emr = boto3.client('emr', region_name=region_name)

    logging.info('Listing active clusters in {} ...'.format(region_name))
    for cluster in emr.list_clusters()['Clusters']:
        if cluster['Status']['State'].startswith('TERMINATED'):
            continue
        logging.info('Cluster {} is active and in {} state'.format(cluster['Id'], cluster['Status']['State']))


def task_add_step(region_name, template, params, cluster_id):
    """
    Add step to existing EMR cluster
    :param region_name: region name
    :param template: step template name
    :param params: step template parameters
    :param cluster_id: EMR cluster id
    :return:
    """
    client = boto3.client('emr', region_name=region_name)

    t = stepTemplates.get(template, params)

    response = client.add_job_flow_steps(
        JobFlowId=cluster_id,
        Steps=[t]
    )
    logging.info('Added stepId {}'.format(response['StepIds'][0]))


def get_public_master_dns_name(region_name, cluster_id):
    """
    Given region name and cluster id, returns the public dns name for the master node
    :param region_name:
    :param cluster_id:
    :return:
    """
    client = boto3.client('emr', region_name=region_name)
    desc = client.describe_cluster(ClusterId=cluster_id)
    return (desc['Cluster']['MasterPublicDnsName'])


def task_ssh(region_name, cluster_id, cmd):
    """
    Given a region and a cluster id, open ssh shell
    :param region_name: name of the region. e.g., 'eu-central-1'
    :param cluster_id: id of the cluster. e.g., 'j-1W1939CQFFXDU'
    :param cmd: execute this remote command over SSH
    :return:
    """

    cmd_ssh = 'ssh -F /dev/null -o ConnectTimeout=5 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i {} hadoop@{} {}'
    local(cmd_ssh.format(AWS_SSH_KEY_PATHNAME, get_public_master_dns_name(region_name, cluster_id), cmd))


def task_tunnel(region_name, cluster_id):
    """
    Given a region and cluster id, create ssh tunnel for zeppelin...
    :param region_name: name of the region. e.g., 'eu-central-1'
    :param cluster_id: id of the cluster. e.g., 'j-1W1939CQFFXDU'
    :return:
    """

    cmd = 'ssh -F /dev/null -o ConnectTimeout=5 -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -i {} -ND 0.0.0.0:8157 hadoop@{}'

    while True:
        with settings(warn_only=True):
            local(cmd.format(AWS_SSH_KEY_PATHNAME, get_public_master_dns_name(region_name, cluster_id)))
            sleep(1)


def emr_wait_states(client, cluster_id, expected_states, sleep_seconds):
    """
    Wait until EMR cluster reaches desired state of terminates
    :param client: boto3 client handler
    :param cluster_id: EMR cluster id
    :param expected_states: wait until one of the states is reached
    :param sleep_seconds: check every `sleep_seconds` seconds
    :return:
    """
    while True:
        desc = client.describe_cluster(ClusterId=cluster_id)
        state = desc['Cluster']['Status']['State']
        logging.info("EMR Cluster {} state: {}".format(cluster_id, state))
        if state in expected_states + ['TERMINATED', 'TERMINATED_WITH_ERRORS']:
            return state
        sleep(sleep_seconds)


@log_duration
def task_terminate(region_name, cluster_id):
    """
    Terminate cluster
    :param region_name: region name
    :param cluster_id: EMR cluster id
    :return:
    """
    client = boto3.client('emr', region_name=region_name)
    client.terminate_job_flows(JobFlowIds=[cluster_id])

    logging.info('Terminating EMR Cluster {} ...'.format(cluster_id))
    emr_wait_states(client, cluster_id, ['TERMINATED'], 10)
    logging.info("EMR Cluster {} terminated!".format(cluster_id))


@log_duration
def task_create(region_name, template, params=[], wait=True, cluster_id=None):
    """
    Create EMR cluster
    :param region_name: region name
    :param template: EMR cluster template
    :param params: EMR cluster template parameters
    :param wait: wait until cluster created before returning
    :param cluster_id: keep monitoring this cluster id, skipp thele creation, until it becomes available
    :return:
    """

    client = boto3.client('emr', region_name=region_name)

    if cluster_id is None:
        t = clusterTemplates.get(template, params)

        response = client.run_job_flow(**t)
        logging.info("Using AWSFlow version {}".format(__version__))
        logging.info(
            'Creating EMR Cluster {} using template "{}" ...'.format(response['JobFlowId'], t['Name']))
        cluster_id = response['JobFlowId']

    if wait:
        state = emr_wait_states(client, cluster_id, ['WAITING', 'RUNNING'], 10)

        if state in ['WAITING', 'RUNNING']:

            public_master_dns_name = get_public_master_dns_name(region_name, cluster_id)

            logging.info("EMR Cluster {} up and running!".format(cluster_id))
            logging.info(
                'SSH into master..............: awsflow.emr ssh --region {} --id {}'.format(region_name, cluster_id))
            logging.info(
                'Start SSH tunnel to master...: awsflow.emr tunnel --region {} --id {}'.format(region_name, cluster_id))
            logging.info('URL Jupyter Lab..............: http://{}:8888/'.format(public_master_dns_name))
            logging.info('URL Zeppelin.................: http://{}:8890/'.format(public_master_dns_name))
            logging.info('URL Spark History Server.....: http://{}:18080/'.format(public_master_dns_name))
            logging.info('URL Hadoop Resource Manager..: http://{}:8088/'.format(public_master_dns_name))
            logging.info('URL HDFS Name Node at URL....: http://{}:50070/'.format(public_master_dns_name))
        else:
            logging.info("EMR Cluster {} terminated!".format(cluster_id))

    else:
        logging.info("EMR Cluster {} being created!".format(cluster_id))

    return cluster_id


def main():
    """
    Application entry point
    :return:
    """

    parser = argparse.ArgumentParser(description="AWS EMR admin tool v{}".format(__version__))
    parser.add_argument('task',
                        choices=['active', 'create', 'terminate', 'ssh', 'tunnel', 'step', 'render', 'templates'])
    parser.add_argument('--region', default=AWS_DEFAULT_REGION, help="region to consider")
    parser.add_argument('--cluster', help="name of cluster template")
    parser.add_argument('--step', help="add step to running cluster")
    parser.add_argument('--bootstrap', help="name of bootstrap template")
    parser.add_argument('--param', action='append', help="template parameter")
    parser.add_argument('--include', action='append', help="include Python script")
    parser.add_argument('--id', help="ID of EMR cluster")
    parser.add_argument('--cmd', default='', help="command to execute on master node")
    parser.add_argument('--tunnel', action='store_true', help="start tunnel once cluster running")

    args = parser.parse_args()

    if args.include:
        for pathname in args.include:
            logging.info('Including {} ...'.format(pathname))
            exec(open(pathname).read(), globals())

    try:

        if args.task == 'active':
            task_list_active(region_name=args.region)

        elif args.task == 'create':

            if args.cluster is None and args.id is None:
                fatal("create task requires --cluster or --id")

            cluster_id = task_create(region_name=args.region, template=args.cluster, params=args.param,
                                     cluster_id=args.id)
            if args.tunnel:
                # if --tunnel, start tunnel afterwards
                task_tunnel(region_name=args.region, cluster_id=cluster_id)

        elif args.task == 'terminate':
            task_terminate(region_name=args.region, cluster_id=args.id)

        elif args.task == 'ssh':
            task_ssh(region_name=args.region, cluster_id=args.id, cmd=args.cmd)

        elif args.task == 'tunnel':
            task_tunnel(region_name=args.region, cluster_id=args.id)

        elif args.task == 'step':
            task_add_step(region_name=args.region, template=args.step, params=args.param, cluster_id=args.id)

        elif args.task == 'render':
            if args.cluster:
                t, n = clusterTemplates.get(args.cluster, args.param), "Cluster"
            elif args.bootstrap:
                t, n = bootstrapTemplates.get(args.bootstrap, args.param), "Bootstrap"
            elif args.step:
                t, n = stepTemplates.get(args.step, args.param), "Step"
            else:
                fatal("render task requires either --cluster, --bootstrap, or --step")
            logging.info('{n} template:\n\n{s}\n\n'.format(n=n, s=json.dumps(t, indent=4, sort_keys=True)))

        elif args.task == 'templates':
            logging.info('EMR cluster templates: {}'.format(clusterTemplates.get_names()))
            logging.info('EMR step templates: {}'.format(stepTemplates.get_names()))
            logging.info('EMR bootstrap templates: {}'.format(bootstrapTemplates.get_names()))

        else:
            fatal("Task not recognized")

    except KeyboardInterrupt:
        fatal("Interrupted")


if __name__ == "__main__":
    main()
