import unittest
from unittest.mock import patch
from src.main import handler

class TestHandler(unittest.TestCase):
    @patch('src.main.requests.get')
    def test_handler(self, mock_get):
        mock_get.return_value.json.return_value = {'authorized': True}
        event = {'cpf': '12345678901'}
        context = {}
        response = handler(event, context)
        self.assertEqual(response, {'authorized': True})
        mock_get.assert_called_with('https://external-api.com/authorize?cpf=12345678901')

if __name__ == '__main__':
    unittest.main()