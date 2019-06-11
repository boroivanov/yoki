from yoki.resources.deployment import Deployment
from yoki.resources.group import ServiceGroupDeploy
from yoki.models.notifications import Notifications


class DeployCommand(object):
    def parse_args(self, args):
        try:
            self.cluster = args[0]
            self.service = args[1]
            tags = args[2:]
            if len(tags) == 0:
                raise IndexError

            self.tags = self.parse_tags(tags)
        except IndexError:
            raise

    def parse_tags(self, tags):
        parsed = {}
        for e, tag in enumerate(tags):
            try:
                container, tag = tag.split(':')
            except ValueError:
                container = e
                tag = tag
            parsed[container] = tag
        return parsed

    def create_deployment(self, service, params):
        deploy = Deployment()
        data = deploy.create_deployment(self.cluster, service,
                                        {'tags': self.tags})
        self.save_cmd_details(data, params)
        return data

    def create_group_deployment(self, group, params):
        deploy = ServiceGroupDeploy()
        data = deploy.deploy_service_group(self.cluster, group,
                                           {'tags': self.tags})
        if 'message' in data:
            return {'message': data['message']}

        for msg in data['messages']:
            self.save_cmd_details(msg, params)
        return data

    def save_cmd_details(self, data, params):
        if 'deployment_id' in data:
            deployment_id = data['deployment_id']
            item = Notifications(deployment_id,
                                 cmd_channel_id=params['channel_id'],
                                 cmd_response_url=params['response_url'],
                                 cmd_username=params['user_name']
                                 )
            item.put_item()

    def help(self):
        help_text = 'Usage: `deploy [cluster] [service] [tags]...`\n'
        examples_text = 'Examples:\n' \
            '`deploy cluster1 srv1 tag1` - deploy a single positional ' \
            'tag. The first container in the service is going to be ' \
            'updated.\n' \
            '`deploy cluster1 srv1 tag1 tag2` - deploy two positional ' \
            'containers. The first and second containers will be updated.\n' \
            '`deploy cluster1 srv1 container1:tag1 container2:tag2` - ' \
            'deploy two containers by name. Useful if you want to be ' \
            'explicit ' \
            'and/or you need to deploy to a specific container(s) in a ' \
            'a service without updating the rest of the containers.'

        return {'attachments': [{'text': help_text}, {'text': examples_text}]}
