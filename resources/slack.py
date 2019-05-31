from flask_restful import Resource, request

from slackapp.app import SlackCommandHandler, SlackMessageActionHandler


class Slack(Resource):

    def post(self):
        cmd = SlackCommandHandler(request.form.to_dict())
        return cmd.run()


class SlackMessageAction(Resource):

    def post(self):
        action = SlackMessageActionHandler(request.form.to_dict())
        return action.run()
