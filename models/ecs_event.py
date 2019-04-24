import os
import boto3
import time
import logging

from botocore.exceptions import ClientError


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


class EcsEventTaskDigest(object):
    table_name = DYNAMODB_TABLE_PREFIX + 'yoki-ECSTaskDigest'

    def __init__(self, event, region):
        self.dynamodb = boto3.resource('dynamodb', region_name=region)
        self.ecs = boto3.client('ecs', region_name=region)
        self.event = event
        self.event_detail = event['detail']
        self.digest_item_ttl = os.getenv('DIGEST_ITEM_TTL', 2592000)

    def table(self):
        return self.dynamodb.Table(self.table_name)

    def td_arn(self):
        return self.event_detail['taskDefinitionArn']

    def describe_service(self):
        response = self.ecs.describe_services(
            cluster=self.cluster(),
            services=[self.service()]
        )
        return response['services'][0]

    def describe_deployment_counts(self):
        for deployment in self.describe_service()['deployments']:
            if deployment['id'] == self.deployment():
                return {
                    'desiredCount': deployment['desiredCount'],
                    'pendingCount': deployment['pendingCount'],
                    'runningCount': deployment['runningCount'],
                }
        return {'desiredCount': 0, 'pendingCount': 0, 'runningCount': 0}

    def describe_task_definition(self):
        try:
            res = self.ecs.describe_task_definition(
                taskDefinition=self.td_arn()
            )
        except ClientError as e:
            log.warning(e.response['Error']['Message'])
            raise
        return res['taskDefinition']

    def cluster(self):
        return self.event_detail['clusterArn'].split('/')[-1]

    def service(self):
        return self.event_detail['group'].split(':')[-1]

    def task_definition(self):
        return self.event_detail['taskDefinitionArn'].split('/')[-1]

    def task_id(self):
        return self.event_detail['taskArn'].split('/')[-1]

    def images(self):
        containers = self.describe_task_definition()['containerDefinitions']
        return [c['image'].split('/')[-1] for c in containers]

    def deployment(self):
        return self.event_detail['startedBy']

    def as_dict(self):
        counts = self.describe_deployment_counts()
        item = {
            'TTL': int(time.time()) + int(self.digest_item_ttl),
            'deployment': self.event_detail['startedBy'],
            'cluster': self.cluster(),
            'service': self.service(),
            'definition': self.task_definition(),
            'tasks': {
                self.task_id(): self.event_detail['lastStatus']
            },
            'updatedAt': self.event_detail['updatedAt'],
            'createdAt': self.event_detail['createdAt'],
            'images': self.images(),
            'launchType': self.event_detail['launchType'],
        }
        return {**item, **counts}

    def get_item(self, key, value):
        try:
            res = self.table().get_item(Key={key: value})
            return res['Item']
        except KeyError:
            return None

    def put_item(self, ttl):
        item = self.get_item('deployment', self.deployment())

        if item:
            log.info(f'Updating digest for {self.deployment()}.')
            item['tasks'][self.task_id()] = self.event_detail['lastStatus']
            item.update(self.describe_deployment_counts())
        else:
            log.info(f'Creating a new digest for {self.deployment()}.')
            item = self.as_dict()

        return self.table().put_item(
            Item=item
        )
