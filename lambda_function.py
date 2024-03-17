from wsgiref import headers

import requests
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    body = json.loads(event.get('body', '{}'))
    logger.info(body)

    cpf = body.get('cpf', '00000000000')

    logger.info(cpf)

    return {
        "statusCode": 200,
        "body": cpf,
        headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": 'true',
        }
    }
