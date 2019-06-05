import os
import logging
import boto3
import threading
import queue

from botocore.exceptions import ClientError
from flask_restful import Resource, reqparse
from flask_cognito import cognito_auth_required

from yoki.resources.deployment import Deployment
from yoki.resources.scale import Scale


log = logging.getLogger()
log.setLevel(os.getenv('LOG_LEVEL', logging.INFO))


DYNAMODB_TABLE_PREFIX = os.getenv('DYNAMODB_TABLE_PREFIX', 'dev-')


class ServiceGroup(Resource):
    dynamodb = boto3.resource('dynamodb')
    table_name = DYNAMODB_TABLE_PREFIX + 'yoki-service-groups'
    table = dynamodb.Table(table_name)

    parser = reqparse.RequestParser()
    parser.add_argument('services',
                        type=str,
                        action='append',
                        required=True,
                        help='Services cannot be blank.'
                        )

    @cognito_auth_required
    def get(self, group):
        return self.get_group(group)

    @cognito_auth_required
    def post(self, group):
        data = self.parser.parse_args()
        res = self.update_group(group, data)
        return res

    @cognito_auth_required
    def delete(self, group):
        return self.delete_group(group)

    def get_group(self, group):
        try:
            params = {
                'Key': {'group': group},
            }
            return {'serviceGroup': self.table.get_item(**params)['Item']}
        except KeyError:
            return {'message': f'Group not found: {group}'}, 404
        except ClientError as e:
            log.error(f'[{self.__class__.__name__}] {e}')
            return {'message': 'Error getting item.'}, 500

    def update_group(self, group, services: dict):
        item = {'group': group}
        item.update(services)
        try:
            self.table.put_item(Item=item)
            return {'serviceGroup': item}
        except ClientError as e:
            log.error(f'[{self.__class__.__name__}] {e}')
            return {'message': 'Error saving item.'}, 500

    def delete_group(self, group):
        try:
            self.table.delete_item(Key={'group': group})
            return {'message': 'Item deleted.'}
        except ClientError as e:
            log.error(f'[{self.__class__.__name__}] {e}')
            return {'message': 'Error deleting item.'}, 500


class ServiceGroupList(Resource):
    dynamodb = boto3.resource('dynamodb')
    table_name = DYNAMODB_TABLE_PREFIX + 'yoki-service-groups'
    table = dynamodb.Table(table_name)

    @cognito_auth_required
    def get(self):
        return self.get_groups()

    def get_groups(self):
        try:
            return {'serviceGroups': self.table.scan()['Items']}
        except ClientError as e:
            log.error(f'[{self.__class__.__name__}] {e}')
            return {'message': 'Error getting items.'}, 500


class ServiceGroupDeploy(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('tags',
                        type=dict,
                        required=True,
                        help='Tags cannot be blank.')

    @cognito_auth_required
    def post(self, cluster, group):
        data = self.parser.parse_args()
        return self.deploy_service_group(cluster, group, data)

    def deploy_service_group(self, cluster, group, data):
        sg = ServiceGroup()
        res = sg.get_group(group)

        if isinstance(res, tuple):
            return res[0]

        services = res['serviceGroup']['services'][0].split()
        messages = self.bulk_create_deployment(cluster, services, data)
        return {'messages': messages}

    def bulk_create_deployment(self, cluster, services: list, tags: dict):
        q = queue.Queue()
        threads = []
        d = Deployment()

        for service in services:
            t = threading.Thread(target=self.create_deployment,
                                 args=(d, cluster, service, tags, q))
            t.start()
            threads.append(t)

        [t.join() for t in threads]
        return [q.get(t) for t in threads]

    def create_deployment(self, d: Deployment, cluster, service, tags: dict,
                          q: queue):
        res = d.create_deployment(cluster, service, tags)
        q.put(res)


class ServiceGroupScale(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('count',
                        type=int,
                        required=True,
                        help='Count cannot be blank.'
                        )

    @cognito_auth_required
    def post(self, cluster, group):
        data = self.parser.parse_args()
        return self.scale_service_group(cluster, group, data)

    def scale_service_group(self, cluster, group, data):
        sg = ServiceGroup()
        res = sg.get_group(group)

        if isinstance(res, tuple):
            return res[0]

        services = res['serviceGroup']['services'][0].split()
        messages = self.bulk_scale_service(cluster, services, data)
        return {'messages': messages}

    def bulk_scale_service(self, cluster, services: list, count: int):
        q = queue.Queue()
        threads = []
        scl = Scale()

        for service in services:
            t = threading.Thread(target=self.scale_service,
                                 args=(scl, cluster, service, count, q))
            t.start()
            threads.append(t)

        [t.join() for t in threads]
        return [q.get(t) for t in threads]

    def scale_service(self, scl: Scale, cluster, service, count: int,
                      q: queue):
        res = scl.scale_service(cluster, service, count)
        q.put(res)
