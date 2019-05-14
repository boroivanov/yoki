from resources.group import ServiceGroup, ServiceGroupList


help_text = 'Manage service groups.'


class SlackCommand(object):
    def _list_all_groups(self, args):
        sg_list = ServiceGroupList()
        return sg_list.get()

    def _list_group(self, args):
        sg = ServiceGroup()
        return sg.get_group(args[0])

    def _store_new_group(self, args):
        self.color = 'good'
        sg = ServiceGroup()
        return sg.update_group(args[0], {'services': args[1:]})

    def _delete_group(self, args):
        self.color = 'warning'
        sg = ServiceGroup()
        res = sg.get_group(args[0])
        sg.delete_group(args[0])
        return res

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
            res = self._list_group(args)
        elif len(args) >= 2:
            if args[-1] == '-d':
                res = self._delete_group(args)
            else:
                res = self._store_new_group(args)
        else:
            res = self._list_all_groups(args)

        if 'serviceGroups' in res or 'serviceGroup' in res:
            return self.prepare_message(res)
        return self.message(res[0]['message'])

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
