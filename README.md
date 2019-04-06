# AWSFlow: From zero to Amazon EMR jobs and Lambda functions with Python 

This package lets you define programmatically workloads for AWS Elastic Map Reduce (EMR) clusters and Lambda
functions using Python with a concise methodology aimed at fast prototyping.

It comes with a predefined set of templates for Amazon EMR clusters, steps, bootstrap actions, and Lambda functions,
including a few handy command line tools to manage them. Further, it gets installed everywhere to provide a unified command-line and programmatic interface: local Docker container, EMR cluster nodes, and context of Lambda functions. 

> We use `awsflow` to create clusters, run Jupyter/Zeppelin notebooks (persisted on S3), schedule the creation of clusters, and manage the execution of Spark jobs triggered by CloudWatch events.

## Usage

1. Fork this repository and clone it
2. Tune the config files
3. Build the package with Docker and deploy to S3
4. Manage lifecycle and deployment of EMR clusters and Lambda functions
5. Add templates and Lambda functions to implement your pipelines
6. Back to step 3.

The next sections will drive you through the setup of the project and some examples.

## System setup

1. Your operating system is MacOS/FreeBSD/Linux
2. Install Docker and Python3 (in the rest of the document, Python3 is assumed to be the default Python interpreter)
3. Install the Fabric package: `pip install Fabric3` 
4. Populate your `~/.aws` directory: [configuring Amazon cli credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
5. Copy your EMR SSH Key to `~/.ssh`: [accessing Amazon EMR master node with ssh](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-connect-master-node-ssh.html)
6. Fork this repository, make it private, and clone it

## Package configuration

The local configuration is located in `./config.py`. The value of `TCP_PORT_PROXY` is used as the TCP port on the Docker host and is mapped internally to handle SSH tunnels to the EMR master node. If you change it, you also need to adjust manually the TCP port in the file `foxyproxy-aws-emr.xml` file.

The configuration of the package is contained in `./awsflow/config.py` and gets shipped as part of the package.
Most of the parameters are optional. Mandatory parameters:

* `AWS_SSH_KEY_PATHNAME`: path to the SSH keyfile to access the EMR master node. This path is used inside the container and should refer to a file inside the  `~/.ssh` directory to be handled transparently
* `AWS_DEFAULT_REGION`: AWS region to use by default 
* `AWS_S3_BUCKET` and `AWS_S3_PREFIX`: S3 bucket name/prefix where logs and `àwsflow` builds are stored
* `AWS_EC2_KEYNAME`: The name of the Amazon EC2 key pair to access the EMR master node (user "hadoop")

To run the examples on Lambda functions, you should also set `AWS_LAMBDA_ROLE`: [Lambda execution role](https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html)

## Package builds and deployments

Builds and deployments are managed from a Docker container.
From the project directory, execute these three commands:

```
fab build # build Docker image
fab start # start Docker container
fab shell # open a Bash shell on Docker container
```

You should see a prompt `bash-4.2#`. This is a shell inside the container.
You can open more shells executing `fab shell` on other terminals.
To terminate the container, `fab kill` (this will terminate all container shells).
All other `fab` commands should be executed from the container shell(s). 
Let's build and deploy the package from the container shell:

```
fab pkg_build
fab pkg_deploy
```

The output reports the complete S3 upload path for clarity, altogether
with a final message `Operation completed: awsflow x.y.z deployed!` If you see it,
congratulations! you built and deployed the package to S3.

> If you want to be able to execute all `fab` commands also from the host,
execute the command `pip -r requirements.txt` on the host to install the dependencies.

## Listing active EMR clusters

Management of EMR clusters is provided by the `awsflow.emr` command line tool.
The first parameter is mandatory and identifies the desired task:

* `active`: list active clusters
* `create`: create cluster
* `terminate`: terminate cluster
* `ssh`: ssh into active cluster
* `tunnel`: activate tunnel to active cluster
* `step`: add step to active cluster
* `templates`: list available registered templates
* `render`: render templates

Example of usage listing all active clusters in the default region:

```
awsflow.emr active
```

Example of output:

```
bash-4.2# awsflow.emr active
2019-04-02 14:09:52,929 | INFO     | Listing active clusters in eu-central-1 ...
2019-04-02 14:09:53,072 | INFO     | Cluster j-ADSJK36XDDNR is active and in WAITING state
2019-04-02 14:09:53,072 | INFO     | Cluster j-FS5GOEIZGTBA is active and in WAITING state
2019-04-02 14:09:53,072 | INFO     | Cluster j-2U7FDX89BVIXT is active and in RUNNING state
2019-04-02 14:09:53,072 | INFO     | Cluster j-10A1JSO6AELXM is active and in RUNNING state
2019-04-02 14:09:53,072 | INFO     | Cluster j-2W6V4ZN24SE2G is active and in RUNNING state
[...]
```

A region different by the default can be specified with `--region`.

## Creating EMR clusters

To create a cluster using the `cheap` template (1 master and 1 core nodes using `m4.large` EC2 instances):

```
awsflow.emr create --cluster cheap
```

All EMR templates are defined in the `awsflow.templates.emr` subpackage.
You can review the definition of this template in `awsflow.templates.emr.cheap`.

The command does not return immediately, providing regular updates on the cluster creation:
 
```
bash-4.2# awsflow.emr create --cluster cheap
2019-04-02 14:20:45,863 | INFO     | Using AWSFlow version 0.0.80
2019-04-02 14:20:50,863 | INFO     | Creating EMR Cluster j-DFSJK36AXDNR using template "cheap" ...
2019-04-02 14:20:55,926 | INFO     | EMR Cluster j-DFSJK36AXDNR state: STARTING
[...]
```

Once the ready is ready, it prints some handy commands, URLs and statistics:

```
[...]
2019-04-02 14:23:49,476 | INFO     | EMR Cluster j-DFSJK36AXDNR up and running!
2019-04-02 14:23:49,476 | INFO     | SSH into master..............: awsflow.emr ssh --region eu-central-1 --id j-DDSJK36XXDNR
2019-04-02 14:23:49,476 | INFO     | Start SSH tunnel to master...: awsflow.emr tunnel --region eu-central-1 --id j-DDSJK36XXDNR
2019-04-02 14:23:49,476 | INFO     | URL Jupyter Lab..............: http://ec2-3-301-77-135.eu-central-1.compute.amazonaws.com:8888/
2019-04-02 14:23:49,477 | INFO     | URL Zeppelin.................: http://ec2-3-301-77-135.eu-central-1.compute.amazonaws.com:8890/
2019-04-02 14:23:49,477 | INFO     | URL Spark History Server.....: http://ec2-3-301-77-135.eu-central-1.compute.amazonaws.com:18080/
2019-04-02 14:23:49,477 | INFO     | URL Hadoop Resource Manager..: http://ec2-3-301-77-135.eu-central-1.compute.amazonaws.com:8088/
2019-04-02 14:23:49,477 | INFO     | URL HDFS Name Node at URL....: http://ec2-3-301-77-135.eu-central-1.compute.amazonaws.com:50070/
2019-04-02 14:23:49,479 | INFO     | Execution of task_create took 0.2933328999206424 seconds
bash-4.2#
```

Interrupting the script with `Ctrl-C` will not interrupt the creation of the cluster.
To restart receiving again updates for a specific cluster creation or to print again the commands and URLs if the cluster is ready, you can pass the EMR cluster ID with the `--id` parameter:

```
awsflow.emr create --id j-DFSJK36AXDNR
```

Cluster templates can have parameters that can be passed with repeated `--param key:value` options.

## Accessing web services on EMR master node

The web services running on the EMR master node are accessible only through an SSH tunnel to the master node. The entire manual process is documented in the EMR official instructions: [Access the Web Interfaces on the Master Node Using the Console](https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-connect-ui-console.html). 
 
The creation of the SSH tunnel is automated as follows:

```
awsflow.emr tunnel --id j-DDSJK36XXDNR
```

Connections to TCP port `TCP_PORT_PROXY` on the host are forwarded through an SSH tunnel on the EMR master node.
The setup and configuration of the web proxy are left to you. With FoxyProxy, you can use the `foxyproxy-aws-emr.xml` configuration file. If you changed the value of `TCP_PORT_PROXY`, you need to adjust the proxy port also in the XML config file.

Once the tunnel is up and running and the proxy is enabled in your browser, the URLs printed
at the end of the cluster creation become reachable. E.g., you can reach Zeppelin at the URL provided at the end of the cluster creation of from the AWS web console. Congratulations! You can now execute Spark jobs from your web browser using Zeppelin.
`
> Hint: the creation of the tunnel right after the creation of the cluster can be enabled with the `--tunnel` option with the `create` task. 

## Adding steps to a running EMR cluster

In the following example, we add a step to a running cluster installing Jupyter on the master node. 
There are two pre-defined steps to start jupyter: `install-jupyter-local` (notebooks in hadoop's home directory) and `install-jupyter-s3` (notebooks persisted on S3), both defined in `awsflow.templates.step.add_jupyter`.

Let's add the `install-jupyter-local` step to a running cluster: 

```
awsflow.emr step --step install-jupyter-local --id j-DFSJK36AXDNR
```

The step creation returns immediately. You can check the status of the step execution in the "Steps" tab on the EMR management dashboard. Once completed, you can access Jupyter from the Jupyter URL provided at the completion of the EMR creation.

The second template, `install-jupyter-s3`, is parametrised and its usage is discussed later in the templates section.

## Accessing the EMR master node with ssh

Example:

```
awsflow.emr ssh --id j-DFSJK36AXDNR
```

## Terminating an EMR cluster

Example:

```
awsflow.emr terminate --id j-DFSJK36AXDNR
```

## Managing templates

Templates define EMR clusters, steps and bootstrap actions. Their format is defined in the [official documentation of the Amazon Web Services (AWS) SDK for Python (Boto)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html).

The `awsflow` package maintains a registry of the templates in `awsflow.templates.__init__.py`. 
The available templates can be listed as follows:

```
bash-4.2# awsflow.emr templates
2019-04-02 15:00:48,647 | INFO     | EMR cluster templates: ['sushi', 'cheap']
2019-04-02 15:00:48,647 | INFO     | EMR step templates: ['install-jupyter-s3', 'install-jupyter-local', 'slack-message', 'update-awsflow']
2019-04-02 15:00:48,647 | INFO     | EMR bootstrap templates: ['install-pkg-awsflow']
bash-4.2# awsflow.emr templates
```

> The `cheap` and `sushi` EMR templates do not terminate once their steps have been completed. To change this behavior, you should set the value of `KeepJobFlowAliveWhenNoSteps` in the EMR template to `False`. 

To render a template:

```
bash-4.2# awsflow.emr render --step install-jupyter-local
2019-04-02 15:05:19,547 | INFO     | Step template:

{
    "ActionOnFailure": "TERMINATE_CLUSTER",
    "HadoopJarStep": {
        "Args": [
            "/usr/local/bin/awsflow.add.jupyter"
        ],
        "Jar": "command-runner.jar"
    },
    "Name": "install-jupyter-local"
}


bash-4.2# 
```

Template names are passed by the `--cluster`, `--step`, and `--bootstrap` parameters for EMR clusters, steps, and bootstrap actions, respectively.

Templates can have parameters resolved at runtime. E.g., the `install-jupyter-s3` step template. Parameters are passed with repeated `--param name=value` arguments. E.g.,

```
bash-4.2# awsflow.emr render --step install-jupyter-s3 --param s3bucket=datascience --param s3prefix=homes/Michele
2019-04-02 15:09:50,652 | INFO     | Template parameters: {'s3bucket': 'datascience', 's3prefix': 'homes/Michele'}
2019-04-02 15:09:50,652 | INFO     | Step template:

{
    "ActionOnFailure": "TERMINATE_CLUSTER",
    "HadoopJarStep": {
        "Args": [
            "/usr/local/bin/awsflow.add.jupyter",
            "--bucket",
            "datascience",
            "--prefix",
            "homes/Michele/jupyter"
        ],
        "Jar": "command-runner.jar"
    },
    "Name": "install-jupyter-s3"
}


bash-4.2# 
```

All tasks that require templates (`create`, `step`, `render`) accept `--param` arguments as well.
To add custom templates, add them in the appropriate subpackage and register them.

## Managing Lambda functions

Lambda functions are built including the `awsflow` package in their context, altogether
will all required dependencies. This is achieved by deploying Lambda functions as [AWS Lambda Deployment Packages](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html) in a transparent way.

Lamda functions are located at `awsflow.lambdas`.

To list the uploaded Lambda functions:

```
awsflow.lambda list
```

To create a Lambda function from the `demo` module, function `hello_world`:

```
awsflow.lambda create --mod demo --func hello_world
```

To delete an uploaded Lambda function:

```
awsflow.lambda delete --name hello_world
```

Building from scratch the archive with all dependencies is time-consuming.
You can use the caching mechanism to save time, specifying a cache key 
that is used to form a cache directory for the archive: 

```
awsflow.lambda create --mod demo --func hello_world --cache cached1

```

The cache key can then be used again to update the Lambda function:

```
awsflow.lambda update --mod demo --func hello_world --cache cached1

```

Let's test the Lambda function above with this test event from the AWS web console:


```
{
  "message": "Hello world!"
}
```

The returned value will be similar to:

```
{
  "parameters": "event={'message': 'Hello world!'} context=<__main__.LambdaContext object at 0x7f32ccd1ab38>",
  "awsflow-version": "0.0.71"
}
```

As you can see, the `awsflow` version is returned, confirming that we indeed have access to the package from the context of the Lambda function!

Let's do a step further, starting and EMR cluster from a Lambda function:


```
awsflow.lambda create --mod daily --func start_emr --cache cached1
```

Again, we used the caching mechanism but in this case for a different Lambda function: `start_emr`.
The cache will contain the module `demo` that is not be required. However, its impact on the overall
archive size is neglectable.

Let's test the creation of the EMR cluster with this test event:

```
{
  "time": "2019-02-12T05:00:00Z"
}
```

The returned value will be similar to:

```
{
  "request_time": "2019-02-12 05:00:00",
  "cluster_id": "j-374732K3RZK9X",
  "awsflow-version": "0.0.71"
}
```

The value of "awsflow-version" can be checked against your local copy. "cluster_id" contains the EMR cluster ID being created. The function returns immediately and doesn't wait for the completion of the creation.

Adding custom Lambda functions is as easy as adding them in modules inside the `awsflow.lambdas` subpackage. There is no registry for Lambda functions.

## Iterative development process

Changes to the awsflow package are immediately reflected inside the container and can be pushed to AWS with `fab pkg_deploy`. PEP8 compliance is ensured with `fab test_pep8` and some fixes can be automated with `fab fix_pep8`.
Additional tests can be added at `awsflow.tests`.

> Warning: updating the deployed package does not update the package version included in uploaded Lambda functions. You must update each uploaded Lambda function separately.

## Additional features

The package provides also these other functionalities:

* All command line tools are also accessible programmatically
* Slack integration: send messages easily from command line, as implemented in the `awsflow.templates.step.slack`
* Update the installed `awsflow` from command line with the `awsflow.update` command to a specific version 
* Add Python packages from S3 with the `awsflow.add.pkg` command line tool
* Add custom command line tools in `awsflow.tools`, making them available from `setup.py`
* Add additional Python code with the `--include` parameter, available for both `awsflow.emr` and `awsfloe.lambda` on all tasks.

# Credits and license

* Thank You to Minodes, a Telefónica NEXT company, for the opportunity to open-source **AWSFlow**
* The **AWSFlow** project is released under the [MIT license](LICENSE.txt)

# Contributing

1. Fork it
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Create a new Pull Request

