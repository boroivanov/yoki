from flask import url_for
from tests.utils import TestMixin


class TestGroupList(TestMixin):
    def test_group_list_unauthorized(self):
        r = self.client.get(url_for('api.ServiceGroupList'))
        assert r.status_code == 401

    def test_group_list(self):
        r = self.client.get(url_for('api.ServiceGroupList'),
                            headers={'X-Yoki-Authorization': self.auth_header})
        assert r.status_code == 200
