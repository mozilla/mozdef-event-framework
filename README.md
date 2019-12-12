# MozDef Event Framework

A PoC using AWS + Serverless framework

This is a work in progess which will eventually be used as a template to create a pipeline which will send events from external sources to [MozDef]("https://mozdef.readthedocs.io/en/latest/").

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

The intention is to have a template of a framework which we store in GitHub, however, the custom configuration for each specific event source can be stored in  either a CodeCommit or separate GitHubrepository. The Cloudformation template has the potential to be separately deployed for various event sources, where the difference between each deployed stack will be the event source's configuration stored in the CodeCommit/GitHub repository. This allows us to maintain a generic framework that is event source agnostic and relieved of sensitive data. 

__Serverless:__ The Serverless framework is utilized to deploy the application components that will handle intake of the event source data, do some minor structuring for MozDef via Lambda and add it to an SQS queue. 
This framework creates the following resources:
 - A custom authorizer for webhook based APIs that use an Authorization header.
 - An API Gateway for receiving post events using the authorizer.
 - Custom configuration variables that are populated by the `buildspec.yml` located in each event source configuration's CodeCommit repository.
 - A lambda event handler that will validate to some degree the event to be processed by MozDef. At some point we may extend functionality here to fully process the event by another lambda.
 - An SQS queue to receive the events that have been handled by our lambda handler.
 - A Dead Letter Queue (DLQ) to receive events that fail to be handled, so that they can be reprocessed once a fix is introduced. This is future functionality that has not been implemented yet.

There are plans to include testing modules in this framework as well.

## Documentation

To deploy this framework please refer to our documentation located at the Read the Docs:

  [MozDef Event Framework Documentation]("https://mozdef-event-framework.readthedocs.io/en/latest/")

For convenience, you may run the CloudFormation template with an AWS account that has administrative rights. This should be fine, as dedicated IAM roles associated with the resources are created by both the Cloudformation template and the Serverless framework. You can fine tune permissions for these roles within the Cloudformation template and/or serverless yaml configuration file (serverless.yml).