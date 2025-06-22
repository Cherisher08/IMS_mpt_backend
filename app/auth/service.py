from app.auth.adapters.jwt_service import JwtService
from app.auth.repository.repository import AuthRepository
from app.config import database
from app.config import env


class Service:
    def __init__(self, auth_user_repository: AuthRepository):
        self.repository = auth_user_repository
        self.jwt_svc = JwtService(algorithm="HS256", secret=env.secret_key, expiration=10)


def get_service():
    auth_repository = AuthRepository(database=database)
    svc = Service(auth_user_repository=auth_repository)
    return svc
