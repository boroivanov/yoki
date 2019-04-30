import boto3
from botocore.exceptions import ClientError


class Ecr(object):
    def __init__(self):
        session = boto3.session.Session()
        self.ecr = session.client('ecr')

    def verify_images(self, repo, tags: list) -> bool:
        if not isinstance(tags, list):
            tags = [tags]

        try:
            self.ecr.describe_images(
                repositoryName=repo,
                imageIds=[
                    {
                        'imageTag': tags
                    },
                ],
                filter={
                    'tagStatus': 'TAGGED'
                }
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == 'ImageNotFoundException':
                raise ValueError('Image not found: {}'.format(e))
            else:
                raise RuntimeError(e)

        return False
