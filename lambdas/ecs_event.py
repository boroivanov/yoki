import os
import json
import logging

from models.ecs_event import EcsEvent, EcsEventTaskDigest


REGION = os.environ.get('AWS_REGION', 'us-east-1')
DIGEST_ITEM_TTL = os.getenv('DIGEST_ITEM_TTL', 2592000)
STATE_ITEM_TTL = os.getenv('STATE_ITEM_TTL', 86400)

log = logging.getLogger()
log.setLevel(os.getenv('LOG_LEVEL', logging.INFO))


def lambda_handler(event, context):
    log.info('Here is the event:')
    log.info(json.dumps(event))

    if event['source'] != 'aws.ecs':
        raise ValueError('Function only supports input from events'
                         ' with a source type of: aws.ecs')

    ecs_event = EcsEvent(event, REGION)
    item = ecs_event.put_item(STATE_ITEM_TTL)

    if item:
        digest = EcsEventTaskDigest(event, REGION)
        digest.put_item(DIGEST_ITEM_TTL)
