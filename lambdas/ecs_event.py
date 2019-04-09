import json
import os

from models.ecs_event import EcsEvent

REGION = os.environ.get('AWS_REGION', 'us-east-1')
DIGEST_ITEM_TTL = os.getenv('DIGEST_ITEM_TTL', 2592000)
STATE_ITEM_TTL = os.getenv('STATE_ITEM_TTL', 86400)


def lambda_handler(event, context):
    print('Here is the event:')
    print(json.dumps(event))

    if event['source'] != 'aws.ecs':
        raise ValueError('Function only supports input from events'
                         ' with a source type of: aws.ecs')

    ecs_event = EcsEvent(event, REGION)
    ecs_event.put_item(DIGEST_ITEM_TTL)
