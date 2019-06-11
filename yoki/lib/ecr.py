import boto3
from botocore.exceptions import ClientError


class Ecr(object):
    def __init__(self):
        session = boto3.session.Session()
        self.ecr = session.client('ecr')

    def verify_image(self, repo, tag) -> bool:
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
                raise ValueError(f'Image not found: {e}')
            elif e.response['Error']['Code'] == 'RepositoryNotFoundException':
                raise ValueError(f'Repo not found: {e}')
            else:
                raise RuntimeError(e)
