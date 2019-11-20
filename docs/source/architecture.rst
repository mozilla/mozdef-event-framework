Architecture
============

**Cloudformation:** Cloudformation will create the CI/CD components utilizing:

    **CodePipeline**

    **CodeCommit**

    **CodeBuild**

    **s3**

    **CloudWatch**

    **GitHub**


The intended behavior is to pull the framework from GitHub, and the custom configuration for a specific event source from its CodeCommit repository.
The Cloudformation template has the potential to be separately deployed for various event sources, while the only difference will be the event source's CodeCommit repository that contains the custom configuration data for that event source.
This allows us to maintain a generic framework that is event source agnostic and relieved of sensitive data.

**Serverless:** The Serverless framework deploys the application components that will handle the event source data. This framework creates the following resources:

    * A **custom authorizer** for webhook based APIs that use an Authorization header.
    * An **API Gateway** for receiving post events using the authorizer.
    * Custom configuration variables that are populated by the buildspec.yml located in each event source configuration's **CodeCommit** repository.
    * A **lambda** event handler that will validate to some degree the event to be processed by MozDef. At some point we may extend functionality here to fully process the event by another lambda.
    * An **SQS queue** to receive the events that have been handled by our lambda handler.
    * An **SQS Dead Letter Queue (DLQ)** to receive events that fail to be handled, so that they can be reprocessed once a fix is introduced. This is future functionality that has not been implemented yet.

To deploy this framework you will need the following established:

    1. You'll need to design your parameter store pathing, and add your tokens or other data to be used with the framework. We used the following structure:

    /<Project_name>/<event_source_name>/<environemnt>/<authorizer_token_var>/

    2. This allows us to keep track of the various event sources, what environment they are used in, and keep the same variables across all event sources that will contain different values.

    3. An AWS Account with the ability to use all of the AWS services previously mentioned.

    4. A CodeCommit repository that contains your buildspec and deploy script.

    Please note the env: variables that must be filled out, these can essentially be whatever you want them to be.

    5. The GitHub Framework Repo which contains the initial Cloudformation template, this will automatically create your CI/CD pipeline and build out the serverless application as a part of that. You should not need to make any changes to it unless you plan to modify it for your own purposes, which is entirely OK for us!
    An S3 bucket to hold the merger lambda code (merge.zip) and your zipped CodeCommit repository for your specific event source, mark this bucket private (not public), the CF template will create the CodeCommit Repo for you with your code. This will only need to be done once per event source, once the repo is created, you may commit to it via git or directly through aws-cli or the console.
