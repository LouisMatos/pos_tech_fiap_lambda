import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    if 'cpf' not in event:
        return {
            "statusCode": 400,
            "body": "Missing 'cpf' in the request",
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
            }
        }

    cpf = event['cpf']

    logger.info(cpf)

    return {
        "statusCode": 200,
        "body": cpf,
        headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": true,
        }
    }
