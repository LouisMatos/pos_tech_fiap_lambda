import requests

def handler(event, context):
    cpf = event['cpf']
    response = requests.get(f'https://external-api.com/authorize?cpf={cpf}')
    return response.json()