import os
import logging
import boto3
from botocore.exceptions import ClientError
from flask_restful import Resource, reqparse


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

    def get(self, group):
        try:
            params = {
                'Key': {'group': group},
            }
            return {'serviceGroup': self.table.get_item(**params)['Item']}
        except KeyError:
            return {'serviceGroup': 'Not found.'}, 404
        except ClientError as e:
            log.error(f'[{self.__class__.__name__}] {e}')
            return {'message': 'Error getting item.'}, 500

    def post(self, group):
        data = self.parser.parse_args()
        item = {'group': group}
        item.update(data)

        try:
            self.table.put_item(Item=item)
            return {'serviceGroup': item}
        except ClientError as e:
            log.error(f'[{self.__class__.__name__}] {e}')
            return {'message': 'Error saving item.'}, 500

    def delete(self, group):
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

    def get(self):
        try:
            return {'serviceGroups': self.table.scan()['Items']}
        except ClientError as e:
            log.error(f'[{self.__class__.__name__}] {e}')
            return {'message': 'Error getting items.'}, 500
