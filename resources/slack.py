from flask_restful import Resource


class Slack(Resource):
    def post(self):
        return {
            # 'response_type': response_type,
            # 'channel': channel,
            # 'username': username,
            'text': 'hi there',
            # 'attachments': attachments,
            # 'replace_original': replace_original,
            # 'delete_original': delete_original,
        }
