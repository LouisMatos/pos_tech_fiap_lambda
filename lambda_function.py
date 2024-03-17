import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):

    cpf = event['cpf']

    logger.info(cpf)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": cpf,
        headers: {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": true,
        }
    }
