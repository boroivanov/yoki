import ast
import os
import requests

from models.notifications import Notifications


YOKI_API = os.getenv('YOKI_API')


class SlackCommand(object):
    def parse_args(self, args):
        try:
            self.cluster = args[0]
            self.service = args[1]
            tags = args[2:]
            if len(tags) == 0:
                raise IndexError

            self.tags = self.parse_tags(tags)
        except IndexError:
            raise

    def parse_tags(self, tags):
        parsed = {}
        for e, tag in enumerate(tags):
            try:
                container, tag = tag.split(':')
            except ValueError:
                container = e
                tag = tag
            parsed[container] = tag
        return parsed

    def run(self, args, params):
        try:
            self.parse_args(args)
        except IndexError:
            return self.help()

        url = f'{YOKI_API}/clusters/{self.cluster}/services/{self.service}'
        r = requests.post(url, json={'tags': self.tags})
        data = ast.literal_eval(r.text)

        if 'deployment_id' in data:
            self.save_cmd_response_url(data, params)

        return {'response_type': 'in_channel', 'text': data['message']}

    def save_cmd_response_url(self, data, params):
        deployment_id = data['deployment_id']
        item = Notifications(deployment_id, slack_ts='pending',
                             cmd_response_url=params['response_url'])
        item.put_item()

    def help(self):
        return {'text': 'Usage: deploy [cluster] [service] [tags]...'}
