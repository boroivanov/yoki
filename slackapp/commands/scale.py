from resources.scale import Scale
from models.notifications import Notifications


help_text = 'Scale a service.'


class SlackCommand(object):

    def run(self, args, params):
        try:
            cluster, service, count = args
            count = int(count)
        except ValueError:
            return self.help()

        scale = Scale()
        data = scale.scale_service(cluster, service, {'count': count})

        if 'deployment_id' in data:
            self.save_cmd_details(data, params)

        return {'response_type': 'ephemeral', 'text': data['message']}

    def save_cmd_details(self, data, params):
        deployment_id = data['deployment_id']
        item = Notifications(deployment_id,
                             cmd_channel_id=params['channel_id'],
                             cmd_response_url=params['response_url'],
                             cmd_username=params['user_name']
                             )
        item.put_item()

    def help(self):
        help_text = 'Usage: `scale [cluster] [service] [count]`\n'

        return {'attachments': [{'text': help_text}]}
