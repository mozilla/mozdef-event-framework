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