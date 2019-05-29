import os
import logging
import boto3
from flask_restful import Resource, reqparse, request
from flask_cognito import cognito_auth_required

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

    @cognito_auth_required
    def get(self, deployment, cluster=None, service=None):
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

    @cognito_auth_required
    def post(self, cluster, service):
        data = self.parser.parse_args()
        return self.create_deployment(cluster, service, data)

    def create_deployment(self, cluster, service, tags: dict):
        ecs = Ecs(cluster, service)
        try:
            d = ecs.deploy(**tags)
        except ValueError as e:
            return {'message': f'[{cluster} {service}]: {str(e)}'}

        deployment_id = d['service']['deployments'][0]['id']
        return {'deployment_id': deployment_id,
                'message': f'Deploying to {cluster} {service} with {tags}'}


class DeploymentList(Resource):
    dynamodb = boto3.resource('dynamodb')
    table_name = DYNAMODB_TABLE_PREFIX + 'yoki-ECSTaskDigest'
    table = dynamodb.Table(table_name)

    @cognito_auth_required
    def get(self, cluster=None, service=None):
        params = {
            'IndexName': 'cluster-service-index',
        }

        try:
            params['Limit'] = int(request.args.get('limit'))
        except ValueError:
            pass
        except TypeError:
            pass

        return self.list_deployments(cluster, service, params)

    def list_deployments(self, cluster, service, params):
        try:
            if cluster and service:
                params['KeyConditionExpression'] = Key('cluster').eq(
                    cluster) & Key('service').eq(service)
            elif cluster and not service:
                params['KeyConditionExpression'] = Key('cluster').eq(cluster)
            else:
                return self.scan_deployments(params)

            return self.query_deployments(params)
        except ClientError as e:
            log.error(f'[{self.__class__.__name__}] {e}')
            return {'message': 'Error getting items.'}, 500

    def query_deployments(self, params):
        data = decimal_to_dict(self.table.query(**params)['Items'])
        return self.json(data)

    def scan_deployments(self, params):
        data = decimal_to_dict(self.table.scan(**params)['Items'])
        return self.json(data)

    def json(self, data, sort_key='updatedAt'):
        data = sorted(data, key=lambda i: i[sort_key], reverse=True)
        return {'deployments': data}
