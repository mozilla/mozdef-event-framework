import boto3
import json
import logging
import os

REGION = os.getenv('REGION', 'us-west-2')
service = os.getenv('efServiceName', 'default')
sqs = boto3.client('sqs', region_name=REGION)
ssm = boto3.client('ssm', region_name=REGION)
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    # This parsing can and will be improved in another PR
    if 'requestBody' in event['body']:
        returnDict = dict()
        returnDict['details'] = {}
        event = json.loads(event['body'])
        event_body = event['requestBody']
        if 'event' not in event_body or 'payload' not in event_body:
            return {
                'statusCode': 400,
                'body': json.dumps('Bad Request')
            }

        returnDict['summary'] = event_body['event']
        returnDict['source'] = 'api_aws_lambda'
        returnDict['category'] = service
        returnDict['eventsource'] = service + '_api'
        returnDict['hostname'] = 'marketplace.'+ service + '.us'
        returnDict['tags'] = service
        returnDict['processname'] = service + 'connect'
        returnDict['processid'] = 'none'
        returnDict['severity'] = 'INFO'

        if 'payload' in event_body:
            if 'account_id' in event_body['payload']:
                returnDict['details']['account_id'] = event_body['payload']['account_id']
            if 'operator' in event_body['payload']:
                returnDict['details']['operator'] = event_body['payload']['operator']
            if 'operator_id' in event_body['payload']:
                returnDict['details']['operator_id'] = event_body['payload']['operator_id']
            if 'object' in event_body['payload']:
                if 'id' in event_body['payload']['object']:
                    returnDict['details']['id'] = event_body['payload']['object']['id']
                if 'owner_id' in event_body['payload']['object']:
                    returnDict['details']['owner_id'] = event_body['payload']['object']['owner_id']
                if 'owner_email' in event_body['payload']['object']:
                    returnDict['details']['owner_email'] = event_body['payload']['object']['owner_email']

        queueURL = os.getenv('SQS_URL')   # Obtaining the queue as environment variable
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
