Installation
============

To deploy this framework you will need the following established:

    1. You'll need to design your parameter store pathing, and add your tokens or other data to be used with the framework. We used the following structure::

        /<Project_name>/<event_source_name>/<environment>/<authorizer_token_var>/

    note::
    This allows us to keep track of the various event sources, what environment they are used in, and keep the same variables across all event sources that will contain different values.


    2. An AWS Account with the ability to use all of the AWS services previously mentioned.


    3. A CodeCommit or Github repository that contains your configuration files in addition to the buildspec and deploy scripts.

    note::
    The env: variables that must be filled out, these can essentially be whatever you want them to be.


    4. The GitHub Framework Repo which contains the initial Cloudformation template, this will automatically create your CI/CD pipeline and build out the serverless application as a part of that. You should not need to make any changes to it unless you plan to modify it for your own purposes, which is entirely OK for us!


    5. If you choose to use the multiple source cloudformation template, you'll need an S3 bucket to hold the merge lambda code (merge.zip) and an archive of your zipped configuration files (templates are in the framework Github repo you clone), for your specific event source, mark this bucket private (not public).

       The CF template will create a CodeCommit Repo for you with your code. This will only need to be done once per event source, once the repo is created, you may commit to it via git or directly through aws-cli or the console.
