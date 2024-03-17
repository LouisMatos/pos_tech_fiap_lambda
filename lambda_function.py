import requests
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(event)
    body = json.loads(event.get('body', '{}'))
    logger.info(body)

    cpf = body.get('cpf', '00000000000')

    logger.info(cpf)

    resp = {
        "statusCode": 200,
        "body": cpf,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": 'true',
        }
    }

    return json.loads(json.dumps(resp, default=str))