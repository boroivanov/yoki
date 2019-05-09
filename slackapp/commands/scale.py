import ast
import os
import requests

from models.notifications import Notifications


YOKI_API = os.getenv('YOKI_API')

help_text = 'Scale a service.'


class SlackCommand(object):

    def run(self, args, params):
        try:
            cluster, service, count = args
            count = int(count)
        except ValueError:
            return self.help()

        url = f'{YOKI_API}/clusters/{cluster}/services/{service}/scale'
        r = requests.post(url, json={'count': count})
        data = ast.literal_eval(r.text)

        if 'deployment_id' in data:
            self.save_cmd_details(data, params)

        return {'response_type': 'ephemeral', 'text': data['message']}

    def save_cmd_details(self, data, params):
        deployment_id = data['deployment_id']
        item = Notifications(deployment_id,
                             cmd_channel_id=params['channel_id'],
                             cmd_response_url=params['response_url'],
                             cmd_username=params['user_name']
                             )
        item.put_item()

    def help(self):
        help_text = 'Usage: `scale [cluster] [service] [count]`\n'

        return {'attachments': [{'text': help_text}]}
