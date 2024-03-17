import json
import boto3
import re
import os
import jwt
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

# Supõe-se que a SECRET_KEY seja definida em uma variável de ambiente por segurança
SECRET_KEY = os.environ.get('JWT_SECRET', 'FIAP123')

# Inicializa o cliente do DynamoDB
dynamodb = boto3.resource('dynamodb')

def validar_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

def validar_nome(nome):
    regex = r'^[A-Za-záàâãéèêíïóôõöúçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑ ]+$'
    return re.match(regex, nome) is not None

def validar_cpf(cpf):
    cpf = re.sub('[^0-9]', '', cpf)  # Remove caracteres não numéricos
    return len(cpf) == 11

def verify_jwt(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return {'error': 'Token expired'}
    except jwt.InvalidTokenError:
        return {'error': 'Invalid token'}

def salvar_cliente_lambda(event):
    headers = event.get('headers', {})
    token = next((value.split(' ')[1] for key, value in headers.items() if key.lower() == 'authorization'), None)

    if token is None:
        return {
            'statusCode': 401,
            'body': json.dumps({'message': 'Unauthorized: No token provided'})
        }

    verification_result = verify_jwt(token)
    if 'error' in verification_result:
        return {
            'statusCode': 401,
            'body': json.dumps({'message': verification_result['error']})
        }

    try:
        body = json.loads(event.get('body', '{}'))
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Invalid request body or not in JSON format'})
        }

    cpf = body.get('cpf')
    email = body.get('email')
    nome = body.get('nome')

    if not cpf or not email or not nome:
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Nome, CPF e e-mail são obrigatórios.'})
        }
    if not validar_cpf(cpf):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'CPF inválido. O CPF deve conter 11 dígitos numéricos.'})
        }
    if not validar_email(email):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Email Invalido.'})
        }
    if not validar_nome(nome):
        return {
            'statusCode': 400,
            'body': json.dumps({'message': 'Nome invalido. O nome não deve conter numeros ou caracteres especiais.'})
        }

    table = dynamodb.Table('Customers')
    try:
        response = table.get_item(Key={'cpf': cpf})
        if 'Item' in response:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'CPF já cadastrado.'})
            }
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'statusCode': 500, 'body': json.dumps({'message': 'Erro de acesso ao DynamoDB.'})}

    try:
        item = {
            'cpf': cpf,
            'nome': nome,
            'email': email
        }
        table.put_item(Item=item)
        return {
            'statusCode': 200,
            'body': json.dumps({'message': ' Criado com sucesso.'})
        }
    except ClientError as e:
        print(e.response['Error']['Message'])
        return {'statusCode': 500, 'body': json.dumps({'message': 'Error inserting customer into DynamoDB.'})}
