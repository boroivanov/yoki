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
        help_text = 'Usage: `deploy [cluster] [service] [tags]...`\n'
        examples_text = 'Examples:\n' \
            '`deploy cluster1 srv1 tag1` - deploy a single positional ' \
            'tag. The first container in the service is going to be ' \
            'updated.\n' \
            '`deploy cluster1 srv1 tag1 tag2` - deploy two positional ' \
            'containers. The first and second containers will be updated.\n' \
            '`deploy cluster1 srv1 container1:tag1 container2:tag2` - ' \
            'deploy two containers by name. Useful if you want to be ' \
            'explicit ' \
            'and/or you need to deploy to a specific container(s) in a ' \
            'a service without updating the rest of the containers.'

        return {'attachments': [{'text': help_text}, {'text': examples_text}]}
