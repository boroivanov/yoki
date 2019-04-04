import boto3
from flask_restful import Resource
from boto3.dynamodb.conditions import Key


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

        return {'deployments': self.table.query(**params)['Items']}
