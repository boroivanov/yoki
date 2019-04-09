import os
import boto3
import time
import logging


log = logging.getLogger()
log.setLevel(os.getenv('LOG_LEVEL', logging.INFO))

DYNAMODB_TABLE_PREFIX = os.getenv('DYNAMODB_TABLE_PREFIX', 'dev-')


class EcsEvent(object):
    instance_state_table = 'yoki-ECSInstanceState'
    task_state_table = 'yoki-ECSTaskState'

    def __init__(self, event, region):
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.event = event
        self.table_name = self.table_name()
        self.id_name = self.id_name()
        self.event_id = self.event_id()
        self.state_item_ttl = os.getenv('STATE_ITEM_TTL', 86400)

    def table(self):
        return self.dynamodb.Table(self.table_name)

    def table_name(self):
        if self.instance_state_change():
            return DYNAMODB_TABLE_PREFIX + self.instance_state_table
        return DYNAMODB_TABLE_PREFIX + self.task_state_table

    def id_name(self):
        if self.instance_state_change():
            return 'containerInstanceArn'
        return 'taskArn'

    def event_id(self):
        if self.instance_state_change():
            return self.event['detail']['containerInstanceArn']
        return self.event['detail']['taskArn']

    def instance_state_change(self):
        state = 'ECS Container Instance State Change'
        return self.event['detail-type'] == state

    def needs_updating(self):
        saved_event = self.get_item(self.id_name, self.event_id)
        if 'Item' not in saved_event:
            return True
        return saved_event['Item']['version'] < self.event['detail']['version']

    def as_dict(self):
        event = {}
        event['cw_version'] = self.event['version']
        event.update(self.event['detail'])
        # event['current_status'] = self.event['status']
        # event.pop('status')
        ttl = int(time.time()) + int(self.state_item_ttl)
        event['TTL'] = ttl
        return event

    def get_item(self, key, value):
        return self.table().get_item(Key={key: value})

    def put_item(self, ttl):
        if self.needs_updating():
            log.info('Received event is more recent version than '
                     'stored event - updating')
            return self.table().put_item(
                Item=self.as_dict()
            )

        log.info('Received event is an older version than '
                 'stored event - ignoring')
        return None
