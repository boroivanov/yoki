from flask import Flask
from flask_restful import Api

from resources.deployment import Deployment, DeploymentList
from resources.slack import Slack

app = Flask(__name__)
api = Api(app)


api.add_resource(Deployment, '/clusters/<string:cluster>/'
                 'services/<string:service>/deployments/<string:deployment>')

DeploymentList_routes = [
    '/deployments',
    '/clusters/<string:cluster>/deployments',
    '/clusters/<string:cluster>/services/<string:service>/deployments',
]
api.add_resource(DeploymentList, *DeploymentList_routes)
api.add_resource(Slack, '/slack')


if __name__ == "__main__":
    app.run()
