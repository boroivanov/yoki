import time
from yoki.models.notifications import Notifications


class TestNotifications(object):
    def test_as_dict_bare(self):
        n = Notifications('ecs-svc/9223370476922431730')
        assert n.as_dict() == {
            'deployment': 'ecs-svc/9223370476922431730',
            'TTL': int(time.time()) + int(2592000),
        }

    def test_as_dict(self):
        expected = {
            'deployment': 'ecs-svc/9223370476922431730',
            'cmd_username': 'cmd_username',
            'slack_ts': 'slack_ts',
            'cmd_response_url': 'cmd_response_url',
            'cmd_channel_id': 'cmd_channel_id',
            'cmd_ts': 'cmd_ts'
        }

        n = Notifications(**expected)

        expected['TTL'] = int(time.time()) + int(2592000)

        assert n.as_dict() == expected

    def test_crud(self):
        expected = {
            'deployment': 'ecs-svc/9223370476922431730',
            'cmd_username': 'cmd_username',
            'slack_ts': 'slack_ts',
            'cmd_response_url': 'cmd_response_url',
            'cmd_channel_id': 'cmd_channel_id',
            'cmd_ts': 'cmd_ts'
        }

        n = Notifications(**expected)
        n.put_item()

        expected['TTL'] = int(time.time()) + int(2592000)

        assert n.get_item() == expected
