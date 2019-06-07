import ast

from flask import url_for
from tests.utils import TestMixin


class TestDeployment(TestMixin):
    def test_get_deployment_unauthorized(self):
        r = self.client.get(url_for('api.Deployment', deployment='none'))
        assert r.status_code == 401
        assert 'Authorization Required' in str(r.data)

    def test_get_deployment_missing(self):
        r = self.client.get(url_for('api.Deployment', deployment='missing'),
                            headers={'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 404
        assert 'Deployment not found' in str(r.data)

    def test_get_deployment_by_id(self):
        r = self.client.get(url_for('api.Deployment',
                                    deployment='9223370476922431730'),
                            headers={'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 200
        d = ast.literal_eval(r.data.decode('utf-8'))
        assert 'ecs-svc/9223370476922431730' == d['deployment']['deployment']

    def test_post_deployment(self):
        r = self.client.post(url_for('api.Deployment',
                                     cluster='test-yoki', service='srv1'),
                             json={'tags': {'container1': 'srv1'}},
                             headers={
            'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 200
        d = ast.literal_eval(r.data.decode('utf-8'))
        msg1 = "Deploying to test-yoki srv1 " \
            "with {'tags': {'container1': 'srv1'}}"
        assert msg1 == d['message']


class TestDeploymentList(TestMixin):
    def test_get_deployments_all(self):
        r = self.client.get(url_for('api.DeploymentList'),
                            headers={'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 200
        d = ast.literal_eval(r.data.decode('utf-8'))
        assert len(d['deployments']) == 3

    def test_get_deployments_by_cluster(self):
        r = self.client.get(url_for('api.DeploymentList',
                                    cluster='test-yoki'),
                            headers={'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 200
        d = ast.literal_eval(r.data.decode('utf-8'))
        assert len(d['deployments']) == 2

    def test_get_deployments_by_cluster_and_service(self):
        r = self.client.get(url_for('api.DeploymentList',
                                    cluster='test-yoki', service='srv1'),
                            headers={'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 200
        d = ast.literal_eval(r.data.decode('utf-8'))
        assert len(d['deployments']) == 1

    def test_get_deployments_missing(self):
        r = self.client.get(url_for('api.DeploymentList',
                                    cluster='test-yoki', service='missing'),
                            headers={'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 200
        d = ast.literal_eval(r.data.decode('utf-8'))
        assert d == {'deployments': []}
