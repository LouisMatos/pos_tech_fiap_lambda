import json
import jwt
import datetime
import os
import re
import json
import boto3
from botocore.exceptions import ClientError
import json
import boto3
import re
import os
import jwt
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

# Inicializa o cliente do DynamoDB
dynamodb = boto3.resource('dynamodb')

# Defina sua chave secreta de forma segura
SECRET_KEY = os.environ.get('JWT_SECRET', 'FIAP123')

def lambda_handler(event, context):

    # Extrai a rota e o método HTTP do evento
    rota = event['resource']
    metodo_http = event['httpMethod']

    # Imprime a rota e o método HTTP
    print(f'Rota: {rota}, Método HTTP: {metodo_http}')

    # Verifica se a rota contém "/jwt" e o método é "GET"
    if "/jwt" in rota and metodo_http == "GET":
        # Chama o método gerar_token_jwt_lambda e retorna a resposta
        return gerar_token_jwt_lambda(event)

    # Verifica se a rota contém "/cliente" e o método é "POST"
    elif "/cliente" in rota and metodo_http == "POST":
        # Chama o método pegar_cliente_lambda e retorna a resposta
        return pegar_cliente_lambda(event)

    # Verifica se a rota contém "/cliente/{cpf}" e o método é "GET"
    elif "/cliente/" in rota and metodo_http == "GET":
        # Chama o método salvar_cliente_lambda e retorna a resposta
        return salvar_cliente_lambda(event)

    # Rota não encontrada ----------------------------------------------
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


# Path: src/lambda_gera_jwt.py
def gerar_token_jwt_lambda(event):
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

# Path: src/lambda_salva_cliente.py
def pegar_cliente_lambda(event):
    # Nome da tabela DynamoDB
    table_name = 'Customers'
    table = dynamodb.Table(table_name)

    # Extrai o CPF do parâmetro de caminho da requisição
    cpf = event['pathParameters']['cpf']

    # Limpa o CPF para manter apenas dígitos
    cpf = ''.join(filter(str.isdigit, cpf))

    # Busca o cliente pelo CPF
    try:
        response = table.get_item(Key={'cpf': cpf})
        if 'Item' in response:
            # Retorna os dados do cliente encontrado
            return {
                'statusCode': 200,
                'body': json.dumps(response['Item'])
            }
        else:
            # Cliente não encontrado
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'Cliente não encontrado.'})
            }
    except ClientError as e:
        print(e.response['Error']['Message'])
        # Erro ao acessar o DynamoDB
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Erro ao buscar informações no banco de dados.'})
        }

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

# Path: src/lambda_salva_cliente.py
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
