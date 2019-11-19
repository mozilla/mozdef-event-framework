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
cw_logs = boto3.client('logs')
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

def handler(event, context):
    logger = setup_logging()
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
        print(log_event)

def subscribe_to_log_handler(event, context, cw_logs_client=boto3.client('logs')):
    logger = setup_logging()
    print(event)
    try:
        log_group_name = event['detail']['requestParameters']['logGroupName']
    except Exception as e:
        logger.warning("An unexpected CloudTrail event received, exception: {}".format(e))
    # print(log_group_name)

    if prefix and prefix in log_group_name:
        cw_logs.put_subscription_filter(
           destinationArn=log_handler,
           logGroupName=log_group_name,
           filterName='ship-logs-to-SQS',
           filterPattern='',
        )
        logger.info("Subscribed {} to {}".format(log_group_name, log_handler))