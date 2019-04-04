from flask import Flask
from flask_restful import Api

from resources.deployment import DeploymentList

app = Flask(__name__)
api = Api(app)

DeploymentList_routes = [
    '/deployments',
    '/clusters/<string:cluster>/deployments',
    '/clusters/<string:cluster>/services/<string:service>/deployments',
]
api.add_resource(DeploymentList, *DeploymentList_routes)


if __name__ == "__main__":
    app.run()
