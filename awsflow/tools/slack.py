import argparse

from awsflow.helpers.instance import get_cluster_id, get_region_name, is_master
from awsflow.helpers.log import logger
from awsflow.helpers.slack import post

logging = logger.setup()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--msg')
    parser.add_argument('--cluster-ready', action='store_true')
    parser.add_argument('--if-master', action='store_true')

    args = parser.parse_args()

    if args.if_master:
        if not is_master():
            logging.info('Not master! nothing to do')
            return
        else:
            logging.info('Installing Jupyter notebook on master node')

    if args.msg:
        post(args.msg)

    if args.cluster_ready:
        post("Cluster {} in {} ready!".format(get_cluster_id(), get_region_name()))


if __name__ == "__main__":
    main()
