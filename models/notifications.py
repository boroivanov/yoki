import os
import boto3
import time
import logging


DYNAMODB_TABLE_PREFIX = os.getenv('DYNAMODB_TABLE_PREFIX', 'dev-')

log = logging.getLogger()
log.setLevel(os.getenv('LOG_LEVEL', logging.INFO))


class Notifications(object):
    table_name = DYNAMODB_TABLE_PREFIX + 'yoki-notifications'

    def __init__(self, deployment, slack_ts=None,
                 cmd_response_url=None, cmd_channel_id=None, cmd_ts=None,
                 cmd_username=None, TTL=None):
        self.dynamodb = boto3.resource('dynamodb')
        self.deployment = deployment
        self.slack_ts = slack_ts
        self.cmd_username = cmd_username
        self.cmd_response_url = cmd_response_url
        self.cmd_channel_id = cmd_channel_id
        self.cmd_ts = cmd_ts
        self.ttl = os.getenv('NOTIFICATION_ITEM_TTL', 2592000)

    def table(self):
        return self.dynamodb.Table(self.table_name)

    def as_dict(self):
        item = {
            'deployment': self.deployment,
            'TTL': int(time.time()) + int(self.ttl),
        }
        if self.cmd_username:
            item['cmd_username'] = self.cmd_username
        if self.slack_ts:
            item['slack_ts'] = self.slack_ts
        if self.cmd_response_url:
            item['cmd_response_url'] = self.cmd_response_url
        if self.cmd_channel_id:
            item['cmd_channel_id'] = self.cmd_channel_id
        if self.cmd_ts:
            item['cmd_ts'] = self.cmd_ts
        return item

    def get_item(self):
        try:
            res = self.table().get_item(Key={'deployment': self.deployment})
            return res['Item']
        except KeyError:
            return None

    def put_item(self):
        return self.table().put_item(
            Item=self.as_dict()
        )
