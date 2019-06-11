from flask import url_for
from tests.utils import TestMixin


class TestAuth(TestMixin):
    def test_auth(self):
        r = self.client.post(url_for('api.Auth'),
                             json={'username': 'test1234@example.com',
                                   'password': 'bn80Zd7Hj$rFCsdWK%gl0B7#w'})
        assert r.status_code == 200
        assert 'access_token' in str(r.data)

    def test_auth_bad_password(self):
        r = self.client.post(url_for('api.Auth'),
                             json={'username': 'test1234@example.com',
                                   'password': 'bad'})
        assert r.status_code == 200
        assert 'NotAuthorizedException' in str(r.data)

    def test_auth_user_not_found(self):
        r = self.client.post(url_for('api.Auth'),
                             json={'username': 'missing',
                                   'password': 'bn80Zd7Hj$rFCsdWK%gl0B7#w'})
        assert r.status_code == 200
        assert 'UserNotFoundException' in str(r.data)
