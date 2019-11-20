import boto3
import json
import logging
import os
import sys
import socket
import gzip
import base64
import cis_logger    # Custom module
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.core import patch_all


REGION = os.getenv('REGION', 'us-west-2')
service = os.getenv('SERVICE', 'default')
prefix = os.getenv('LOG_HANDLER_PREFIX', '/aws/lambda')
log_handler = os.getenv('LOG_HANDLER_FUNCTION', 'default')
log_handler_arn = os.getenv('LOG_HANDLER_FUNCTION_ARN', 'default')
cw_logs = boto3.client('logs')
sqs = boto3.client('sqs', region_name=REGION)

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

def handler(event, context, sqs_client = boto3.client('sqs', region_name=REGION), sqs_url=os.getenv('LOGS_SQS_URL')):
    logger = setup_logging()
    queueURL = sqs_url

    try:
        cw_data = event['awslogs']['data']
        compressed_payload = base64.b64decode(cw_data)
        uncompressed = gzip.decompress(compressed_payload)
        payload = json.loads(uncompressed)
    except Exception as e:
        logger.error("Cannot parse CloudWatch log event, exception: {}".format(e))
    # This is where we would send to SQS instead
    # or maybe an S3 bucket?
    log_events = payload['logEvents']
    for log_event in log_events:
        sqs_client.send_message(QueueUrl=queueURL, MessageBody=log_event['message'].strip('\n'))
    
    logger.info("Log messages added to the logs queue.")

def subscribe_to_log_handler(event, context, cw_logs_client=boto3.client('logs')):
    logger = setup_logging()
    suffix = log_handler
    try:
        log_group_name = event['detail']['requestParameters']['logGroupName']
        # Cannot subscribe logs for the same function to itself, so ignoring suffix
        # We only want to subscribe to logs that are WARNING or ERROR level
        if prefix and suffix and prefix in log_group_name and suffix not in log_group_name:
            try:
                cw_logs_client.put_subscription_filter(
                    destinationArn=log_handler_arn,
                    logGroupName=log_group_name,
                    filterName='ship-logs-to-SQS',
                    filterPattern='{ $.levelname = "WARNING" || $.levelname = "ERROR" }'
                )
                logger.info("Subscribed {} to {}".format(log_group_name, log_handler_arn))
                return True
            except Exception as e:
                logger.warning("Failed to subscribe log group {}, exception: {}".format(log_group_name, e))
                return False

    except Exception as e:
        # We do not care about events that has a missing log group name
        return False
