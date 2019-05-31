import os
from resources.deployment import DeploymentList


REGION = os.environ.get('AWS_REGION', 'us-east-1')

help_text = 'Rollback a service.'


class SlackCommand(object):

    def run(self, args, params):
        try:
            cluster, service = args
        except ValueError:
            return self.help()

        params = {
            'IndexName': 'cluster-service-index',
            'Limit': 5,
        }

        dl = DeploymentList()
        res = dl.list_deployments(cluster, service, params)

        attachments = []
        for d in res['deployments']:
            value = {
                'cluster': d['cluster'],
                'service': d['service'],
                'images': {e: v for (e, v) in enumerate(d['images'])},
            }
            attachments.append(
                {
                    'title': f"[{d['definition'].split(':')[-1]}]"
                    f" {' '.join(d['images'])}",
                    'title_link': self.td_url(d['definition']),
                    'footer': f"ecs {d['launchType'].lower()}"
                    f" {d['definition']} {d['deployment']} {d['createdAt']}",
                    'callback_id': 'rollback',
                    'attachment_type': 'default',
                    'actions': [
                        {
                            'name': 'rollback',
                            'text': 'Redeploy images',
                            'type': 'button',
                            'value': str(value),
                        }
                    ]

                }
            )

        return {
            'response_type': 'ephemeral',
            'text': f'Deployments for {cluster} {service}',
            'attachments': attachments,
        }

    def td_url(self, definition):
        return f'https://console.aws.amazon.com/ecs/home?region=' \
            f'{REGION}#/taskDefinitions/' \
            f"{definition.replace(':', '/')}"

    def help(self):
        help_text = 'Usage: `rollback [cluster] [service]`\n'

        return {'attachments': [{'text': help_text}]}
