from flask import Flask
from flask_restful import Api

from resources.deployment import Deployment, DeploymentList
from resources.scale import Scale
from resources.service_group import ServiceGroup, ServiceGroupList
from resources.slack import Slack

app = Flask(__name__)
api = Api(app)


Deployment_routes = [
    '/clusters/<string:cluster>/services/<string:service>',
    '/clusters/<string:cluster>/'
    'services/<string:service>/deployments/<string:deployment>',
]
api.add_resource(Deployment, *Deployment_routes)

DeploymentList_routes = [
    '/deployments',
    '/clusters/<string:cluster>/deployments',
    '/clusters/<string:cluster>/services/<string:service>/deployments',
]
api.add_resource(DeploymentList, *DeploymentList_routes)
api.add_resource(Scale, '/clusters/<string:cluster>/services/<string:service>')
api.add_resource(ServiceGroup, '/service-groups/<string:group>')
api.add_resource(ServiceGroupList, '/service-groups')
api.add_resource(Slack, '/slack')


if __name__ == "__main__":
    app.run()
