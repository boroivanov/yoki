import json
from resources.deployment import Deployment
from models.notifications import Notifications


class SlackAction(object):

    def run(self, action_value, params):
        av = json.loads(action_value)
        av['images'] = {e: v.split(':')[-1]
                        for (e, v) in enumerate(av['images'])}
        data = self.create_deployment(**av, params=params)

        return {'response_type': 'ephemeral', 'text': data['message']}

    def create_deployment(self, cluster, service, images, params):
        deploy = Deployment()
        data = deploy.create_deployment(cluster, service, {'tags': images})
        self.save_cmd_details(data, params)
        return data

    def save_cmd_details(self, data, params):
        if 'deployment_id' in data:
            deployment_id = data['deployment_id']
            item = Notifications(deployment_id,
                                 cmd_channel_id=params['channel']['id'],
                                 cmd_response_url=params['response_url'],
                                 cmd_username=params['user']['name']
                                 )
            item.put_item()
