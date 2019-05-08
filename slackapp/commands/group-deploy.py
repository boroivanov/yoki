from slackapp.lib.command_helpers import DeployCommand
from resources.group import ServiceGroup


class SlackCommand(DeployCommand):

    def run(self, args, params):
        try:
            self.parse_args(args)
        except IndexError:
            return self.help()

        sg = ServiceGroup()
        res = sg.get(self.service)

        if isinstance(res, tuple):
            return {'text': res[0]}

        services = res['serviceGroup']['services'][0].split()

        messages = []
        for service in services:
            msg = self.create_deployment(service, params)
            messages.append(msg)

        attachments = []
        for msg in messages:
            attachments.append({'text': msg['message']})

        return {'attachments': attachments}

    def help(self):
        help_text = 'Usage: `group-deploy [cluster] [group] [tags]...`\n'
        examples_text = 'Examples:\n' \
            '`group-deploy cluster1 grp1 tag1` - deploy a single positional ' \
            'tag. The first container in the service is going to be ' \
            'updated.\n' \
            '`group-deploy cluster1 grp1 tag1 tag2` - deploy two positional ' \
            'containers. The first and second containers will be updated.\n' \
            '`group-deploy cluster1 grp1 container1:tag1 container2:tag2` - ' \
            'deploy two containers by name. Useful if you want to be ' \
            'explicit ' \
            'and/or you need to deploy to a specific container(s) in a ' \
            'a service without updating the rest of the containers.'

        return {'attachments': [{'text': help_text}, {'text': examples_text}]}
