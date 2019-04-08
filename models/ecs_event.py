import os
import boto3
import time
import logging


log = logging.getLogger()
log.setLevel(os.getenv('LOG_LEVEL', logging.INFO))


class EcsEvent(object):
    instance_state_table = 'ECSInstanceState'
    task_state_table = 'ECSTaskState'

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
            return self.instance_state_table
        return self.task_state_table

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
        return saved_event['Item']['version'] < self.event['detail']['version']

    def get_item(self, key, value):
        return self.table.get_item(Key={key: value})

    def put_item(self, item, ttl):
        if self.needs_updating():
            log.info('Received event is more recent version than '
                     'stored event - updating')
            ttl = int(time.time()) + int(self.state_item_ttl)
            item['TTL'] = ttl
            self.table.put_item(
                Item=item
            )
        else:
            log.info('Received event is more recent version than '
                     'stored event - ignoring')
