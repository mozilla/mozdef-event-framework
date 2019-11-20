import logging
import json
import boto3
import os
import sys
import socket
import cis_logger    # Custom module
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all


REGION = os.getenv('REGION', 'us-west-2')
ssm = boto3.client('ssm', region_name=REGION)
service_token = os.getenv('TOKEN')

patch_all()


def setup_logging():
    logger = logging.getLogger()
    for h in logger.handlers:
        logger.removeHandler(h)
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(cis_logger.JsonFormatter(extra={"hostname": socket.gethostname()}))
    logger.addHandler(h)
    logger.setLevel(logging.INFO)

    # Quiet botocore verbose logging...
    logging.getLogger("botocore").setLevel(logging.WARNING)
    return logger

def generate_policy(principalId, effect, resource):
    authResponse = {}
    authResponse['principalId'] = principalId
    if effect and resource:
        policyDocument = {}
        policyDocument['Version'] = '2012-10-17'
        policyDocument['Statement'] = []
        statementOne = {}
        statementOne['Action'] = 'execute-api:Invoke'
        statementOne['Effect'] = effect
        statementOne['Resource'] = resource
        policyDocument['Statement'].append(statementOne)
        authResponse['policyDocument'] = policyDocument

    return authResponse


def get_auth_token(ssm_client=ssm, token=service_token):
    logger = setup_logging()
    try:
        logger.info("Obtaining auth token from SSM.")
        response = ssm.get_parameter(Name=token, WithDecryption=True)
        auth_token = response['Parameter']['Value']
        return auth_token
    except Exception as e:
        logger.error("A problem occurred while accessing SSM, exception: {}".format(e))
        return False


def validate_token(event, context, ssm_client=ssm, token=service_token):
    logger = setup_logging()
    if 'authorizationToken' not in event:
        logger.error("No authorization header received, denying access.")
        return {
            'statusCode': 403,
            'body': json.dumps('Unauthorized.')
        }
    else:
        request_token = event['authorizationToken']
        auth_token = get_auth_token(ssm_client, token=token)
        if not auth_token:
            # Unable to fetch auth token from SSM for some reason, return "Deny"
            logger.error("Unable to retrieve auth token from SSM.")
            deny_response = generate_policy('webhook_service', 'Deny', event['methodArn'])
        elif auth_token and str(request_token) == auth_token:
            # Correct authorization token, we should allow
            logger.info("Correct authorization token received, passing event to handler.")
            allow_response = generate_policy('webhook_service', 'Allow', event['methodArn'])
            return allow_response
        else:
            # Incorrect token received, we should deny
            # TODO: We should implement monitoring on "Deny" events
            # This will be done in another PR
            logger.warning("Incorrect authorization token received, dropping event.")
            deny_response = generate_policy('webhook_service', 'Deny', event['methodArn'])
            return deny_response

    # Default response
    return {
        'statusCode': 403,
        'body': json.dumps('Unauthorized.')
    }
