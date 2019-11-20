import boto3
import json
import logging
import os
import sys
import socket
import cis_logger    # Custom module
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all


REGION = os.getenv('REGION', 'us-west-2')
service = os.getenv('SERVICE', 'default')
sqs = boto3.client('sqs', region_name=REGION)
ssm = boto3.client('ssm', region_name=REGION)
# logger = logging.getLogger()
# logger.setLevel(logging.INFO)

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


def lambda_handler(event, context, sqs_client = boto3.client('sqs', region_name=REGION), sqs_url=os.getenv('EVENT_SQS_URL')):
    logger = setup_logging()
    # This parsing can and will be improved in the future
    logger.info("{} service initialized.".format(service))
    api_event = event
    returnDict = dict()
    returnDict['details'] = {}

    # See if submitted POST body is a valid JSON and has
    # a "payload" since this is common in webhook data
    try:
        message = json.loads(api_event['body'])
    except Exception as e:
        logger.error("Cannot parse API event: {}, exception: {}".format(
            str(api_event['body']), e)
        )
        return {
                'statusCode': 400,
                'body': json.dumps('Bad Request')
        }
    if 'payload' not in message.keys():
        logger.error("Expecting a payload for the event, but not found.")
        return {
                'statusCode': 400,
                'body': json.dumps('Bad Request')
        }

    returnDict = {
        'hostname': '{}_host'.format(service),
        'processname': service,
        'summary': '{}_event'.format(service),
        'category': service,
        'source': 'api_aws_lambda',
        'eventsource': service + '_api',
        'tags': [
            service
        ],
        'details': message
    }

    queueURL = sqs_url
    sqs_client.send_message(QueueUrl=queueURL, MessageBody=json.dumps(returnDict))
    logger.info("Event added to the resource queue.")

    return {
        'statusCode': 200,
        'body': json.dumps('Event received')
    }
