import requests
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    cpf = event['cpf']
    logger.info(cpf)
    return cpf
