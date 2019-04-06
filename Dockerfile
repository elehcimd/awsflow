# base Linux image similar to what you'll find on Amazon EC2 instances
FROM amazonlinux

MAINTAINER Michele Dallachiesa <michele.dallachiesa@gmail.com>

# install common upackages
RUN yum -y update && yum -y install openssh-clients git unzip vim

# install python3 interpreter and packages
RUN amazon-linux-extras install -y python3
RUN pip-3.6 install --upgrade pip
ADD requirements.txt /tmp/requirements.txt
RUN pip-3.6 install -r /tmp/requirements.txt

# add Fabric autocompletion (fab+[tab]+[tab])
ADD fab_autocompletion.sh /root/.bashrc

# set workdir and entrypoint
WORKDIR /shared/awsflow
ENTRYPOINT ["/usr/bin/python3"]
