import ast

from flask import url_for
from tests.utils import TestMixin


class TestScale(TestMixin):
    def test_scale_unauthorized(self):
        r = self.client.post(url_for('api.Scale',
                                     cluster='test-yoki', service='srv1'))
        assert r.status_code == 401
        assert 'Authorization Required' in str(r.data)

    def test_scale(self):
        r = self.client.post(url_for('api.Scale',
                                     cluster='test-yoki', service='srv1'),
                             json={'count': 0},
                             headers={
                                 'X-Yoki-Authorization': self.auth_header})

        assert r.status_code == 200
        d = ast.literal_eval(r.data.decode('utf-8'))
        assert d['message'] == "Scaling test-yoki srv1 with {'count': 0}"

    def test_scale_missing_cluster(self):
        r = self.client.post(url_for('api.Scale',
                                     cluster='missing', service='srv1'),
                             json={'count': 0},
                             headers={
                                 'X-Yoki-Authorization': self.auth_header})

        assert r.status_code == 200
        d = ast.literal_eval(r.data.decode('utf-8'))
        assert d['message'] == "[missing srv1]: " \
            "Cluster not found: missing"

    def test_scale_missing_service(self):
        r = self.client.post(url_for('api.Scale',
                                     cluster='test-yoki', service='missing'),
                             json={'count': 0},
                             headers={
                                 'X-Yoki-Authorization': self.auth_header})

        assert r.status_code == 200
        d = ast.literal_eval(r.data.decode('utf-8'))
        assert d['message'] == "[test-yoki missing]: " \
            "Service not found: missing"


class TestServiceGroupScale(TestMixin):
    def test_group_scale_unauthorized(self):
        r = self.client.post(url_for('api.ServiceGroupScale',
                                     cluster='test-yoki', group='group1'))
        assert r.status_code == 401
        assert 'Authorization Required' in str(r.data)

    def test_group_scale(self):
        r = self.client.post(url_for('api.ServiceGroupScale',
                                     cluster='test-yoki', group='group1'),
                             json={'count': 0},
                             headers={
                                 'X-Yoki-Authorization': self.auth_header})

        assert r.status_code == 200
        d = ast.literal_eval(r.data.decode('utf-8'))

        msg1 = "Scaling test-yoki srv1 with {'count': 0}"
        msg2 = "Scaling test-yoki srv2 with {'count': 0}"

        assert 'deployment_id' in d['messages'][0]
        assert 'deployment_id' in d['messages'][1]
        assert msg1 == d['messages'][0]['message'] or \
            msg1 == d['messages'][1]['message']
        assert msg2 == d['messages'][0]['message'] or \
            msg2 == d['messages'][1]['message']

    def test_group_scale_missing_group(self):
        r = self.client.post(url_for('api.ServiceGroupScale',
                                     cluster='test-yoki', group='missing'),
                             json={'count': 0},
                             headers={
                                 'X-Yoki-Authorization': self.auth_header})

        assert r.status_code == 200
        d = ast.literal_eval(r.data.decode('utf-8'))
        assert d['message'] == 'Group not found: missing'
