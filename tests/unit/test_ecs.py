import pytest
from botocore.stub import Stubber

from yoki.lib.ecs import Ecs


class TestEcs(object):
    def test_descrive_service_missing_cluster(self):
        ecs = Ecs('missing', 'srv1')

        with Stubber(ecs.ecs) as stubber:
            stubber.add_client_error('describe_services',
                                     'ClusterNotFoundException')
            with pytest.raises(ValueError) as excinfo:
                ecs.describe_service()

        assert 'Cluster not found: missing' in str(excinfo.value)

    def test_descrive_service_missing_service(self):
        ecs = Ecs('test-yoki', 'missing')

        with Stubber(ecs.ecs) as stubber:
            stubber.add_client_error('describe_services',
                                     'ServiceNotFoundException')
            with pytest.raises(ValueError) as excinfo:
                ecs.describe_service()

        assert 'Service not found: missing' in str(excinfo.value)

    def test_descrive_service_runtime(self):
        ecs = Ecs('test-yoki', 'srv1')

        with Stubber(ecs.ecs) as stubber:
            stubber.add_client_error('describe_services')
            with pytest.raises(RuntimeError) as excinfo:
                ecs.describe_service()

        assert 'An error occurred' in str(excinfo.value)

    def test_scale_runtime_error(self):
        ecs = Ecs('test-yoki', 'srv1')

        with Stubber(ecs.ecs) as stubber:
            stubber.add_client_error('update_service')
            with pytest.raises(RuntimeError) as excinfo:
                ecs.scale(0)

        assert 'An error occurred' in str(excinfo.value)

    def test_split_image_uri_no_tag(self):
        ecs = Ecs('test-yoki', 'srv1')
        r = ecs.split_image_uri({'image': 'image_uri'})

        assert r == {'repo': 'image_uri', 'tag': 'latest'}
