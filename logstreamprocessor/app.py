import base64
import json
import logging
import os
import time
import zlib

import boto3
from boto3.dynamodb.conditions import Attr, Key


def lambda_handler(event, context):
    logging.getLogger().setLevel(logging.INFO)
    logging.info("Received event: " + json.dumps(event, indent=2))
    encoded_payload = zlib.decompress(base64.b64decode(event['awslogs']['data']), 16 + zlib.MAX_WBITS)
    payload = json.loads(encoded_payload.decode('utf-8'))
    logging.info('Decoded logs: ' + json.dumps(payload, indent=2))

    # Connect to DynamoDB, the table 'log_messages' is used to dedup messages and avoid being spammed by SNS
    region = context.invoked_function_arn.split(":")[3]
    logging.info("Using region: {}".format(region))

    try:
        dynamodb = boto3.resource('dynamodb', region_name=region)
        # TODO Generate the table name at stack creation
        table = dynamodb.Table('log_messages')

        messages = []
        for log_event in payload['logEvents']:
            message = log_event['message']
            # TODO Make time period size configurable
            response = table.query(
                KeyConditionExpression=Key('message').eq(message),
                # Filter out messages that have been alerted in the last 24 hours, 'last_alerted_time' is an integer
                FilterExpression=Attr('last_alerted_time').gt(int(time.time()) - 86400)
            )
            if response['Count'] == 0:
                logging.info(f'New message \'{message}\'')
                messages.append(message)
                # Insert new message into DynamoDB
                table.put_item(
                    Item={
                        'message': message,
                        'last_alerted_time': int(time.time())
                    }
                )
            else:
                logging.info(f'Message \'{message}\' already alerted, skipping it')
                # Update last alerted time in DynamoDB
                table.update_item(
                    Key={'message': message},
                    UpdateExpression='SET last_alerted_time = :t',
                    ExpressionAttributeValues={':t': int(time.time())}
                )

        if messages:
            # Send SNS notification for new error messages
            # TODO Try to include a link to the messages themselves in CloudWatch Logs
            sns = boto3.client('sns')
            topic_arn = os.environ['SNS_TOPIC_ARN']
            subject = 'New log stream event'
            sns.publish(TopicArn=topic_arn, Subject=subject, Message='\n'.join(messages))
    except Exception as e:
        logging.error(f'Error processing log stream event: {e}')
        return {
            'statusCode': 500,
            'body': f'Error processing log stream event: {e}'
        }

    return {
        'statusCode': 200,
        'body': f'Log stream event processed.'
    }
