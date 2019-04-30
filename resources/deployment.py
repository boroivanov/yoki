import os
import logging
import boto3
from flask_restful import Resource, reqparse
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from encoders.decimal import decimal_to_dict
from lib.ecs import Ecs


DYNAMODB_TABLE_PREFIX = os.getenv('DYNAMODB_TABLE_PREFIX', 'dev-')

log = logging.getLogger()
log.setLevel(os.getenv('LOG_LEVEL', logging.INFO))


class Deployment(Resource):
    dynamodb = boto3.resource('dynamodb')
    table_name = DYNAMODB_TABLE_PREFIX + 'yoki-ECSTaskDigest'
    table = dynamodb.Table(table_name)

    parser = reqparse.RequestParser()
    parser.add_argument('tags',
                        type=dict,
                        required=True,
                        help='Tags dict cannot be blank.'
                        )

    def get(self, cluster, service, deployment):
        try:
            params = {
                'Key': {'deployment': f'ecs-svc/{deployment}'},
            }
            return {'deployment': decimal_to_dict(
                self.table.get_item(**params)['Item']
            )}
        except KeyError:
            return {'deployment': 'Deployment not found'}, 404
        except ClientError as e:
            log.error(f'[{self.__class__.__name__}] {e}')
            return {'message': 'Error getting item.'}, 500

    def post(self, cluster, service):
        data = self.parser.parse_args()
        ecs = Ecs(cluster, service, data['tags'])
        try:
            d = ecs.deploy()
        except ValueError as e:
            return {'message': str(e)}

        deployment_id = d['service']['deployments'][0]['id']
        return {'deployment_id': deployment_id,
                'message': f'Deploying {deployment_id} to {cluster} '
                f'{service} with {data}'}


class DeploymentList(Resource):
    dynamodb = boto3.resource('dynamodb')
    table_name = DYNAMODB_TABLE_PREFIX + 'yoki-ECSTaskDigest'
    table = dynamodb.Table(table_name)

    def get(self, cluster=None, service=None):
        params = {
            'IndexName': 'cluster-service-index',
        }
        try:
            if cluster and service:
                params['KeyConditionExpression'] = Key('cluster').eq(
                    cluster) & Key('service').eq(service)
            elif cluster and not service:
                params['KeyConditionExpression'] = Key('cluster').eq(cluster)
            else:
                return {'deployments': decimal_to_dict(
                    self.table.scan()['Items']
                )}

            return {'deployments': decimal_to_dict(
                self.table.query(**params)['Items']
            )}
        except ClientError as e:
            log.error(f'[{self.__class__.__name__}] {e}')
            return {'message': 'Error getting items.'}, 500
