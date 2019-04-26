from flask_restful import Resource, request

from lib.slack import SlackCommandHandler


class Slack(Resource):

    def post(self):
        cmd = SlackCommandHandler(request.form.to_dict())
        return cmd.run()
