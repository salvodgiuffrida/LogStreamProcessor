import unittest
from unittest.mock import MagicMock, patch
import os

from logstreamprocessor.app import lambda_handler


def context():
    context = MagicMock()
    context.invoked_function_arn = 'arn:aws:lambda:us-east-1:111111111:function:my-function:prod'
    return context


def event():
    return {
        "awslogs": {
            "data": "H4sIAAAAAAAAAHWPwQqCQBCGX0Xm7EFtK+smZBEUgXoLCdMhFtKV3akI8d0bLYmibvPPN3wz00CJxmQnTO41whwWQRIctmEcB6sQbFC3CjW3XW8kxpOpP+OC22d1Wml1qZkQGtoMsScxaczKN3plG8zlaHIta5KqWsozoTYw3/djzwhpLwivWFGHGpAFe7DL68JlBUk+l7KSN7tCOEJ4M3/qOI49vMHj+zCKdlFqLaU2ZHV2a4Ct/an0/ivdX8oYc1UVX860fQDQiMdxRQEAAA=="
        }
    }


class TestLambdaHandler(unittest.TestCase):

    @patch.dict(os.environ, {'SNS_TOPIC_ARN': 'test-sns-topic-arn'})
    @patch('boto3.client')
    @patch('boto3.resource')
    @patch('time.time', return_value=1620583500)
    def test_lambda_handler_new_message(self, mock_time, mock_dynamodb_resource, mock_sns_client):
        table = MagicMock()
        mock_dynamodb_resource.return_value.Table.return_value = table
        table.query.return_value = {'Count': 0}
        sns = MagicMock()
        mock_sns_client.return_value = sns

        response = lambda_handler(event(), context())

        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], f'Log stream event processed.')

        # assert that the correct SNS message was published
        sns.publish.assert_called_with(
            TopicArn='test-sns-topic-arn',
            Subject='New log stream event',
            Message='[ERROR] First test message\n[ERROR] Second test message'
        )

        # assert that the message was added to DynamoDB table
        table.put_item.assert_any_call(
            Item={'message': '[ERROR] First test message', 'last_alerted_time': 1620583500})

        table.put_item.assert_any_call(
            Item={'message': '[ERROR] Second test message', 'last_alerted_time': 1620583500})

    @patch.dict(os.environ, {'SNS_TOPIC_ARN': 'test-sns-topic-arn'})
    @patch('boto3.client')
    @patch('boto3.resource')
    @patch('time.time', return_value=1620583500)
    def test_lambda_handler_message_already_exists(self, mock_time, mock_dynamodb_resource, mock_sns_client):
        # TODO Write additional tests using local DynamoDB instance instead of mock, if possible
        table = MagicMock()
        mock_dynamodb_resource.return_value.Table.return_value = table
        table.query.return_value = {'Count': 1}

        response = lambda_handler(event(), context())

        # assert that the response is correct
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], f'Log stream event processed.')

        # assert that the message was not added to DynamoDB table
        table.put_item.assert_not_called()

        # assert that no SNS message was published
        mock_sns_client.assert_not_called()

    # Test what happens when Dynamo throws an exception
    @patch.dict(os.environ, {'SNS_TOPIC_ARN': 'test-sns-topic-arn'})
    @patch('boto3.client')
    @patch('boto3.resource')
    @patch('time.time', return_value=1620583500)
    def test_lambda_handler_dynamo_exception(self, mock_time, mock_dynamodb_resource, mock_sns_client):
        table = MagicMock()
        mock_dynamodb_resource.return_value.Table.return_value = table
        table.query.side_effect = Exception('test exception')

        response = lambda_handler(event(), context())

        # assert that the response is correct
        self.assertEqual(response['statusCode'], 500)
        self.assertEqual(response['body'], 'Error processing log stream event: test exception')

        # assert that the message was not added to DynamoDB table
        table.put_item.assert_not_called()

        # assert that no SNS message was published
        mock_sns_client.assert_not_called()
