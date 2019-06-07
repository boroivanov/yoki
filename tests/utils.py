import pytest
import json
import boto3

from tests.seed import task_digest_items


class TestMixin(object):
    '''
    Automatically load in a client.
    '''
    @pytest.fixture(autouse=True)
    def set_common_fixtures(self, client):
        self.client = client

        auth_request = self.client.post('/auth', data=json.dumps({
            'username': 'test1234@example.com',
            'password': 'bn80Zd7Hj$rFCsdWK%gl0B7#w'
        }), headers={'Content-Type': 'application/json'})

        self.auth_header = "Bearer {}".format(
            json.loads(auth_request.data)['access_token'])

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('test-yoki-ECSTaskDigest')
        for item in task_digest_items:
            table.put_item(Item=item)
