import json
import jwt
import datetime
import os
import re

# Defina sua chave secreta de forma segura
SECRET_KEY = os.environ.get('JWT_SECRET', 'FIAP123')


def validar_cpf(cpf):
    # Remove caracteres não numéricos
    cpf = re.sub('[^0-9]', '', cpf)

    # Verifica o tamanho do CPF
    if len(cpf) != 11:
        return False

    # Verifica se todas as entradas no CPF são iguais (inválido)
    if cpf == cpf[0] * len(cpf):
        return False

    # Calcula e verifica os dígitos verificadores
    for i in range(9, 11):
        value = sum((int(cpf[num]) * ((i + 1) - num) for num in range(0, i)))
        digit = ((value * 10) % 11) % 10
        if digit != int(cpf[i]):
            return False
    return True


def lambda_handler(event, context):
    print("Received event:", event)  # Para propósitos de depuração

    # Verifica se 'body' está presente no evento e se ele é uma string
    if 'body' in event and event['body']:
        try:
            # Tenta carregar o corpo como JSON
            body = json.loads(event['body'])
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'JSON Formato invalido.'})
            }
    else:
        # Retorna um erro se 'body' não estiver presente ou estiver vazio
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'body de envio vazio.'})
        }

    cpf_usuario = body.get('cpf')
    if not cpf_usuario or not validar_cpf(cpf_usuario):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'CPF inválido ou obrigatório.'})
        }

    # Dados a serem incluídos no token
    payload = {
        'cpf': cpf_usuario,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=2)
    }

    # Gera o token JWT
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    # Retorna o token gerado como resposta
    return {
        'statusCode': 200,
        'body': json.dumps({'token': token})
    }

