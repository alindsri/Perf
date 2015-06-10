# Workload Simulation Using Containers as Clients

## About

Refer to the [Workload Simulation Using Containers as Clients](http://cloud.google.com/solutions/workload-simulation-using-containers-as-clients) solutions paper.

## Prerequisites

* Google Cloud Platform account
* Install and setup [Google Cloud SDK](https://cloud.google.com/sdk/)

**Note:** when installing the Google Cloud SDK you will need to enable the following additional components:

* `App Engine Command Line Interface (Preview)`
* `App Engine SDK for Python and PHP`
* `Compute Engine Command Line Interface`
* `Developer Preview gcloud Commands`
* `gcloud Alpha Commands`
* `gcloud app Python Extensions`
* `kubectl`

Before continuing, you can also set your preferred zone and project:

    $ gcloud config set compute/zone ZONE
    $ gcloud config set project PROJECT-ID

## Deploy Web Application

The `sample-webapp` folder contains a simple Google App Engine Python application as the "system under test". To deploy the application to your project use the `gcloud preview app deploy` command.

    $ gcloud preview app deploy sample-webapp/app.yaml

**Note:** you will need the URL of the deployed sample web application when deploying the `locust-master` and `locust-worker` controllers.

## Deploy Controllers and Services

Before deploying the `locust-master` and `locust-worker` controllers, update each to point to the location of your deployed sample web application. Set the `TARGET_HOST` environment variable found in the `spec.template.spec.containers.env` field to your sample web application URL.

    - name: TARGET_HOST
      key: TARGET_HOST
      value: http://YOUR-APPLICATION.appspot.com

### Update Controller Docker Image (Optional)

The `locust-master` and `locust-worker` controllers are set to use the pre-built `locust-tasks` Docker image, which has been uploaded to the [Google Container Registry](http://gcr.io) and is available at `gcr.io/cloud-solutions-images/locust-tasks`. If you are interested in making changes and publishing a new Docker image, refer to the following steps.

First, [install Docker](https://docs.docker.com/installation/#installation) on your platform. Once Docker is installed and you've made changes to the `Dockerfile`, you can build, tag, and upload the image using the following steps:

    $ docker build -t USERNAME/locust-tasks .
    $ docker tag USERNAME/locust-tasks gcr.io/PROJECT-ID/locust-tasks
    $ gcloud preview docker --project PROJECT-ID push gcr.io/PROJECT-ID/locust-tasks

**Note:** you are not required to use the Google Container Registry. If you'd like to publish your images to the [Docker Hub](https://hub.docker.com) please refer to the steps in [Working with Docker Hub](https://docs.docker.com/userguide/dockerrepos/).


Once the Docker image has been rebuilt and uploaded to the registry you will need to edit the controllers with your new image location. Specifically, the `spec.template.spec.containers.image` field in each controller controls which Docker image to use.

If you uploaded your Docker image to the Google Container Registry:

    image: gcr.io/PROJECT-ID/locust-tasks:latest

If you uploaded your Docker image to the Docker Hub:

    image: USERNAME/locust-tasks:latest

**Note:** the image location includes the `latest` tag so that the image is pulled down every time a new Pod is launched. To use a Kubernetes-cached copy of the image, remove `:latest` from the image location.

### Deploy Kubernetes Cluster

First create the [Google Container Engine](http://cloud.google.com/container-engine) cluster using the `gcloud` command (this command defaults to creating a three node Kubernetes cluster (not counting the master) using the `n1-standard-1` machine type, refer to the `gcloud` [documentation](https://cloud.google.com/sdk/gcloud/reference/alpha/container/clusters/create) for information on specifying a different configuration).

    $ gcloud alpha container clusters create CLUSTER-NAME

After a few minutes, you'll have a working Kubernetes cluster with three nodes (not counting the Kubernetes master). Next, configure your system to use the `kubectl` command:

    $ kubectl config use-context gke_PROJECT-ID_ZONE_CLUSTER-NAME

**Note:** the output from the previous `gcloud` cluster create command will contain the specific `kubectl config` command to execute for your platform/project.

### Deploy locust-master

Now that `kubectl` is setup, deploy the `locust-master-controller`:

    $ kubectl create -f locust-master-controller.yaml

To confirm that the Replication Controller and Pod are created, run the following:

    $ kubectl get rc
    $ kubectl get pods -l name=locust,role=master

Next, deploy the `locust-master-service`:

    $ kubectl create -f locust-master-service.yaml

This step will expose the Pod with an internal DNS name (`locust-master`) and ports `8089`, `5557`, and `5558`. As part of this step, the `createExternalLoadBalancer` directive in `locust-master-service.yaml` will tell Google Container Engine to create a Google Compute Engine forwarding-rule from a publicly avaialble IP address to the `locust-master` Pod. To view the newly created forwarding-rule, execute the following:

    $ gcloud compute forwarding-rules list 

### Deploy locust-worker

Now deploy `locust-worker-controller`:

    $ kubectl create -f locust-worker-controller.yaml

The `locust-worker-controller` is set to deploy 10 `locust-worker` Pods, to confirm they were deployed run the following:

    $ kubectl get pods -l name=locust,role=worker

Next, deploy the `locust-worker-service`:

    $ kubectl create -f locust-worker-service.yaml 

This step will expose the Pods with an internal DNS name (`locust-worker`) and ports `5557` and `5558`, (additionally as part of the Service layer, an internal proxy is created to load balance across the worker instances using the internal DNS name).

### Setup Firewall Rules

The final step in deploying these controllers and services is to allow traffic from your publicly accessible forwarding-rule IP address to the appropriate Container Engine instances.

The only traffic we need to allow externally is to the Locust web interface, running on the `locust-master` Pod at port `8089`. To create the firewall rule, execute the following:

    $ gcloud compute firewall-rules create firewall-rule-name --allow=tcp:8089 --target-tags k8s-CLUSTER-NAME-node

## Execute Tests

To execute the Locust tests, navigate to the IP address of your forwarding-rule (see above) and port `8089` and enter the number of clients to spawn and the client hatch rate.

## License

This code is Apache 2.0 licensed and more information can be found in `LICENSE`. For information on licenses for third party software and libraries, refer to the `docker-image/licenses` directory.