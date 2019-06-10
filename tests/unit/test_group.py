from botocore.stub import Stubber

from yoki.resources.group import ServiceGroup, ServiceGroupList


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

    def test_delete_group(self):
        sg = ServiceGroup()

        with Stubber(sg.dynamodb.meta.client) as stubber:
            stubber.add_client_error('delete_item')
            r = sg.delete_group('group1')

        assert r == ({'message': 'Error deleting item.'}, 500)


class TestServiceGroupList(object):
    def test_get_groups(self):
        sgl = ServiceGroupList()

        with Stubber(sgl.dynamodb.meta.client) as stubber:
            stubber.add_client_error('scan')
            r = sgl.get_groups()

        assert r == ({'message': 'Error getting items.'}, 500)
