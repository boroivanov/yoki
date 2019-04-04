from flask import Flask
from flask_restful import Api

from resources.deployment import DeploymentList

app = Flask(__name__)
api = Api(app)

api.add_resource(DeploymentList, '/')


if __name__ == "__main__":
    app.run()
