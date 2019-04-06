import sys

from setuptools import setup, find_packages

# make sure that we import the awsflow package from this directory
sys.path = ["."] + sys.path

from version import __version__

with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = list(filter(None, [x.strip() for x in f.readlines()]))

setup(
    name='awsflow',
    version=__version__,
    author='Michele Dallachiesa',
    author_email='michele.dallachiesa@gmail.com',
    packages=find_packages(),
    scripts=[],
    url='https://github.com/elehcimd/awsflow',
    description='AWSFlow: Gluing Amazon EMR and Lambda with Python',
    python_requires=">=3.6",
    install_requires=requirements,
    classifiers=[],
    entry_points={
        'console_scripts': [
            'awsflow.emr = awsflow.tools.emr:main',
            'awsflow.lambda = awsflow.tools.lambda:main',
            'awsflow.update = awsflow.tools.update_awsflow:main',
            'awsflow.add.jupyter = awsflow.tools.add_jupyter:main',
            'awsflow.add.pkg = awsflow.tools.add_pkg:main',
            'awsflow.slack = awsflow.tools.slack:main'
        ]
    },
)
