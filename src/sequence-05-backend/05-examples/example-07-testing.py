"""Example 7: Testing with pytest"""
import pytest, grpc
from generated import user_pb2

class MockContext:
    def abort(self, code, details):
        raise grpc.RpcError(code, details)

def test_create_user_success():
    service = UserService()
    request = user_pb2.CreateUserRequest(
        name="Test User",
        email="test@example.com",
        password="SecurePass123"
    )
    response = service.CreateUser(request, MockContext())
    assert response.name == "Test User"
    assert response.email == "test@example.com"

def test_create_user_invalid_email():
    service = UserService()
    request = user_pb2.CreateUserRequest(
        name="Test",
        email="invalid",
        password="Pass123"
    )
    with pytest.raises(grpc.RpcError) as exc:
        service.CreateUser(request, MockContext())
    assert exc.value.code() == grpc.StatusCode.INVALID_ARGUMENT

@pytest.fixture
def user_service():
    return UserService()

def test_list_users_pagination(user_service):
    # Create 5 users
    for i in range(5):
        req = user_pb2.CreateUserRequest(
            name=f"User {i}",
            email=f"user{i}@example.com",
            password="Pass123"
        )
        user_service.CreateUser(req, MockContext())
    
    # Test pagination
    req = user_pb2.ListUsersRequest(page=1, page_size=2)
    resp = user_service.ListUsers(req, MockContext())
    assert len(resp.users) == 2
    assert resp.total_count == 5
