import unittest
from unittest.mock import patch, MagicMock
from lambda_function import lambda_handler

class TestLambdaFunction(unittest.TestCase):

    @patch('lambda_function.logging')
    def test_lambda_handler(self, mock_logging):
        # Define o evento de teste
        event = {'cpf': '123.456.789-00'}

        # Define o contexto de teste
        context = {}

        # Chama a função lambda_handler com o evento e o contexto de teste
        result = lambda_handler(event, context)

        # Verifica se a função retornou o CPF esperado
        self.assertEqual(result, '123.456.789-00')

        # Verifica se a função registrou o CPF esperado
        mock_logging.getLogger.assert_called_once()
        mock_logging.getLogger.return_value.info.assert_called_once_with('123.456.789-00')

if __name__ == '__main__':
    unittest.main()