import os

from flask import Flask
from flask_restful import Api
from flask_cognito import CognitoAuth

from yoki.resources.deployment import Deployment, DeploymentList
from yoki.resources.scale import Scale
from yoki.resources.group import (
    ServiceGroup,
    ServiceGroupList,
    ServiceGroupDeploy,
    ServiceGroupScale
)
from yoki.resources.slack import Slack, SlackMessageAction
from yoki.resources.auth import Auth


def create_app(settings_override=None):
    '''
    Create a Flask application using the app factory pattern.

    :param settings_override: Override settings
    :return: Flask app
    '''
    app = Flask(__name__, instance_relative_config=True)
    api = Api(app)

    if settings_override:
        app.config.update(settings_override)

    conginto_config(app)
    register_routes(api)

    return app


def conginto_config(app):
    cogconf = {
        'COGNITO_REGION': os.environ.get('COGNITO_REGION', 'us-east-1'),
        'COGNITO_USERPOOL_ID': os.environ['COGNITO_USERPOOL_ID'],
        'COGNITO_APP_CLIENT_ID': os.environ['COGNITO_APP_CLIENT_ID'],
        'COGNITO_CHECK_TOKEN_EXPIRATION': False,
        'COGNITO_JWT_HEADER_NAME': 'X-Yoki-Authorization',
        'COGNITO_JWT_HEADER_PREFIX': 'Bearer',
    }
    app.config.update(**cogconf)
    CognitoAuth(app)


def register_routes(api):
    CL = '/clusters/<string:cluster>'
    CL_SRV = f'{CL}/services/<string:service>'
    CL_GRP = f'{CL}/groups/<string:group>'

    Deployment_routes = [
        f'{CL_SRV}/deploy',
        f'/deployments/<string:deployment>',
        f'{CL_SRV}/deployments/<string:deployment>',
    ]
    api.add_resource(Deployment, *Deployment_routes, endpoint='api.Deployment')

    DeploymentList_routes = [
        '/deployments',
        f'{CL}/deployments',
        f'{CL_SRV}/deployments',
    ]
    api.add_resource(DeploymentList, *DeploymentList_routes,
                     endpoint='api.DeploymentList')
    api.add_resource(Scale, f'{CL_SRV}/scale', endpoint='api.Scale')

    # Groups
    api.add_resource(ServiceGroup, '/groups/<string:group>',
                     endpoint='api.ServiceGroup')
    api.add_resource(ServiceGroupList, '/groups',
                     endpoint='api.ServiceGroupList')
    api.add_resource(ServiceGroupDeploy, f'{CL_GRP}/deploy',
                     endpoint='api.ServiceGroupDeploy')
    api.add_resource(ServiceGroupScale, f'{CL_GRP}/scale',
                     endpoint='api.ServiceGroupScale')

    api.add_resource(Slack, '/slack', endpoint='api.Slack')
    api.add_resource(SlackMessageAction, '/slack/message_action',
                     endpoint='api.SlackMessageAction')

    api.add_resource(Auth, '/auth', endpoint='api.Auth')
