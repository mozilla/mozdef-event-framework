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
    api_event = event
    returnDict = dict()
    returnDict['details'] = {}

    # See if submitted POST body is a valid JSON and has
    #  a "payload" since this is common in webhook data
    try:
        message = json.loads(api_event['body'])
    except Exception as e:
        logger.error("Cannot parse API event: {}, context: {}, exception: ".format(
            str(api_event['body']),
            context.function_name, e)
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
        'processid': 'none',
        'severity': 'INFO',
        'summary': '{}_event'.format(service),
        'category': service,
        'source': 'api_aws_lambda',
        'eventsource': service + '_api',
        'tags': [
            service
        ],
        'details': message
    }

    # returnDict['summary'] = '{}_event'.format(service)
    # returnDict['source'] = 'api_aws_lambda'
    # returnDict['category'] = service
    # returnDict['eventsource'] = service + '_api'
    # returnDict['hostname'] = '{}_host'.format(service)
    # returnDict['tags'] = [ service ]
    # returnDict['processname'] = service
    # returnDict['processid'] = 'none'
    # returnDict['severity'] = 'INFO'
    # returnDict['details'] = message

    queueURL = os.getenv('SQS_URL')
    sqs.send_message(QueueUrl=queueURL, MessageBody=json.dumps(returnDict))
    logger.info("Event added to the resource queue.")

    return {
        'statusCode': 200,
        'body': json.dumps('Event received')
    }
