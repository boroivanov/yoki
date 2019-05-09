import ast
import os
import requests

from models.notifications import Notifications


YOKI_API = os.getenv('YOKI_API')

help_text = 'Scale a service group.'


class SlackCommand(object):

    def run(self, args, params):
        try:
            cluster, group, count = args
            count = int(count)
        except ValueError:
            return self.help()

        res = self.scale_service_group(cluster, group, count)

        if 'message' in res:
            return {'attachments': [{'text': res['message']}]}

        attachments = []
        for msg in res['messages']:
            attachments.append({'text': msg['message']})
            self.save_cmd_details(msg, params)

        return {'attachments': attachments}

    def scale_service_group(self, cluster, group, count):
        url = f'{YOKI_API}/clusters/{cluster}/groups/{group}/scale'
        r = requests.post(url, json={'count': count})
        data = ast.literal_eval(r.text)

        return data

    def save_cmd_details(self, data, params):
        deployment_id = data['deployment_id']
        item = Notifications(deployment_id,
                             cmd_channel_id=params['channel_id'],
                             cmd_response_url=params['response_url'],
                             cmd_username=params['user_name']
                             )
        item.put_item()

    def help(self):
        help_text = 'Usage: `scale [cluster] [group] [count]`\n'

        return {'attachments': [{'text': help_text}]}
