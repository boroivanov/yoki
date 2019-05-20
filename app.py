import os

from flask import Flask
from flask_restful import Api
from flask_cognito import CognitoAuth

from resources.deployment import Deployment, DeploymentList
from resources.scale import Scale
from resources.group import (
    ServiceGroup,
    ServiceGroupList,
    ServiceGroupDeploy,
    ServiceGroupScale
)
from resources.slack import Slack
from resources.auth import Auth

app = Flask(__name__)
api = Api(app)


# Cognito
cogconf = {
    'COGNITO_REGION': os.environ.get('COGNITO_REGION', 'us-east-1'),
    'COGNITO_USERPOOL_ID': os.environ['COGNITO_USERPOOL_ID'],
    'COGNITO_APP_CLIENT_ID': os.environ['COGNITO_APP_CLIENT_ID'],
    'COGNITO_CHECK_TOKEN_EXPIRATION': False,
    'COGNITO_JWT_HEADER_NAME': 'X-Yoki-Authorization',
    'COGNITO_JWT_HEADER_PREFIX': 'Bearer',
}
app.config.update(**cogconf)
cogauth = CognitoAuth(app)


CL = '/clusters/<string:cluster>'
CL_SRV = f'{CL}/services/<string:service>'
CL_GRP = f'{CL}/groups/<string:group>'
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

# Groups
api.add_resource(ServiceGroup, '/groups/<string:group>')
api.add_resource(ServiceGroupList, '/groups')
api.add_resource(ServiceGroupDeploy, f'{CL_GRP}/deploy')
api.add_resource(ServiceGroupScale, f'{CL_GRP}/scale')

api.add_resource(Slack, '/slack')

api.add_resource(Auth, '/auth')

if __name__ == "__main__":
    app.run()
