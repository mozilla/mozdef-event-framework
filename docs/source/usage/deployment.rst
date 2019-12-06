==========
Deployment
==========

This guide uses Zoom as our service, your service may be different, be sure to name it something appropriately. 

***************
Getting Started
***************

  1. Clone the master branch of the repository at “https://github.com/mozilla/mozdef-event-framework” to the local file system.
  2. Before any action, decide on the various parameter and environment variable values, as these are referenced throughout the CF templates and serverless framework configuration.
     The following are the environment variables with example values:

     * PROJECT: MozDef-EF
     * SERVICE: zoom
     * STAGE: dev
     * API_PATH: events
     * Stack name: zoom2mozdef

************************
Steps in the AWS Console
************************

You'll need to log into the AWS console or you can alternatively use the aws-cli to create the parameters needed for your webhook to properly authenticate:

  1. Login to AWS Console using your account credentials. This framework has been tested to work with federated logins where the user assumes a role.
  2. Navigate to “Services” and under “Management and Governance” select “Systems Manager”
  3. Once the page loads, under “Application Management, choose “Parameter Store"
  4. Create a parameter there in the form of:

      “/<project>/<service>/<environment>/auth_token”

      **Example:** For our Zoom example, this would be something like:
       
    .. image:: ../images/Parameter_Store_Example.png
       :width: 400
       :alt: /MozDef-EF/zoom/prod/auth_token

  5. In the description field, add “Authentication token used by the Webhook app to post events”.
  6. For type, select “SecureString”. 
  7. For value, paste the value from the app’s configuration from your webhook's configured authentication token.
  8. Add a Tag with key: Project and value: MozDef-EF-<environment>, then create the parameter.

*************************************
Fill in the Framework Config Template
*************************************

The following should be done in your local copy of the framework you cloned or forked:


  1. Open the downloaded repository in an IDE to edit locally.
  2. Under config directory, edit “buildspec-prod.yml” file to contain:

    .. code-block:: yaml
    
       version: 0.2
       
       env:
         variables:
           STAGE: prod
           SERVICE: zoom
           PROJECT: MozDef-EF
           API_PATH: zoom
           TOKEN_ARN: arn:aws:ssm:<REGION_NAME>:<ACCOUNT_ID>:parameter/<parameter-name>
       
       phases:
         install:
           runtime-versions:
             python: 3.7
             nodejs: 10
           commands:
             # Install dependencies here
             - pip3 install --upgrade awscli -q
             - pip3 install --upgrade pytest -q
             - pip3 install --upgrade moto -q
             - pip3 install --upgrade aws-xray-sdk -q
             - npm install -g --silent --progress=false serverless
             - npm install --silent --save-dev serverless-pseudo-parameters
             - npm install --silent --save-dev serverless-prune-plugin
         pre_build:
           commands:
             # Perform pre-build actions here
             - chmod +x $CODEBUILD_SRC_DIR/config/deploy.sh
             - $CODEBUILD_SRC_DIR/config/deploy.sh unit-test
         build:
           commands:
             # Invoke the deploy script here
             - $CODEBUILD_SRC_DIR/config/deploy.sh deploy $STAGE $AWS_REGION


  3. The important part here is the filling in of the “env” section at the top of the file. These environment variables will be used by the “serverless.yml” file when deployed by the serverless framework.
     For each service deployed for a source (such as zoom), the service name and API path will be different.
  4. Save the file.
  5. Make any other desired changes on the local copy. For webhook based services, like zoom, there should not be any additional changes needed.

*********************
Deploy Your Framework
*********************

This is where we take everything we've done up to this point and start the deployment.

  1. Go back to AWS Console  “Services -> CodeCommit” and create a repository with the name “<project>-<service>”, in this case “mozdef-ef-zoom”. Add a description and a tag using these keys: <project>-<environment>.
  2. Using the connection settings, setup Git access with the git credential helper over HTTPS (ensure you can pull and push to the newly created repo)
  3. Pull the empty repository to a local directory, then add/move all the cloned and updated framework code to this repository. Add and commit all changes, then push.
  4. Go to “Services -> CloudFormation” on the AWS Console.
  5. On top right, click “Create stack (with new resources)”
  6. Select “template is ready” on the first option. In “specify template” menu, select “upload a template file”

       .. toggle-header::
           :header: **2. Create stack from Template:**
       
             Example screenshot for creating a stack from the template
       
             .. image:: ../images/create_stack.png
                :width: 400
                :alt: AWS Cloudformation Console Create Stack

  7. Browse the filesystem, and select the CloudFormation template you wish to use under the “templates” directory of the cloned and updated framework code. Assuming no syntax errors, click next.
  8. For the stack name, enter something descriptive, like: <project>-<service> (e.g., mozdef-ef-zoom, see the example image below for steps 8 through 14)
  9. For stack parameters, enter the values decided in "Getting Started" Step 2.
  10. For service, enter your <service> name that you determined in the "Getting Started" section Step 2.
  11. For environment, choose “dev”, "staging", or "prod" according to the environment you are working out of.
  12. In the TOKEN_ARN field, you'll need to enter your token arn to correctly map the iam permissions for this resource.
  13. An S3 utility bucket will be created for AWS CodePipeline to store artifacts. The bucket name will match the parameters you created for your stack name in step 8 and the environment in step 11 (e.g., <stackname>-<environment>-utility)
  14. For source configuration, enter the name of the codecommit repo created in step 1, and the branch to monitor for changes and trigger rebuilds of the deployment. For our example we used zoom, “mozdef-ef-zoom/master”.
  
       .. toggle-header::
           :header: **2. Stack Details:**
       
             Example screenshot for steps 8 through 14
       
             .. image:: ../images/stack_details.png
                :width: 400
                :alt: AWS Cloudformation Console Stack Details
  
  15. Under stack options, add a tag with key: Project and value: <project>-<environment>. Click Next
  16. On the review step, check the box under “Capabilities” saying “I acknowledge that AWS CloudFormation might create IAM resources with custom names.”.
  17. Click Create Stack. On the Cloudformation page, check the stack creation status. It should deploy the pipeline stack successfully.
  18. Once the API Gateway has been created, copy the URL into your webhook application's configuration as the endpoint to post events to begin sending events to the AWS infra that was deployed using this framework.
