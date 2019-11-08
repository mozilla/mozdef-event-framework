import json
import pytest
import boto3
import os
from moto import mock_sqs


@pytest.fixture(scope='function')
def aws_credentials():
    # Mocked AWS Credentials for moto, this is required 
    # as per their readme: https://github.com/spulec/moto
    os.environ['AWS_ACCESS_KEY_ID'] = 'testing'
    os.environ['AWS_SECRET_ACCESS_KEY'] = 'testing'
    os.environ['AWS_SECURITY_TOKEN'] = 'testing'
    os.environ['AWS_SESSION_TOKEN'] = 'testing'

@pytest.fixture(scope='function')
def sqs(aws_credentials):
    mock = mock_sqs()
    mock.start()

    sqs_client = boto3.client('sqs', 'us-west-2')
    queue_name = "test-resource-queue"
    queue_url = sqs_client.create_queue(
        QueueName=queue_name
    )['QueueUrl']

    yield (sqs_client, queue_url)
    mock.stop()

def test_lambda_handler(sqs):
    sqs_client, queue_url = sqs
    test_zoom_event = {
        "event": "user.created",
        "payload": {
            "account_id": "TEST",
            "operator": "john.doe@example.com",
            "creation_type": "create",
            "object": {
                "id": "abcD3ojfdbjfg",
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "type": "3"
            }
        }
    }
    # Taken from https://serverless.com/framework/docs/providers/aws/events/apigateway/#example-lambda-event-before-customization,
    # but slightly modified
    test_api_event = {
        "body": json.dumps(test_zoom_event),
        "method": "POST",
        "principalId": "",
        "stage": "dev",
        "cognitoPoolClaims": {
            "sub": ""
        },
        "enhancedAuthContext": {},
        "headers": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4",
            "Authorization": "TEST AUTHORIZATION HEADER",
            "CloudFront-Forwarded-Proto": "https",
            "CloudFront-Is-Desktop-Viewer": "true",
            "CloudFront-Is-Mobile-Viewer": "false",
            "CloudFront-Is-SmartTV-Viewer": "false",
            "CloudFront-Is-Tablet-Viewer": "false",
            "CloudFront-Viewer-Country": "US",
            "Host": "1234567890.execute-api.us-east-1.amazonaws.com",
            "upgrade-insecure-requests": "1",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "Via": "2.0 f165ce34daf8c0da182681179e863c24.cloudfront.net (CloudFront)",
            "X-Amz-Cf-Id": "l06CAg2QsrALeQcLAUSxGXbm8lgMoMIhR2AjKa4AiKuaVnnGsOFy5g==",
            "X-Amzn-Trace-Id": "Root=1-5970ef20-3e249c0321b2eef14aa513ae",
            "X-Forwarded-For": "94.117.120.169, 116.132.62.73",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https"
        },
        "query": {},
        "path": {},
        "identity": {
            "cognitoIdentityPoolId": "",
            "accountId": "",
            "cognitoIdentityId": "",
            "caller": "",
            "apiKey": "",
            "sourceIp": "94.197.120.169",
            "accessKey": "",
            "cognitoAuthenticationType": "",
            "cognitoAuthenticationProvider": "",
            "userArn": "",
            "userAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            "user": ""
        },
        "stageVariables": {},
        "requestPath": "/request/path"
    }

    from functions import handler
    response_200 = handler.lambda_handler(test_api_event, "", sqs_client, queue_url)

    assert type(response_200) is dict
    assert response_200['statusCode'] == 200
    # More assertions here for the message sent to SQS
    sqs_response = sqs_client.receive_message(QueueUrl=queue_url)
    message_for_mozdef = json.loads(sqs_response['Messages'][0]['Body'])
    assert type(message_for_mozdef) is dict
    assert message_for_mozdef['source'] == 'api_aws_lambda'
    assert 'summary' in message_for_mozdef
    assert 'category' in message_for_mozdef
    assert 'details' in message_for_mozdef
    if os.getenv('SERVICE'):
         assert message_for_mozdef['eventsource'] == '{}_api'.format(os.getenv('SERVICE'))
    else:
        assert message_for_mozdef['eventsource'] == 'default_api'
    assert message_for_mozdef['details'] == test_zoom_event

    invalid_api_event = test_api_event.copy()
    invalid_api_event.pop('body')
    with pytest.raises(KeyError):
        response_400 = handler.lambda_handler(invalid_api_event, "", sqs_client, queue_url)
        assert type(response_400) is dict
        assert response_400['statusCode'] == 400

    invalid_zoom_event = test_zoom_event.copy()
    invalid_zoom_event.pop('payload')
    test_api_event.update({'body': json.dumps(invalid_zoom_event)})
    response_400 = handler.lambda_handler(test_api_event, "", sqs_client, queue_url)
    assert type(response_400) is dict
    assert response_400['statusCode'] == 400