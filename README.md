# Data Engineering Test

## Why..

**Running the Pyspark Job in a Local Environment for Unit testing**
 1. Since there will be no drastic load in dev/testing environment,I will be using pre-   built image and run it locally.
    
2. If the workflow is bit complex then the dockerfile can be used to create the custom image

**Running the Pyspark Job in a Production Environment**
 1. I have choosen AKS cluster 


## What..
 **Prerequisites for running the job in Local Environment**
 
 This can be used either for Unit testing
1. Docker Application in running state.I am using `Docker Desktop `in Windows   
2. Command Prompt
3. Python Script
4. Optional:You can also use the DockerFile for complex workflows

 **Prerequisites for running the job in Prod Environment/Distributed Manner**
 -  Azure account
-   A valid access key/secret key 
-   Azure Cli installed
-  AKS Cluster Created



## How..

**Local/Unit Testing**
1. Once the Docker app is up and running.Open the command prompt
 - [ ] **Note**: I am using Docker Desktop in WIndows
 2. Run the command without making use of dockerfile
```
docker run -it --rm --name python-script -v "$PWD":/usr/Subash/HelloFresh python:3 python readJSON.py
```
I am using **-v** to  mount the current working directory into the container.
 - [ ] **Note**:  I am importing  the image from a public repository but its not always recommended due to security concerns. Either we
       can push the images to `Azure Container Registry` or `Amazon ECR`
       and use the `docker pull` command to extract the images.
       
  3.  To create image with DockerFile
```
docker build -t SparkData  -f /<path to docker file>/Dockerfile
```
DockerFile Contents
You can also use `RUN` command with  `pip` to install libraries.Currently I am not using any extrenal libraries.`COPY` command copies the files to Container directories
 - [ ] **Note**: It has to be ensured that  there should be no  extension to the Dockerfile (i.e. Docker does not recognize
       Dockerfile.txt

```
from gcr.io/datamechanics/spark:platform-3.1-dm14

ENV PYSPARK_MAJOR_PYTHON_VERSION=3

WORKDIR /opt/application/

copy readJSON_Spark.py
```
 
3. Execute the below command to run the image locally
```
docker run SparkData
```

**Deploying on a Cluster**

1. ##### Create an AKS cluster

Ref Link-https://docs.microsoft.com/en-us/azure/aks/kubernetes-action#code-try-0
