import boto3
import json
import logging
import os

REGION = os.getenv('REGION', 'us-west-2')
service = os.getenv('SERVICE', 'default')
sqs = boto3.client('sqs', region_name=REGION)
ssm = boto3.client('ssm', region_name=REGION)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # print(json.dumps(event))
    # This parsing can and will be improved in the future
    logger.info("{} service initialized.".format(service))
    aws_event = event
    returnDict = dict()
    returnDict['details'] = {}

    try:
        zoom_event = json.loads(aws_event['body'])
    except Exception as e:
        logger.error("Cannot parse event: {}, context: {}, exception: ".format(str(aws_event), context.function_name, e))
        return {
                'statusCode': 400,
                'body': json.dumps('Bad Request')
        }

    zoom_event = json.loads(aws_event['body'])
    if 'event' not in zoom_event or 'payload' not in zoom_event:
        logger.error("AWS event does not contain Zoom event data.")
        return {
            'statusCode': 400,
            'body': json.dumps('Bad Request')
        }

    returnDict['summary'] = zoom_event['event']
    returnDict['source'] = 'api_aws_lambda'
    returnDict['category'] = service
    returnDict['eventsource'] = service + '_api'
    # This is probably not very generic
    returnDict['hostname'] = 'marketplace.'+ service + '.us'
    returnDict['tags'] = service
    # So is this
    returnDict['processname'] = service + 'connect'
    returnDict['processid'] = 'none'
    returnDict['severity'] = 'INFO'

    # Parsing / validation from here is a sample only,
    # based on "meeting.started" Zoom event
    if 'payload' in zoom_event:
        if 'account_id' in zoom_event['payload']:
            returnDict['details']['account_id'] = zoom_event['payload']['account_id']
        if 'operator' in zoom_event['payload']:
            returnDict['details']['operator'] = zoom_event['payload']['operator']
        if 'operator_id' in zoom_event['payload']:
            returnDict['details']['operator_id'] = zoom_event['payload']['operator_id']
        if 'object' in zoom_event['payload']:
            if 'duration' in zoom_event['payload']['object']:
                returnDict['details']['duration'] = zoom_event['payload']['object']['duration']
            if 'start_date' in zoom_event['payload']['object']:
                returnDict['details']['start_date'] = zoom_event['payload']['object']['start_date']
            if 'timezone' in zoom_event['payload']['object']:
                returnDict['details']['timezone'] = zoom_event['payload']['object']['timezone']
            if 'topic' in zoom_event['payload']['object']:
                returnDict['details']['topic'] = zoom_event['payload']['object']['topic']
            if 'id' in zoom_event['payload']['object']:
                returnDict['details']['id'] = zoom_event['payload']['object']['id']
            if 'uuid' in zoom_event['payload']['object']:
                returnDict['details']['uuid'] = zoom_event['payload']['object']['uuid']
            if 'host_id' in zoom_event['payload']['object']:
                returnDict['details']['host_id'] = zoom_event['payload']['object']['host_id']

        queueURL = os.getenv('SQS_URL')
        sqs.send_message(QueueUrl=queueURL, MessageBody=json.dumps(returnDict))
        return {
            'statusCode': 200,
            'body': json.dumps('Event received')
        }
    else:
        # Not the expected event request format
        return {
            'statusCode': 400,
            'body': json.dumps('Bad Request')
        }
