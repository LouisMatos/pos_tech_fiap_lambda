import datetime
import json
from unittest.mock import patch, MagicMock

import jwt

import lambda_function as lf


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------

def test_validar_cpf_valid():
    # CPF numericamente valido (digitos verificadores corretos)
    assert lf.validar_cpf('529.982.247-25') is True


def test_validar_cpf_wrong_length():
    assert lf.validar_cpf('123') is False


def test_validar_cpf_all_same_digits():
    assert lf.validar_cpf('111.111.111-11') is False


def test_validar_cpf_bad_check_digits():
    # Mesmo comprimento, digitos verificadores errados
    assert lf.validar_cpf('123.456.789-00') is False


def test_validar_cpf_1_only_checks_length():
    assert lf.validar_cpf_1('529.982.247-25') is True
    assert lf.validar_cpf_1('123') is False


def test_validar_email_1_valid():
    assert lf.validar_email_1('fulano@example.com') is True


def test_validar_email_1_invalid():
    assert lf.validar_email_1('nao-eh-email') is False
    assert lf.validar_email_1('fulano@') is False


def test_validar_nome_1_valid():
    assert lf.validar_nome_1('João da Silva') is True


def test_validar_nome_1_invalid():
    assert lf.validar_nome_1('João123') is False
    assert lf.validar_nome_1('João_Silva!') is False


# ---------------------------------------------------------------------------
# verify_jwt
# ---------------------------------------------------------------------------

def test_verify_jwt_valid_token():
    payload = {
        'cpf': '52998224725',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=2),
    }
    token = jwt.encode(payload, lf.SECRET_KEY, algorithm='HS256')
    decoded = lf.verify_jwt(token)
    assert decoded['cpf'] == '52998224725'


def test_verify_jwt_expired_token():
    payload = {
        'cpf': '52998224725',
        'exp': datetime.datetime.utcnow() - datetime.timedelta(minutes=2),
    }
    token = jwt.encode(payload, lf.SECRET_KEY, algorithm='HS256')
    result = lf.verify_jwt(token)
    assert result == {'error': 'Token expired'}


def test_verify_jwt_invalid_token():
    result = lf.verify_jwt('not-a-real-token')
    assert result == {'error': 'Invalid token'}


# ---------------------------------------------------------------------------
# gerar_token_jwt_lambda / lambda_handler routing for /jwt
# ---------------------------------------------------------------------------

def test_lambda_handler_jwt_route_success():
    event = {
        'resource': '/jwt',
        'httpMethod': 'POST',
        'body': json.dumps({'cpf': '529.982.247-25'}),
    }
    response = lf.lambda_handler(event, None)
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'token' in body
    decoded = jwt.decode(body['token'], lf.SECRET_KEY, algorithms=['HS256'])
    assert decoded['cpf'] == '529.982.247-25'


def test_lambda_handler_jwt_route_missing_body():
    event = {'resource': '/jwt', 'httpMethod': 'POST'}
    response = lf.lambda_handler(event, None)
    assert response['statusCode'] == 400
    assert 'body' in json.loads(response['body'])['message']


def test_lambda_handler_jwt_route_invalid_json_body():
    event = {'resource': '/jwt', 'httpMethod': 'POST', 'body': 'not-json'}
    response = lf.lambda_handler(event, None)
    assert response['statusCode'] == 400
    assert 'invalido' in json.loads(response['body'])['message']


def test_lambda_handler_jwt_route_invalid_cpf():
    event = {
        'resource': '/jwt',
        'httpMethod': 'POST',
        'body': json.dumps({'cpf': '123'}),
    }
    response = lf.lambda_handler(event, None)
    assert response['statusCode'] == 400


# ---------------------------------------------------------------------------
# lambda_handler routing when resource does not match any known route
# ---------------------------------------------------------------------------

def test_lambda_handler_unmatched_route_returns_none():
    event = {'resource': '/unknown', 'httpMethod': 'POST'}
    assert lf.lambda_handler(event, None) is None


def test_lambda_handler_missing_resource_key_raises_keyerror():
    event = {'httpMethod': 'POST'}
    try:
        lf.lambda_handler(event, None)
        assert False, 'expected KeyError'
    except KeyError:
        pass


# ---------------------------------------------------------------------------
# salvar_cliente_lambda / lambda_handler routing for /cliente (POST)
# ---------------------------------------------------------------------------

def _valid_token():
    payload = {
        'cpf': '52998224725',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=2),
    }
    return jwt.encode(payload, lf.SECRET_KEY, algorithm='HS256')


@patch('lambda_function.dynamodb')
def test_lambda_handler_cliente_route_success(mock_dynamodb):
    mock_table = MagicMock()
    mock_table.get_item.return_value = {}  # cliente ainda nao existe
    mock_dynamodb.Table.return_value = mock_table

    event = {
        'resource': '/cliente',
        'httpMethod': 'POST',
        'headers': {'Authorization': f'Bearer {_valid_token()}'},
        'body': json.dumps({
            'cpf': '529.982.247-25',
            'email': 'fulano@example.com',
            'nome': 'Fulano de Tal',
        }),
    }
    response = lf.lambda_handler(event, None)
    assert response['statusCode'] == 200
    mock_table.put_item.assert_called_once()


@patch('lambda_function.dynamodb')
def test_salvar_cliente_lambda_no_token(mock_dynamodb):
    event = {'resource': '/cliente', 'httpMethod': 'POST', 'headers': {}}
    response = lf.lambda_handler(event, None)
    assert response['statusCode'] == 401


@patch('lambda_function.dynamodb')
def test_salvar_cliente_lambda_invalid_token(mock_dynamodb):
    event = {
        'resource': '/cliente',
        'httpMethod': 'POST',
        'headers': {'Authorization': 'Bearer not-a-real-token'},
    }
    response = lf.lambda_handler(event, None)
    assert response['statusCode'] == 401


@patch('lambda_function.dynamodb')
def test_salvar_cliente_lambda_missing_fields(mock_dynamodb):
    event = {
        'resource': '/cliente',
        'httpMethod': 'POST',
        'headers': {'Authorization': f'Bearer {_valid_token()}'},
        'body': json.dumps({'cpf': '529.982.247-25'}),
    }
    response = lf.lambda_handler(event, None)
    assert response['statusCode'] == 400


@patch('lambda_function.dynamodb')
def test_salvar_cliente_lambda_already_exists(mock_dynamodb):
    mock_table = MagicMock()
    mock_table.get_item.return_value = {'Item': {'cpf': '52998224725'}}
    mock_dynamodb.Table.return_value = mock_table

    event = {
        'resource': '/cliente',
        'httpMethod': 'POST',
        'headers': {'Authorization': f'Bearer {_valid_token()}'},
        'body': json.dumps({
            'cpf': '529.982.247-25',
            'email': 'fulano@example.com',
            'nome': 'Fulano de Tal',
        }),
    }
    response = lf.lambda_handler(event, None)
    assert response['statusCode'] == 400
    body = json.loads(response['body'])
    assert 'cadastrado' in body['message']


# ---------------------------------------------------------------------------
# pegar_cliente_lambda / lambda_handler routing for /cliente/{cpf} (GET)
# ---------------------------------------------------------------------------

@patch('lambda_function.dynamodb')
def test_lambda_handler_get_cliente_found(mock_dynamodb):
    mock_table = MagicMock()
    mock_table.get_item.return_value = {'Item': {'cpf': '52998224725', 'nome': 'Fulano'}}
    mock_dynamodb.Table.return_value = mock_table

    event = {
        'resource': '/cliente/{cpf}',
        'httpMethod': 'GET',
        'pathParameters': {'cpf': '529.982.247-25'},
    }
    response = lf.lambda_handler(event, None)
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert body['cpf'] == '52998224725'


@patch('lambda_function.dynamodb')
def test_lambda_handler_get_cliente_not_found(mock_dynamodb):
    mock_table = MagicMock()
    mock_table.get_item.return_value = {}
    mock_dynamodb.Table.return_value = mock_table

    event = {
        'resource': '/cliente/{cpf}',
        'httpMethod': 'GET',
        'pathParameters': {'cpf': '52998224725'},
    }
    response = lf.lambda_handler(event, None)
    assert response['statusCode'] == 404
