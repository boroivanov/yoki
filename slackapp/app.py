import os
import boto3
import logging
import string
import importlib

from collections import Counter
from slackclient import SlackClient

from models.notifications import Notifications


log = logging.getLogger()
log.setLevel(os.getenv('LOG_LEVEL', logging.INFO))

boto3.resource('dynamodb')


class Slack(object):
    def __init__(self, token):
        self.sc = SlackClient(token)

    def get_slack_channels(self):
        channels = []
        cursor = None
        response = None

        while True:
            try:
                cursor = response['response_metadata']['next_cursor']
                if len(cursor) == 0:
                    break
            except KeyError:
                break
            except TypeError:
                pass
            response = self.sc.api_call(
                'channels.list',
                exclude_archived='true',
                exclude_members='true',
                cursor=cursor
            )
            channels += response['channels']

        return channels

    def get_slack_channel_id(self, channel_name):
        channel_id = None
        channels = self.get_slack_channels()

        for c in channels:
            if c['name'] == channel_name:
                channel_id = c['id']

        return channel_id


class SlackTaskDigest(Slack):
    def __init__(self, token, channel, record):
        super().__init__(token)
        self.deserializer = boto3.dynamodb.types.TypeDeserializer()
        self.channel = channel
        self.record = record['Records'][0]
        self.region = self.record['awsRegion']
        self.item = self.record['dynamodb']
        self.deployment = self.deployment()

    def deployment_id(self):
        keys = {k: self.deserializer.deserialize(
            v) for k, v in self.item['Keys'].items()}
        return keys['deployment']

    def deployment(self):
        return {k: self.deserializer.deserialize(
            v) for k, v in self.item['NewImage'].items()}

    def ecs_url(self):
        return f'https://console.aws.amazon.com/ecs/home?region=' \
            f'{self.region}#/'

    def srv_url(self):
        return f'{self.ecs_url()}' \
            f"clusters/{self.deployment['cluster']}/" \
            f"services/{self.deployment['service']}/tasks"

    def td_url(self):
        return f'{self.ecs_url()}taskDefinitions/' \
            f"{self.deployment['definition'].replace(': ', '/')}"

    def stats(self):
        return Counter(self.deployment['tasks'].values())

    def container_stats(self):
        return ' '.join(f'{k.lower()}: {v}' for k, v in self.stats().items())

    def message_color(self):
        if self.deployment['desiredCount'] != self.deployment['runningCount']:
            color = 'warning'
        elif self.deployment['pendingCount'] != 0:
            color = 'warning'
        else:
            color = 'good'
        return color

    def message_title(self):
        return f"{self.deployment['cluster']} " \
            f"{self.deployment['service']} - " \
            f"{' '.join(self.deployment['images'])}"

    def message_title_cmd(self):
        return f"{self.deployment['runningCount']}/" \
            f"{self.deployment['desiredCount']} {self.message_title()} "

    def message_text(self):
        return f"running: {self.deployment['runningCount']}" \
            f" desired: {self.deployment['desiredCount']}" \
            f"  pending: {self.deployment['pendingCount']}"

    def message_footer(self):
        return f"ecs {self.deployment['launchType'].lower()}" \
            f" {self.deployment['definition']} {self.deployment_id()}"

    def prepare_message(self):
        return {
            'channel': self.get_slack_channel_id(self.channel),
            'attachments': [
                {
                    'title': self.message_title(),
                    'title_link': self.srv_url(),
                    'color': self.message_color(),
                    'text': self.message_text(),
                    'fields': [
                        {
                            'title': 'Container Stats',
                            'value': self.container_stats(),
                            'short': 'false'
                        },
                    ],
                    'footer': self.message_footer(),
                }
            ]
        }

    def prepare_message_cmd_response(self, channel, rtype='in_channel'):
        return {
            'channel': channel,
            'response_type': rtype,
            'attachments': [
                {
                    'title': self.message_title_cmd(),
                    'title_link': self.srv_url(),
                    'color': self.message_color(),
                    'footer': self.message_footer(),
                }
            ]
        }

    def post_to_slack(self):
        params = self.prepare_message()

        notification = Notifications(self.deployment_id())
        item = notification.get_item()

        if item:
            res = self.update_message(item, params)
        else:
            res = self.post_new_message(params)

        log.info(f'Slack response is: {res}')
        return True

    def post_new_message(self, params, item=None):
        res = self.sc.api_call('chat.postMessage', **params)
        self.update_notifications_item(res, item)
        return res

    def update_message(self, item, params):
        ts = item['slack_ts']
        if ts == 'locked':
            log.info('Skipping post. Slack timestamp is locked.')
        elif ts == 'pending':
            self.post_new_message(params, item)
        res = self.sc.api_call('chat.update', ts=ts, **params)

        if 'cmd_channel_id' in item:
            self.respond_to_command(item)
        return res

    def respond_to_command(self, item):
        params = self.prepare_message_cmd_response(item['cmd_channel_id'])
        if 'cms_ts' in item:
            res = self.sc.api_call('chat.update', ts=item['cmd_ts'], **params)
        else:
            res = self.sc.api_call('chat.postMessage', **params)
            self.update_notifications_item(res, item, msg_ts_type='cmd_ts')

        log.info(f'Slack command response: {res}')

    def update_notifications_item(self, slack_response, saved_item=None,
                                  msg_ts_type='slack_ts'):
        try:
            ts = slack_response['message']['ts']
        except KeyError:
            log.error('Error: Cannot get slack timestamp. Slack response:')
            log.error(slack_response)

        if saved_item:
            saved_item[msg_ts_type] = ts
            item = Notifications(**saved_item)
        else:
            item = Notifications(self.deployment_id(), ts)
        item.put_item()


class SlackCommandHandler(Slack):
    commands_path = os.path.join(os.path.dirname(__file__), 'commands')

    def __init__(self, params):
        log.info(f'Received slack command: {params}')
        self.verify_slack_token(params['token'])
        self.params = params

    def verify_slack_token(self, token):
        if token != os.environ['SLACK_VERIFICATION_TOKEN']:
            log.error('Request token ' + token + ' does not match expected')
            raise ValueError('Invalid request token')

    def run(self):
        '''Parse slack command object and run the command.

        :return: Slack command response
        :rtype: dict
        '''
        try:
            command_text = self.params['text'].split()
            self.command = command_text[0]
            self.args = command_text[1:]
        except IndexError:
            return self.help()

        if self.command == 'help':
            return self.help()

        try:
            cmd = self.get_command(self.command)
        except ImportError:
            return self.help()

        res = cmd.run(self.args, self.params)
        return res

    def help(self):
        return {'text': '\n'.join(self.list_commands())}

    def get_command(self, module):
        '''Dynamically load slack commands from slackapp/commands/

        :param module: Command filename
        :type module: str
        :return: SlackCommand object
        :rtype: class object
        '''
        try:
            path = f'slackapp.commands.{module}'
            cmd_module = importlib.import_module(path)
            cmd_obj = getattr(cmd_module, 'SlackCommand')
            return cmd_obj()
        except ImportError:
            raise

    def list_commands(self):
        '''List commands in slackapp/commands/

        :return: Slack commands
        :rtype: list
        '''
        commands = []
        alpha = string.ascii_letters
        for filename in os.listdir(self.commands_path):
            if filename.startswith(tuple(alpha)) and filename.endswith('.py'):
                commands.append(filename[:-3])
        commands.sort()
        return commands