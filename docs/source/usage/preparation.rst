Preparation
============

To deploy this framework you will need the following established:


    1. **AWS Account:**

      An AWS Account with the ability to use all of the AWS services previously mentioned.

    2. **Environment Variables:**

      Decide on the various parameter and environment variable values, as these are referenced throughout the CF templates and serverless framework configuration. These include (example values in parenthesis):

        * Project (e.g., MozDef-EF)
        * Service (e.g., zoom)
        * Environment or Stage (e.g. dev)
        * Stack name (e.g., <project>-<service>, MozDef-EF-zoom)
        * Token Arn (e.g., arn:aws:ssm:us-west-2:<ACCOUNT_ID>:parameter/<project/service/environment/auth_token>, arn:aws:ssm:us-west-2:<ACCOUNT_ID>:parameter/MozDef-EF/zoom/dev/auth_token>)


    3. **SSM/KMS/Secrets Manager:**

      You'll need to design your parameter store pathing, and add your tokens or other data to be used with the framework. This allows us to keep track of the various event sources, what environment they are used in, and keep the same variables across all event sources that will contain different values.
      We used the following structure::

        /<project>/<service>/<environment>/auth_token

      .. note:: If you would like use Github in your workflow to host your code and/or configuration, you will need to generate a Personal Access Token in GitHub, and store the token in AWS Secrets Manager. We assumed the following structure in our Cloudformation template::
        
        <environment>/codepipeline/github

      See :doc:`deployment` section for more details.

    4. **A CodeCommit or Github repository:**

      This is where your configuration files will be stored in addition to the buildspec and deploy scripts.
      If you parameterize all your sensitive data, there shouldn't be any risk of sensitive data disclosure.

      **Note:** The env: variables that must be filled out, these can essentially be whatever you want them to be provided they fall in line with the naming conventions the cloudformation and serverless scripts expect.


    5. **GitHub Framework Repo:**

      This repo contains all the templates you'll need to build out the pipeline. 
      The cloudformation template will automatically build your CI/CD pipeline which will deploy the serverless application. 
      You should not need to make any changes to it unless you plan to modify it for your own purposes, which is entirely OK with us!


    6. **Pick a Cloudformation template:**
    
      If you choose to use the multiple source cloudformation template, you'll need:

      * A private S3 bucket to hold the merge lambda code (merge.zip)
      * Add an archive of your zipped configuration files (templates are in the framework Github repo you clone) to the bucket you use for the merge lambda.

      **Note:** The CF template will create a CodeCommit Repo with your configuration structure.
      This will only need to be done once per event source, once the repo is created, you may commit to it via git or directly through aws-cli or the console.
