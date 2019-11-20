import json
import pytest
import boto3
import os
import time
from moto import mock_sqs, mock_logs


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
def sqs(aws_credentials):
    mock = mock_sqs()
    mock.start()

    sqs_client = boto3.client('sqs', 'us-west-2')
    queue_name = "test-logs-queue"
    queue_url = sqs_client.create_queue(
        QueueName=queue_name
    )['QueueUrl']

    yield (sqs_client, queue_url)
    mock.stop()

@pytest.fixture(scope='function')
def logs(aws_credentials):
    mock = mock_logs()
    mock.start()

    logs_client = boto3.client('logs')

    yield logs_client
    mock.stop()

def test_handler(sqs):
    sqs_client, queue_url = sqs
    test_cwlog = {
        "awslogs": {
            "data": "H4sIABy01F0C/52Tb2vbMBDGv4oRe7cmkSzLlvMusLQU2jCWwGB1CYp9a8Ucy8hKui7ku1fnP02ywRgzBqN7Ht2d7icfyBaaRj3B6rUGMg3Ip9lqtr6fL5ezmzm5Coh5qcCikJ49KJTm6caaXY3aRL00k1JtN4WaOGjcqAG71zn0vqWzoLZoDClLJ1ROwnjy8OFutpovV4+FUCqKNrFKQUbAZLoJVb5JOFAuUx6GmKTZbZrc6tppU13r0oFtfLoHctfW7PKvsfL6e6uSx67yfA+Va60HogvsgHPBRSQjkYZciCgSsX9DEScx45JGkeQ0pqnkMqLemYRUSBGFVGIXTvthObXFMzNBeSI540lKU6/1Y8QSh4yoJkdz5pdZe+gRY6OQriidMj4V9NtH6p/MJ81IpQajNcZ1sdqa3CdcvEv3Slefu2Dn8OeE0061c8/G6l9gx/Vrb9hV+Wn/XpW6UA7WzvyAqnOUsIfylOPr7MvidnHTa7qCyqAgE1xvTbEr/yjWed2zH39x2euqjXV6P5pOvK1yYy3kLhjSKIQatH0FXgC9h+IqKKypa109BYAIx32lAcA/DfbZNO50PBan41BEY8b8N83IMauQKfx0VuUOimsNZYFX5TDQGy7sqYSQU8G6ErgXk6MJueH6jBqGz5ihOhBD6YJXK/a0ULxk1f5DAymUe05tvKXUQ+oZXaZvr+07n6Grjg65vLb/Seb3H+PvIxuYoHEgwtlYCnI8Ph7fAFefEKmOBAAA"
        }
    }
    from functions import log_handler
    # This function does not return anything, wait before checking queue
    log_handler.handler(test_cwlog, "", sqs_client, queue_url)
    time.sleep(2)
    # Now check our queue content
    response = sqs_client.receive_message(QueueUrl=queue_url)
    log_message = response['Messages'][0]['Body']
    assert type(log_message) is str
    log_message_dict = json.loads(log_message)
    assert 'asctime' in log_message_dict
    assert 'name' in log_message_dict
    assert 'processName' in log_message_dict
    assert 'filename' in log_message_dict
    assert 'funcName' in log_message_dict
    assert 'levelname' in log_message_dict
    assert 'lineno' in log_message_dict
    assert 'module' in log_message_dict
    assert 'threadName' in log_message_dict
    assert 'message' in log_message_dict
    assert 'timestamp' in log_message_dict
    assert 'hostname' in log_message_dict

def test_subscribe_to_log_handler(logs):
    logs_client = logs
    test_cloudtrail_cw_event = {
        "version": "0",
        "id": "52d15c46-1bbc-47da-84e4-cef8c4dfc5b7",
        "detail-type": "AWS API Call via CloudTrail",
        "source": "aws.logs",
        "account": "TEST",
        "time": "2019-08-20T18:50:54Z",
        "region": "us-west-2",
        "resources": [],
        "detail": {
            "eventVersion": "1.04",
            "userIdentity": {
                "type": "IAMUser",
                "principalId": "AIDAIP5G4Z37ZNNNKVEUW",
                "arn": "arn:aws:iam::xxx:user/test",
                "accountId": "TEST",
                "accessKeyId": "TEST",
                "userName": "test",
                "sessionContext": {
                    "attributes": {
                        "mfaAuthenticated": "false",
                        "creationDate": "2017-08-20T18:50:48Z"
                    }
                },
                "invokedBy": "cloudformation.amazonaws.com"
            },
        "eventTime": "2017-08-20T18:50:54Z",
        "eventSource": "logs.amazonaws.com",
        "eventName": "CreateLogGroup",
        "awsRegion": "us-west-2",
        "sourceIPAddress": "cloudformation.amazonaws.com",
        "userAgent": "cloudformation.amazonaws.com",
        "requestParameters": {
            "logGroupName": "/aws/lambda/test-service"
        },
        "responseElements": None,
        "requestID": "7f14f744-85d8-11e7-b277-a3957840b2c0",
        "eventID": "ddcd560b-b39e-4991-8e2b-e39fd8d7dabf",
        "eventType": "AwsApiCall",
        "apiVersion": "20140328"
        }
    }
    from functions import log_handler
    response = log_handler.subscribe_to_log_handler(test_cloudtrail_cw_event, "", logs_client)
    # NOTE: This SHOULD return True, however at the moment moto cannot mock
    # the CloudWatch "subscribe_to_log_handler" API, therefore expecting False
    assert response is False
