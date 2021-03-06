from flask_restful import Resource, reqparse
from flask_cognito import cognito_auth_required

from yoki.lib.ecs import Ecs


class Scale(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('count',
                        type=int,
                        required=True,
                        help='Count cannot be blank.'
                        )

    @cognito_auth_required
    def post(self, cluster, service):
        data = self.parser.parse_args()
        return self.scale_service(cluster, service, data)

    def scale_service(self, cluster, service, data):
        ecs = Ecs(cluster, service)
        try:
            d = ecs.scale(**data)
        except ValueError as e:
            return {'message': f'[{cluster} {service}]: {str(e)}'}

        deployment_id = d['service']['deployments'][0]['id']
        return {'deployment_id': deployment_id,
                'message': f'Scaling {cluster} {service} with {data}'}
