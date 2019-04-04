import boto3
from flask_restful import Resource
from boto3.dynamodb.conditions import Key

from encoders.decimal import decimal_to_dict


class Deployment(Resource):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ecs-slack-ECSTaskDigest')

    def get(self, deployment, cluster=None, service=None):
        try:
            params = {
                'Key': {'startedBy': f'ecs-svc/{deployment}'},
            }
            return {'deployment': decimal_to_dict(
                self.table.get_item(**params)['Item']
            )}
        except KeyError:
            return {'deployment': 'Deployment not found'}, 404


class DeploymentList(Resource):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ECSDeployments')

    def get(self, cluster=None, service=None):
        params = {
            'IndexName': 'cluster-service-index',
        }
        if cluster and service:
            params['KeyConditionExpression'] = Key('cluster').eq(
                cluster) & Key('service').eq(service)
        elif cluster and not service:
            params['KeyConditionExpression'] = Key('cluster').eq(cluster)
        else:
            return self.table.scan()['Items']

        return {'deployments': decimal_to_dict(
            self.table.query(**params)['Items']
        )}
