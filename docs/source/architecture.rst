Architecture
============

Cloudformation
--------------

Cloudformation will create the CI/CD components utilizing:

    * **CodePipeline**
    * **CodeCommit**
    * **CodeBuild**
    * **S3**
    * **CloudWatch**
    * **Cloudtrail**
    * **GitHub**

There are multiple Cloudformation templates to choose from depending on the management style you prefer. The template can be deployed once for each event source you wish to integrate.
Each event source will have it's own configuration repository that the Cloudformation template will pull from to build the framework.
This allows us to maintain a generic framework that is event source agnostic and relieved of sensitive data while still maintaining configuration revision history specific to each event source.

Serverless
----------

The Serverless framework deploys the application components that will handle the event source data. This framework creates the following resources:

    * A **custom authorizer** for webhook based APIs that use an Authorization header.
    * An **API Gateway** for receiving post events using the authorizer.
    * Custom configuration variables that are populated by the buildspec.yml located in each event source configuration repository. [1]_
    * A **lambda** event handler that will validate to some degree the event to be processed by MozDef. At some point we may extend functionality here to fully process the event by another lambda.
    * An **SQS queue** to receive the events that have been handled by our lambda handler.
    * An **SQS Dead Letter Queue (DLQ)** to receive events that fail to be handled, so that they can be reprocessed once a fix is introduced. This is future functionality that has not been implemented yet.

.. [1] This repository can be in **GitHub** or **CodeCommit** depending on the Cloudformation template used.


