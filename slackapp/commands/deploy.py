from slackapp.lib.command_helpers import DeployCommand


class SlackCommand(DeployCommand):

    def run(self, args, params):
        try:
            self.parse_args(args)
        except IndexError:
            return self.help()

        data = self.create_deployment(self.service, params)

        return {'response_type': 'ephemeral', 'text': data['message']}

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
