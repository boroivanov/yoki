from flask_restful import Resource, reqparse

from lib.ecs import Ecs


class Scale(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('count',
                        type=int,
                        required=True,
                        help='Count cannot be blank.'
                        )

    def post(self, cluster, service):
        data = self.parser.parse_args()
        ecs = Ecs(cluster, service)
        try:
            d = ecs.scale(**data)
        except ValueError as e:
            return {'message': str(e)}

        deployment_id = d['service']['deployments'][0]['id']
        return {'deployment_id': deployment_id,
                'message': f'Scaling to {cluster} {service} with {data}'}
