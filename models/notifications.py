import os
import boto3
import time
import logging


DYNAMODB_TABLE_PREFIX = os.getenv('DYNAMODB_TABLE_PREFIX', 'dev-')

log = logging.getLogger()
log.setLevel(os.getenv('LOG_LEVEL', logging.INFO))


class Notifications(object):
    table_name = DYNAMODB_TABLE_PREFIX + 'yoki-notifications'

    def __init__(self, region, deployment_id, slack_ts='locked'):
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.deployment_id = deployment_id
        self.slack_ts = slack_ts
        self.ttl = os.getenv('TTL', 2592000)

    def table(self):
        return self.dynamodb.Table(self.table_name)

    def as_dict(self):
        return {
            'deployment': self.deployment_id,
            'slack_ts': self.slack_ts,
            'TTL': int(time.time()) + int(self.ttl),
        }

    def get_item(self):
        try:
            res = self.table().get_item(Key={'deployment': self.deployment_id})
            return res['Item']
        except KeyError:
            return None

    def put_item(self):
        return self.table().put_item(
            Item=self.as_dict()
        )
