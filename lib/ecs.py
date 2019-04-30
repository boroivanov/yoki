import boto3
from botocore.exceptions import ClientError

from lib.ecr import Ecr


class Ecs(object):
    def __init__(self, cluster, service, tags: dict):
        session = boto3.session.Session()
        self.ecs = session.client('ecs')
        self.cluster_name = cluster
        self.service_name = service
        self.tags = tags

    def describe_service(self):
        try:
            res = self.ecs.describe_services(
                cluster=self.cluster_name,
                services=[self.service_name]
            )
            return res['services'][0]
        except ClientError as e:
            if e.response['Error']['Code'] == 'ClusterNotFoundException':
                raise ValueError('Cluster not found.')
            else:
                raise RuntimeError(e)
        except IndexError:
            raise ValueError('Service not found.')

    def describe_task_definition(self, taskDefinition):
        res = self.ecs.describe_task_definition(taskDefinition=taskDefinition)
        return res['taskDefinition']

    def verify_images(self, td):
        containers = td['containerDefinitions']
        ecr = Ecr()
        images = {}
        for container in containers:
            image_uri = self.split_image_uri(container)

            if image_uri['image'] not in self.tags.keys():
                raise ValueError('Image not found in current task definition.')

            if not ecr.verify_image(self.tags[image_uri['image']]):
                raise
            images[container['name']] = image_uri
        return images

    def register_new_task_definition(self):
        '''Get the current task definition. Compare and verify all images/tags.
           Then create a new task definition with the new tags.

           :return: New task definition name
           :rtype: str
        '''
        srv = self.desc_service()
        td_arn = srv['taskDefinition']
        td = self.describe_task_definition(td_arn)
        current_images = self.verify_images(td)

        new_td = self.create_new_task_definition(td, current_images)
        new_td_res = self.ecs.register_task_definition(**new_td)
        td_name = new_td_res['taskDefinition']['taskDefinitionArn'].split(
            '/')[-1]

        return td_name

    def deploy(self):
        params = {
            'cluster': self.cluster_name,
            'service': self.service_name,
            'taskDefinition': self.register_new_task_definition(),
            'forceNewDeployment': True
        }
        return self.ecs.update_service(**params)

    def create_new_task_definition(self, td, current_images):
        new_td = td.copy()
        for k in ['status', 'compatibilities', 'taskDefinitionArn',
                  'revision', 'requiresAttributes']:
            del new_td[k]

        # Update containers with the new image tags.
        for cd in new_td['containerDefinitions']:
            cd['image'] = f"{current_images[cd['name']]['repo']}" \
                f"{current_images[cd['name']]['image']}/" \
                f"{self.tags[cd['name']]}"

        return new_td

    def split_image_uri(self, container: str) -> tuple:
        raw = container['image']
        image_uri = {}

        try:
            raw, image_uri['tag'] = raw.split(':')
        except ValueError:
            # If no tag was specified - defaulting to latest tag.
            image_uri['tag'] = 'latest'

        try:
            image_uri['repo'], image_uri['image'] = raw.split('/')
            image_uri['repo'] = image_uri['repo'] + '/'
        except ValueError:
            # No repo specified.
            image_uri['image'] = raw

        return image_uri
