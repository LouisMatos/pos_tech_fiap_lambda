import json
import boto3
from botocore.exceptions import ClientError

# Inicializa o cliente do DynamoDB
dynamodb = boto3.resource('dynamodb')


def pegar_cliente_lambda(event, context):
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