import ast

from flask import url_for
from tests.utils import TestMixin


class TestServiceGroup(TestMixin):
    def test_post_group_unauthorized(self):
        r = self.client.post(url_for('api.ServiceGroup', group='test1'),
                             json={'services': 'first second third'})
        assert r.status_code == 401
        assert 'Authorization Required' in str(r.data)

    def test_post_group(self):
        r = self.client.post(url_for('api.ServiceGroup', group='test1'),
                             json={'services': 'first second third'},
                             headers={
                                 'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 200
        d = ast.literal_eval(r.data.decode('utf-8'))
        assert d['serviceGroup']['group'] == 'test1'
        assert d['serviceGroup']['services'] == ['first second third']

    def test_get_group_unauthorized(self):
        r = self.client.get(url_for('api.ServiceGroup', group='test1'))
        assert r.status_code == 401
        assert 'Authorization Required' in str(r.data)

    def test_get_group(self):
        r = self.client.get(url_for('api.ServiceGroup', group='test1'),
                            headers={'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 200
        d = ast.literal_eval(r.data.decode('utf-8'))
        assert d['serviceGroup']['group'] == 'test1'
        assert d['serviceGroup']['services'] == ['first second third']

    def test_delete_group_unauthorized(self):
        r = self.client.delete(url_for('api.ServiceGroup', group='test1'))
        assert r.status_code == 401
        assert 'Authorization Required' in str(r.data)

    def test_delete_group(self):
        r = self.client.delete(url_for('api.ServiceGroup', group='test1'),
                               headers={
                                   'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 200
        d = ast.literal_eval(r.data.decode('utf-8'))
        d = ast.literal_eval(r.data.decode('utf-8'))
        assert d['message'] == 'Item deleted.'


class TestServiceGroupList(TestMixin):
    def test_group_list_unauthorized(self):
        r = self.client.get(url_for('api.ServiceGroupList'))
        assert r.status_code == 401
        assert 'Authorization Required' in str(r.data)

    def test_group_list(self):
        r = self.client.get(url_for('api.ServiceGroupList'),
                            headers={'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 200


class TestServiceGroupDeploy(TestMixin):
    def create_test_group(self):
        self.client.post(url_for('api.ServiceGroup', group='group1'),
                         json={'services': 'srv1 srv2'},
                         headers={'X-Yoki-Authorization': self.auth_header})

    def test_create_deployment_unauthorized(self):
        r = self.client.post(url_for('api.ServiceGroupDeploy',
                                     cluster='test', group='group1'))
        assert r.status_code == 401
        assert 'Authorization Required' in str(r.data)

    def test_create_deployment(self):
        self.create_test_group()

        url = url_for('api.ServiceGroupDeploy',
                      cluster='test-yoki', group='group1')

        r = self.client.post(url,
                             json={'tags': {'container1': 'srv1'}},
                             headers={
                                 'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 200

        d = ast.literal_eval(r.data.decode('utf-8'))
        msg1 = "Deploying to test-yoki srv1 " \
            "with {'tags': {'container1': 'srv1'}}"
        msg2 = "Deploying to test-yoki srv2 " \
            "with {'tags': {'container1': 'srv1'}}"

        assert 'deployment_id' in d['messages'][0]
        assert 'deployment_id' in d['messages'][1]
        assert msg1 == d['messages'][0]['message'] or \
            msg1 == d['messages'][1]['message']
        assert msg2 == d['messages'][0]['message'] or \
            msg2 == d['messages'][1]['message']

    def test_service_group_not_found(self):
        url = url_for('api.ServiceGroupDeploy',
                      cluster='test-yoki', group='missing')

        r = self.client.post(url,
                             json={'tags': {'container1': 'srv1'}},
                             headers={
                                 'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 200
        d = ast.literal_eval(r.data.decode('utf-8'))
        assert d == {'message': 'Group not found: missing'}

    def test_cluster_not_found(self):
        self.create_test_group()

        url = url_for('api.ServiceGroupDeploy',
                      cluster='missing', group='group1')

        r = self.client.post(url,
                             json={'tags': {'container1': 'srv1'}},
                             headers={
                                 'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 200

        d = ast.literal_eval(r.data.decode('utf-8'))
        msg1 = '[missing srv1]: Cluster not found: missing'
        msg2 = '[missing srv2]: Cluster not found: missing'

        assert msg1 == d['messages'][0]['message'] or \
            msg1 == d['messages'][1]['message']
        assert msg2 == d['messages'][0]['message'] or \
            msg2 == d['messages'][1]['message']

    def test_container_not_found(self):
        self.create_test_group()

        url = url_for('api.ServiceGroupDeploy',
                      cluster='test-yoki', group='group1')

        r = self.client.post(url,
                             json={'tags': {'missing': 'srv1'}},
                             headers={
                                 'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 200

        d = ast.literal_eval(r.data.decode('utf-8'))
        expected = 'Container missing not found in task definition'

        assert expected in d['messages'][0]['message']
        assert expected in d['messages'][1]['message']

    def test_tag_not_found(self):
        self.create_test_group()

        url = url_for('api.ServiceGroupDeploy',
                      cluster='test-yoki', group='group1')

        r = self.client.post(url,
                             json={'tags': {'container1': 'missing'}},
                             headers={
                                 'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 200

        d = ast.literal_eval(r.data.decode('utf-8'))
        expected = 'Image not found: An error occurred'

        assert expected in d['messages'][0]['message']
        assert expected in d['messages'][1]['message']
