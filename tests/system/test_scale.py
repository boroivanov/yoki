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
