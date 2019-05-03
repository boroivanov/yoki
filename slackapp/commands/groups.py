import ast
import os
import requests


YOKI_API = os.getenv('YOKI_API')


class SlackCommand(object):
    def _list_all_groups(self, args):
        url = f'{YOKI_API}/service-groups'
        return requests.get(url)

    def _list_group(self, args):
        url = f'{YOKI_API}/service-groups/{args[0]}'
        return requests.get(url)

    def _store_new_group(self, args):
        self.color = 'good'
        url = f'{YOKI_API}/service-groups/{args[0]}'
        services = ' '.join(args[1:])
        return requests.post(url, json={'services': services})

    def _delete_group(self, args):
        self.color = 'warning'
        url = f'{YOKI_API}/service-groups/{args[0]}'
        r = self._list_group(args)
        requests.delete(url)
        return r

    def create_service_group_line(self, sg):
        services = ' '.join(sg['services'])
        return f"{sg['group']}  {services}"

    def prepare_message(self, data):
        if 'serviceGroup' in data:
            sg = data['serviceGroup']
            if sg == 'Not found.':
                return self.message(sg)
            text = self.create_service_group_line(sg)
        else:
            lines = []
            for sg in data['serviceGroups']:
                line = self.create_service_group_line(sg)
                lines.append(line)
            text = '\n'.join(lines)
            if len(lines) == 0:
                return self.message('No groups found.')
        return self.message(text)

    def message(self, text):
        return {
            'response_type': 'ephemeral',
            'text': 'Service groups: ',
            'attachments': [
                {
                    'text': text,
                    'color': self.color,
                }
            ]
        }

    def run(self, args, params):
        self.color = 'grey'

        if len(args) == 1:
            if args[0] == 'help':
                return self.help()
            r = self._list_group(args)
        elif len(args) >= 2:
            if args[-1] == '-d':
                r = self._delete_group(args)
            else:
                r = self._store_new_group(args)
        else:
            r = self._list_all_groups(args)

        data = ast.literal_eval(r.text)
        if 'serviceGroups' in data or 'serviceGroup' in data:
            return self.prepare_message(data)
        return self.message(r.text)

    def help(self):
        help_text = 'Usage: `groups [group] [service]...`\n' \
            'Options:\n\t-d\tDelete a group\n'
        examples_text = 'Examples:\n' \
            '`groups` - list all service groups\n' \
            '`groups [group]` - list a specific service group\n' \
            '`groups [group] [service]...` - create/update ' \
            'new group with one or more services\n' \
            '`groups [group] -d` - delete a group'

        return {'attachments': [{'text': help_text}, {'text': examples_text}]}
