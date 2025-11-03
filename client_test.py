import unittest
from client import get_client  # notre fonction client

class TestClient(unittest.TestCase):
    def test_client_valide(self):
        get_client(1)

    def test_client_invalide(self):
        get_client(-1)

if __name__ == '__main__':
    unittest.main()
