from flask_restful import Resource


class DeploymentList(Resource):
    def get(self):
        return 'hi there'
