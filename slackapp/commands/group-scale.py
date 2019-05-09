import ast
import os
import requests

from resources.group import ServiceGroup
from models.notifications import Notifications


YOKI_API = os.getenv('YOKI_API')


class SlackCommand(object):

    def run(self, args, params):
        try:
            cluster, group, count = args
            count = int(count)
        except ValueError:
            return self.help()

        sg = ServiceGroup()
        res = sg.get(group)

        if isinstance(res, tuple):
            return {'text': res[0]}

        services = res['serviceGroup']['services'][0].split()

        messages = []
        for service in services:
            msg = self.scale_service(cluster, group, count, params)
            messages.append(msg)

        attachments = []
        for msg in messages:
            attachments.append({'text': msg['message']})

        return {'attachments': attachments}

    def scale_service(self, cluster, group, count, params):
        url = f'{YOKI_API}/clusters/{cluster}/groups/{group}/scale'
        r = requests.post(url, json={'count': count})
        data = ast.literal_eval(r.text)

        if 'deployment_id' in data:
            self.save_cmd_details(data, params)

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
