# MozDef Event Framework

A PoC using AWS + Serverless framework

This is a work in progess which will eventually be used as a template for external event sources.

The idea behind this work was to create a repeatable process for introducing new event sources to MozDef without having to specially craft it every time. While this is new and we haven't onboarded many sources yet, it is expected the function library may grow, and with it we will introduce further changes to this framework as it becomes more mature. 

For example, being able to handle SSO, JWT, or other methods of authorizing event sources are in our interest to support, as well as the ability to reach out and pull down data from Rest API's using those methods of authorization. With the introduction of this framework we should be able to have a repeatable CI/CD pipeline, and be able to add to the library many functions to handle various types of connectivity and data retrieval without much additional work.
___
## Framework Components

__Cloudformation:__ Cloudformation will create the CI/CD components utilizing:
- __CodePipeline__
- __CodeCommit__
- __CodeBuild__
- __s3__
- __CloudWatch__
- __GitHub__.

The intended behavior is to pull the framework from GitHub, and the custom configuration for a specific event source from its CodeCommit repository. The Cloudformation template has the potential to be separately deployed for various event sources, while the only difference will be the event source's CodeCommit repository that contains the custom configuration data for that event source. This allows us to maintain a generic framework that is event source agnostic and relieved of sensitive data. 

__Serverless:__ The Serverless framework is utilized to deploy the actual application that will handle the event source data. This framework creates the following resources:
 - A custom authorizer for webhook based APIs that use an Authorization header.
 - An API Gateway for receiving post events using the authorizer.
 - Custom configuration variables that are populated by the `buildspec.yml` located in each event source configuration's CodeCommit repository.
 - A lambda event handler that will validate to some degree the event to be processed by MozDef. At some point we may extend functionality here to fully process the event by another lambda.
 - An SQS queue to receive the events that have been handled by our lambda handler.
 - A Dead Letter Queue (DLQ) to receive events that fail to be handled, so that they can be reprocessed once a fix is introduced. This is future functionality that has not been implemented yet.

We plan to include testing modules in this framework as well.

To deploy this framework you will need the following established:

1. You'll need to design your parameter store pathing, and add your tokens or other data to be used with the framework. We used the following structure:

   `/<Project_name>/<event_source_name>/<environemnt>/<authorizer_token_var>/`

   This allows us to keep track of the various event sources, what environment they are used in, and keep the same variables across all event sources that will contain different values.

2. An AWS Account with the ability to use all of the AWS services previously mentioned.

3. A CodeCommit repository that contains your buildspec and deploy script.

   Please note the env: variables that must be filled out, these can essentially be whatever you want them to be.
___

__Example of a Buildspec:__

```
version: 0.2 
 
env:  
  variables: 
    STAGE: dev 
    SERVICE: zoom 
    PROJECT: MozDef-EF 
    API_PATH: zoom 
  ssm: 
 
phases: 
  install: 
    runtime-versions: 
      python: 3.7 
      nodejs: 10 
    commands: 
      # Install dependencies here 
      - pip3 install --upgrade awscli -q 
      - npm install -g --silent --progress=false serverless 
      - npm install --silent --save-dev serverless-pseudo-parameters 
      - npm install --silent --save-dev serverless-prune-plugin 
  pre_build: 
    commands: 
      # Perform pre-build actions here, maybe tests for instance 
  build: 
    commands: 
      # Invoke the deploy script here 
      - chmod +x $CODEBUILD_SRC_DIR/config/deploy.sh 
      - $CODEBUILD_SRC_DIR/config/deploy.sh deploy $STAGE $AWS_REGION 
```

___    

**Example of the deploy script**

```
#!/bin/bash     
 
# This is deploy script template. Feel free modify per service/resource. 
   
instruction()   
{   
  echo "-----------------------------------------------"   
  echo "usage: ./deploy.sh deploy <env>"   
  echo "env: eg. dev, staging, prod, ..."   
  echo "for example: ./deploy.sh deploy dev"   
  echo ""   
  echo "to test: ./deploy.sh <int-test|acceptance-test>"   
  echo "for example: ./deploy.sh acceptance-test"   
}  
  
if [ $# -eq 0 ]; then 
  instruction   
  exit 1   
elif [ "$1" = "int-test" ] && [ $# -eq 1 ]; then 
  pytest int-test   
   
elif [ "$1" = "acceptance-test" ] && [ $# -eq 1 ]; then 
  pytest acceptance-test   
   
elif [ "$1" = "deploy" ] && [ $# -eq 3 ]; then 
  STAGE=$2   
  REGION=$3 
  STATE=`aws cloudformation describe-stacks --stack-name "$SERVICE-$STAGE" \ 
        --query Stacks[*].StackStatus --output text | grep -E "ROLLBACK|FAIL" -c` 
  # Forcefully remove the stack deployed by Serverless   
  # framework ONLY IF previous build errored  
  # NOTE: This is probably only a good idea for dev stage  
  if [ $STATE -ne 0 ]; then 
     sls remove -s $STAGE -r $REGION --force 
  fi   
  sleep 2  
  # Try to deploy again after stack removal  
  sls deploy -s $STAGE -r $REGION --force 
 
else   
  instruction   
  exit 1   
fi  
```
4. The GitHub Framework Repo which contains the initial Cloudformation template, this will automatically create your CI/CD pipeline and build out the serverless application as a part of that. You should not need to make any changes to it unless you plan to modify it for your own purposes, which is entirely OK for us!
5. An S3 bucket to hold the merger lambda code (merge.zip) and your zipped CodeCommit repository for your specific event source, mark this bucket private (not public), the CF template will create the CodeCommit Repo for you with your code. This will only need to be done once per event source, once the repo is created, you may commit to it via git or directly through aws-cli or the console.

## Run It!
Upload the cloudformation template, fill in the CloudFormation parameters and environment variables according to your design, unless you intend to use the defaults, and wait for it to complete!
To run multiple deployments (e.g if you have multiple event sources you would like to consume), you'll need to rename the cloudformation template each time you upload it for a new deployment.

For convenience, you may run the CloudFormation template with an AWS account that has administrative rights. This should be fine, as dedicated IAM roles associated with the resources are created by both the Cloudformation template and the Serverless framework. You can fine tune permissions for these roles within the Cloudformation template and/or serverless yaml configuration file (serverless.yml).