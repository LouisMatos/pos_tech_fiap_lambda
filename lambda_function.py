from src.lambda_gera_jwt import gerar_token_jwt_lambda
from src.lambda_pega_cliente import pegar_cliente_lambda
from src.lambda_salva_cliente import salvar_cliente_lambda


def lambda_handler(event, context):

    # Extrai a rota e o método HTTP do evento
    rota = event['resource']
    metodo_http = event['httpMethod']

    # Imprime a rota e o método HTTP
    print(f'Rota: {rota}, Método HTTP: {metodo_http}')

    # Verifica se a rota contém "/jwt" e o método é "GET"
    if "/jwt" in rota and metodo_http == "GET":
        # Chama o método gerar_token_jwt_lambda e retorna a resposta
        return gerar_token_jwt_lambda(event, context)

    # Verifica se a rota contém "/cliente" e o método é "POST"
    elif "/cliente" in rota and metodo_http == "POST":
        # Chama o método pegar_cliente_lambda e retorna a resposta
        return pegar_cliente_lambda(event, context)

    # Verifica se a rota contém "/cliente/{cpf}" e o método é "GET"
    elif "/cliente/" in rota and metodo_http == "GET":
        # Chama o método salvar_cliente_lambda e retorna a resposta
        return salvar_cliente_lambda(event, context)
