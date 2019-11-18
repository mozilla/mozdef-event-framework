import boto3
import json
import logging
import os
import gzip
import base64
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all


REGION = os.getenv('REGION', 'us-west-2')
service = os.getenv('SERVICE', 'default')
prefix = os.getenv('LOG_HANDLER_PREFIX', '/aws/lambda')
log_handler = os.getenv('LOG_HANDLER_FUNCTION', 'default')
log_handler_role = os.getenv('LOG_HANDLER_ROLE', 'IamRoleLambdaExecution')
sqs = boto3.client('sqs', region_name=REGION)
ssm = boto3.client('ssm', region_name=REGION)
cw_logs = boto3.client('logs')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

patch_all()


def lambda_handler(event, context, sqs_client = boto3.client('sqs', region_name=REGION), sqs_url=os.getenv('SQS_URL')):
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

def logs_handler(event, context):
    print(event)
    cw_data = event['awslogs']['data']
    print(cw_data)

    compressed_payload = base64.b64decode(cw_data)
    uncompressed = gzip.decompress(compressed_payload)
    payload = json.loads(uncompressed)

    # This is where we would send to SQS instead
    # or maybe an S3 bucket?
    log_events = payload['logEvents']
    for log_event in log_events:
        print(log_event)

def subscribe_to_logs_handler(event, context):
    print(event)
    # Need to wrap this in try - except
    logGroupName = event['detail']['requestParameters']['logGroupName']
    # print(logGroupName)

    if prefix and prefix not in logGroupName:
        pass
        # logger.warning("ignoring the log group {}, because it does not match the prefix {}".format(logGroupName, prefix))
    else:
        print(logGroupName)
        subscribe(logGroupName)
        logger.info("Subscribed {} to {}".format(logGroupName, log_handler))

def subscribe(log_group_name):
    cw_logs.put_subscription_filter(
       destinationArn=log_handler,
       logGroupName=log_group_name,
       filterName='ship-logs-to-SQS',
       filterPattern='*',
    )
