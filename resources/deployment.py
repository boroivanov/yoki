from flask_restful import Resource


class DeploymentList(Resource):
    def get(self, cluster=None, service=None):
        return 'hi there'
