from flask import Flask
from flask_restful import Api

from resources.deployment import Deployment, DeploymentList
from resources.scale import Scale
from resources.service_group import ServiceGroup, ServiceGroupList
from resources.slack import Slack

app = Flask(__name__)
api = Api(app)

CL = '/clusters/<string:cluster>'
CL_SRV = f'{CL}/services/<string:service>'
CL_SRV_DEPL = f'{CL_SRV}/<string:deployment>'


Deployment_routes = [
    f'{CL_SRV}/deploy',
    f'{CL_SRV}/deployments/<string:deployment>',
]
api.add_resource(Deployment, *Deployment_routes)

DeploymentList_routes = [
    '/deployments',
    f'{CL}/deployments',
    f'{CL_SRV}/deployments',
]
api.add_resource(DeploymentList, *DeploymentList_routes)
api.add_resource(Scale, f'{CL_SRV}/scale')
api.add_resource(ServiceGroup, '/service-groups/<string:group>')
api.add_resource(ServiceGroupList, '/service-groups')
api.add_resource(Slack, '/slack')


if __name__ == "__main__":
    app.run()
