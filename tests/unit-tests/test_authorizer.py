import json
import pytest
import boto3
import os
from moto import mock_ssm


@pytest.fixture(scope='function')
def aws_credentials():
    # Mocked AWS Credentials for moto, this is required 
    # as per their readme: https://github.com/spulec/moto
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'

    # Disable X-Ray for unit tests
    from aws_xray_sdk import global_sdk_config
    global_sdk_config.set_sdk_enabled(False)

@pytest.fixture(scope='function')
def ssm(aws_credentials):
    mock = mock_ssm()
    mock.start()
    # There is currently a bug on moto, this line is needed as a workaround
    # Ref: https://github.com/spulec/moto/issues/1926
    # boto3.setup_default_session()

    ssm_client = boto3.client('ssm', 'us-west-2')
    token_name = "TEST_TOKEN"
    token_value = "TEST_VALUE"
    response = ssm_client.put_parameter(
        Name=token_name, Description="A test parameter", Value=token_value, Type="SecureString"
    )

    yield (ssm_client, token_name, token_value)
    mock.stop()

def test_generate_policy():
    from functions import authorizer
    test_principalId = "test-principal"
    test_effect_allow = "Allow"
    test_effect_deny = "Deny"
    test_resource = "arn:aws:execute-api:test-region:test-account:test-resource"

    allow_response = authorizer.generate_policy(
        test_principalId,
        test_effect_allow,
        test_resource
    )

    assert type(allow_response) is dict
    assert allow_response['principalId'] == test_principalId
    assert type(allow_response['policyDocument']) is dict
    assert allow_response['policyDocument']['Version'] == '2012-10-17'
    assert type(allow_response['policyDocument']['Statement']) is list
    assert allow_response['policyDocument']['Statement'][0]['Action'] == 'execute-api:Invoke'
    assert allow_response['policyDocument']['Statement'][0]['Effect'] == 'Allow'
    assert allow_response['policyDocument']['Statement'][0]['Resource'] == test_resource

    deny_response = authorizer.generate_policy(
        test_principalId,
        test_effect_deny,
        test_resource
    )

    assert type(deny_response) is dict
    assert deny_response['principalId'] == test_principalId
    assert type(deny_response['policyDocument']) is dict
    assert deny_response['policyDocument']['Version'] == '2012-10-17'
    assert type(deny_response['policyDocument']['Statement']) is list
    assert deny_response['policyDocument']['Statement'][0]['Action'] == 'execute-api:Invoke'
    assert deny_response['policyDocument']['Statement'][0]['Effect'] == 'Deny'
    assert deny_response['policyDocument']['Statement'][0]['Resource'] == test_resource

def test_get_auth_token_success(ssm):

    ssm_client, tname, tvalue = ssm
    # Local imports are also recommended as per moto
    # Ref: https://github.com/spulec/moto#what-about-those-pesky-imports
    from functions import authorizer
    # We have already created a test token, now attempt to retrieve it
    auth_token = authorizer.get_auth_token(ssm_client, tname)
    assert auth_token == tvalue

def test_get_auth_token_failure(ssm):

    ssm_client, tname, tvalue = ssm
    invalid_tvalue = "INVALID"
    # Local imports are also recommended as per moto
    # Ref: https://github.com/spulec/moto#what-about-those-pesky-imports
    from functions import authorizer
    # We have already created a test token, now attempt to retrieve it
    auth_token = authorizer.get_auth_token(ssm_client, invalid_tvalue)
    assert auth_token is False

def test_validate_token(ssm):

    ssm_client, tname, tvalue = ssm
    invalid_tvalue = "INVALID"
    
    valid_test_event = {
        'type': "TOKEN",
        'authorizationToken': tvalue,
        'methodArn': "arn:aws:execute-api:test-region:test-account:test-resource"
    }
    from functions import authorizer
    allow_response = authorizer.validate_token(valid_test_event, "", ssm_client, tname)
    
    assert type(allow_response) is dict
    assert allow_response['principalId'] == 'webhook_service'
    assert type(allow_response['policyDocument']) is dict
    assert allow_response['policyDocument']['Version'] == '2012-10-17'
    assert type(allow_response['policyDocument']['Statement']) is list
    assert allow_response['policyDocument']['Statement'][0]['Action'] == 'execute-api:Invoke'
    assert allow_response['policyDocument']['Statement'][0]['Effect'] == 'Allow'
    assert allow_response['policyDocument']['Statement'][0]['Resource'] == valid_test_event['methodArn']

    invalid_test_event = {
        'type': "TOKEN",
        'authorizationToken': invalid_tvalue,
        'methodArn': "arn:aws:execute-api:test-region:test-account:test-resource"
    }
    deny_response = authorizer.validate_token(invalid_test_event, "", ssm_client, tname)
    assert type(deny_response) is dict
    assert deny_response['principalId'] == 'webhook_service'
    assert type(deny_response['policyDocument']) is dict
    assert deny_response['policyDocument']['Version'] == '2012-10-17'
    assert type(deny_response['policyDocument']['Statement']) is list
    assert deny_response['policyDocument']['Statement'][0]['Action'] == 'execute-api:Invoke'
    assert deny_response['policyDocument']['Statement'][0]['Effect'] == 'Deny'
    assert deny_response['policyDocument']['Statement'][0]['Resource'] == invalid_test_event['methodArn']

    incomplete_test_event = {
        "type":"TOKEN",
        "methodArn":"arn:aws:execute-api:test-region:test-account:test-resource"
    }
    response_403 = authorizer.validate_token(incomplete_test_event, "", ssm_client, tname)
    assert type(response_403) is dict
    assert response_403['statusCode'] == 403

