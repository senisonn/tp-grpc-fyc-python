"""Example 6: Repository Pattern with PostgreSQL"""
import psycopg2
from psycopg2.extras import RealDictCursor
from dataclasses import dataclass

@dataclass
class User:
    id: str
    name: str
    email: str

class UserRepository:
    def __init__(self, connection_params):
        self.connection_params = connection_params
    
    def _get_connection(self):
        return psycopg2.connect(**self.connection_params)
    
    def create(self, user):
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    "INSERT INTO users (id, name, email) VALUES (%s, %s, %s) RETURNING *",
                    (user.id, user.name, user.email)
                )
                row = cursor.fetchone()
                conn.commit()
                return User(**row)
    
    def get_by_id(self, user_id):
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                row = cursor.fetchone()
                return User(**row) if row else None

# Usage in service:
# class UserService(user_pb2_grpc.UserServiceServicer):
#     def __init__(self):
#         self.repo = UserRepository(connection_params)
