import boto3
from botocore.exceptions import ClientError

from yoki.lib.ecr import Ecr


class Ecs(object):
    def __init__(self, cluster, service):
        session = boto3.session.Session()
        self.ecs = session.client('ecs')
        self.cluster_name = cluster
        self.service_name = service

    def describe_service(self):
        try:
            res = self.ecs.describe_services(
                cluster=self.cluster_name,
                services=[self.service_name]
            )
            return res['services'][0]
        except ClientError as e:
            if e.response['Error']['Code'] == 'ClusterNotFoundException':
                raise ValueError(f'Cluster not found: {self.cluster_name}')
            elif e.response['Error']['Code'] == 'ServiceNotFoundException':
                raise ValueError(f'Service not found: {self.service_name}')
            else:
                raise RuntimeError(e)
        except IndexError:
            raise ValueError(f'Service not found: {self.service_name}')

    def describe_task_definition(self, taskDefinition):
        res = self.ecs.describe_task_definition(taskDefinition=taskDefinition)
        return res['taskDefinition']

    def verify_images(self, td):
        containers = td['containerDefinitions']
        ecr = Ecr()
        images = {}
        for e, container in enumerate(containers):
            self.rename_positional_containers(e, container)
            if container['name'] not in self.tags.keys():
                continue
            image_uri = self.split_image_uri(container)

            if 'dkr.ecr' in image_uri['repo']:
                if not ecr.verify_image(image_uri['repo'].split('/')[1],
                                        self.tags[container['name']]
                                        ):
                    raise
            images[container['name']] = image_uri

        for name in self.tags.keys():
            if name not in images:
                raise ValueError(f' Container {name}'
                                 f' not found in task definition'
                                 f" {td['taskDefinitionArn']}.")

        return images

    def rename_positional_containers(self, index, container):
        '''Swap positional container/tag with container_name/tag'''
        if index in self.tags.keys():
            self.tags[container['name']] = self.tags[index]
            del self.tags[index]

    def register_new_task_definition(self):
        '''Get the current task definition. Compare and verify all images/tags.
           Then create a new task definition with the new tags.

           :return: New task definition name
           :rtype: str
        '''
        srv = self.describe_service()
        td = self.describe_task_definition(srv['taskDefinition'])
        new_images = self.verify_images(td)

        new_td = self.create_new_task_definition(td, new_images)
        res = self.ecs.register_task_definition(**new_td)
        return res['taskDefinition']['taskDefinitionArn'].split('/')[-1]

    def deploy(self, tags: dict):
        self.tags = tags
        params = {
            'cluster': self.cluster_name,
            'service': self.service_name,
            'taskDefinition': self.register_new_task_definition(),
            'forceNewDeployment': True
        }
        return self.ecs.update_service(**params)

    def scale(self, count):
        params = {
            'cluster': self.cluster_name,
            'service': self.service_name,
            'desiredCount': count,
        }
        try:
            return self.ecs.update_service(**params)
        except ClientError as e:
            if e.response['Error']['Code'] == 'ClusterNotFoundException':
                raise ValueError(f'Cluster not found: {self.cluster_name}')
            elif e.response['Error']['Code'] == 'ServiceNotFoundException':
                raise ValueError(f'Service not found: {self.service_name}')
            else:
                raise RuntimeError(e)

    def create_new_task_definition(self, td, new_images):
        new_td = td.copy()
        for k in ['status', 'compatibilities', 'taskDefinitionArn',
                  'revision', 'requiresAttributes']:
            del new_td[k]

        # Update containers with the new image tags.
        for cd in new_td['containerDefinitions']:
            if cd['name'] not in new_images:
                continue
            cd['image'] = f"{new_images[cd['name']]['repo']}:" \
                f"{self.tags[cd['name']]}"

        return new_td

    def split_image_uri(self, container: str) -> tuple:
        raw = container['image']
        image_uri = {}

        try:
            image_uri['repo'], image_uri['tag'] = raw.split(':')
        except ValueError:
            # If no tag was specified - defaulting to latest tag.
            image_uri['repo'] = raw
            image_uri['tag'] = 'latest'

        return image_uri
