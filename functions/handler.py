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
        json.loads(aws_event['body'])
    except Exception as e:
        logger.error("Cannot parse event: {}, context: {}, exception: ".format(str(aws_event), context.function_name, e))
        return {
                'statusCode': 400,
                'body': json.dumps('Bad Request')
        }
    else:
        zoom_event = aws_event['body']
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

        if 'payload' in zoom_event:
            if 'account_id' in zoom_event['payload']:
                returnDict['details']['account_id'] = zoom_event['payload']['account_id']
            if 'operator' in zoom_event['payload']:
                returnDict['details']['operator'] = zoom_event['payload']['operator']
            if 'operator_id' in zoom_event['payload']:
                returnDict['details']['operator_id'] = zoom_event['payload']['operator_id']
            if 'object' in zoom_event['payload']:
                if 'id' in zoom_event['payload']['object']:
                    returnDict['details']['id'] = zoom_event['payload']['object']['id']
                if 'owner_id' in zoom_event['payload']['object']:
                    returnDict['details']['owner_id'] = zoom_event['payload']['object']['owner_id']
                if 'owner_email' in zoom_event['payload']['object']:
                    returnDict['details']['owner_email'] = zoom_event['payload']['object']['owner_email']

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
