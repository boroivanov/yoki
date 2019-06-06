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
