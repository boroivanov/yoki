from botocore.stub import Stubber

from yoki.resources.group import ServiceGroup


class TestServiceGroup(object):
    def test_get_group(self):
        sg = ServiceGroup()

        with Stubber(sg.dynamodb.meta.client) as stubber:
            stubber.add_client_error('get_item')
            r = sg.get_group('group1')

        assert r == ({'message': 'Error getting item.'}, 500)

    def test_update_group(self):
        sg = ServiceGroup()

        with Stubber(sg.dynamodb.meta.client) as stubber:
            stubber.add_client_error('put_item')
            r = sg.update_group('group1', {'services': ['srv1', 'srv2']})

        assert r == ({'message': 'Error saving item.'}, 500)
