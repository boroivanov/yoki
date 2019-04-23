import os
import json
import logging


log = logging.getLogger()
log.setLevel(os.getenv('LOG_LEVEL', logging.INFO))


def lambda_handler(event, context):
    log.info('Here is the event:')
    log.info(json.dumps(event))
