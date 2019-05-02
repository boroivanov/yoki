import os
import json
import logging

from slackapp.app import SlackTaskDigest

log = logging.getLogger()
log.setLevel(os.getenv('LOG_LEVEL', logging.INFO))

SLACK_TOKEN = os.environ.get('SLACK_TOKEN', '')
SLACK_CHANNEL = os.environ.get('SLACK_CHANNEL', 'general')


def lambda_handler(event, context):
    log.info('Here is the event:')
    log.info(json.dumps(event))

    if event['Records'][0]['eventName'] == 'REMOVE':
        log.info('Skipping REMOVE event.')
        return

    digest = SlackTaskDigest(SLACK_TOKEN, SLACK_CHANNEL, event)
    digest.post_to_slack()
