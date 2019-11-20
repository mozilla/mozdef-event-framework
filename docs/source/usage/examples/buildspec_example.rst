Buildspec Example
=================

"""
buildspec.yml
=============

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
      - $CODEBUILD_SRC_DIR/config/deploy.sh deploy $STAGE $AWS_REGION::
"""
