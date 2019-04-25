import os
import boto3
import logging
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

    def message_color(self):
        self.color = 'good'
        if self.deployment['desiredCount'] != self.deployment['runningCount']:
            self.color = '#0000FF'

    def message_title(self):
        return f"{self.deployment['cluster']} " \
            f"{self.deployment['service']} - " \
            f"{' '.join(self.deployment['images'])}"

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
                    'footer': self.message_footer(),
                }
            ]
        }

    def post_to_slack(self):
        params = self.prepare_message()

        notification = Notifications(self.region, self.deployment_id())
        item = notification.get_item()

        if item:
            ts = item['slack_ts']
            if ts == 'locked':
                log.info('Skipping post. Slack timestamp is locked.')
                return False
            res = self.sc.api_call('chat.update', ts=ts, **params)
        else:
            res = self.sc.api_call('chat.postMessage', **params)

        self.update_notifications_item(res)
        return True

    def update_notifications_item(self, slack_response):
        try:
            ts = slack_response['message']['ts']
            item = Notifications(self.region, self.deployment_id(), ts)
            item.put_item()
        except KeyError:
            print('Error: Cannot get slack timestamp. Slack response:')
            print(slack_response)
