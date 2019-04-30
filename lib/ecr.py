import boto3
from botocore.exceptions import ClientError


class Ecr(object):
    def __init__(self):
        session = boto3.session.Session()
        self.ecr = session.client('ecr')

    def verify_image(self, repo, tag):
        try:
            self.ecr.describe_images(
                repositoryName=repo,
                imageIds=[
                    {
                        'imageTag': tag
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
