import pytest
from botocore.stub import Stubber

from yoki.lib.ecs import Ecs
from yoki.lib.ecr import Ecr


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
