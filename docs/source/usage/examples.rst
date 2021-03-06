Examples
========

We've  included some sample scripts you can modify for your deployment.

You'll want to replace the [env:variables]: for 'SERVICE' and 'API_PATH' to whatever you have decided upon for your event source pipeline and API gateway path.

Buildspec Example
-----------------

buildspec.yml::

  version: 0.2 

  env:  
    variables: 
      STAGE: dev 
      SERVICE: zoom 
      PROJECT: MozDef-EF 
      API_PATH: zoom
      TOKEN_ARN: arn:aws:ssm:$AWS_REGION:<ACCOUNT_ID>:parameter/<parameter-name>

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
        # Remove or comment out the next line if you are not using 
        # "serverless-python-requirements" plugin to manage 3rd party Python libraries
        - npm install --silent --save-dev serverless-python-requirements
    pre_build: 
      commands: 
        # Perform pre-build actions here
        - chmod +x $CODEBUILD_SRC_DIR/config/deploy.sh
        - $CODEBUILD_SRC_DIR/config/deploy.sh unit-test
    build: 
      commands: 
        # Invoke the deploy script here 
        - $CODEBUILD_SRC_DIR/config/deploy.sh deploy $STAGE $AWS_REGION

Deploy Script Example
---------------------

deploy.sh::

  #!/bin/bash     
   
  # This is deploy script template. Feel free modify per service/resource. 
     
  instruction()   
  {   
    echo "-----------------------------------------------"   
    echo "usage: ./deploy.sh deploy <env>"   
    echo "env: eg. dev, staging, prod, ..."   
    echo "for example: ./deploy.sh deploy dev"   
    echo ""   
    echo "to test: ./deploy.sh <int-test|unit-test>"   
    echo "for example: ./deploy.sh unit-test"   
  }  
    
  if [ $# -eq 0 ]; then 
      instruction
      exit 1
  elif [ "$1" = "int-test" ] && [ $# -eq 1 ]; then
      python3 -m pytest "$CODEBUILD_SRC_DIR/tests/int-tests/"
  
  elif [ "$1" = "unit-test" ] && [ $# -eq 1 ]; then
      python3 -m pytest "$CODEBUILD_SRC_DIR/tests/unit-tests/"
  
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
