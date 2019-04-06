import argparse
import os

from fabric.api import local


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--src-s3')

    args = parser.parse_args()

    if args.src_s3:
        fname = os.path.split(args.src_s3)[1]
        local("aws s3 cp {} /tmp/{}".format(args.src_s3, fname))
        local("sudo pip-3.6 install /tmp/{}".format(fname))


if __name__ == "__main__":
    main()
