import pytest

from botocore.stub import Stubber

from yoki.lib.ecr import Ecr


class TestEcr(object):
    def test_verify_image(self):
        ecr = Ecr()
        ecr.verify_image('test-yoki', 'srv1')

    def test_verify_image_missing_image(self):
        ecr = Ecr()

        with Stubber(ecr.ecr) as stubber:
            stubber.add_client_error('describe_images',
                                     'ImageNotFoundException')
            with pytest.raises(ValueError) as excinfo:
                ecr.verify_image('repo', 'tag')

        assert 'Image not found:' in str(excinfo.value)

    def test_verify_image_missing_repo(self):
        ecr = Ecr()

        with Stubber(ecr.ecr) as stubber:
            stubber.add_client_error('describe_images',
                                     'RepositoryNotFoundException')
            with pytest.raises(ValueError) as excinfo:
                ecr.verify_image('repo', 'tag')

        assert 'Repo not found:' in str(excinfo.value)

    def test_verify_image_runtime_error(self):
        ecr = Ecr()

        with Stubber(ecr.ecr) as stubber:
            stubber.add_client_error('describe_images')
            with pytest.raises(RuntimeError) as excinfo:
                ecr.verify_image('repo', 'tag')

        assert 'An error occurred' in str(excinfo.value)
