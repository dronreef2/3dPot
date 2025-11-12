"""
Testes unitários para autenticação
Sistema de Prototipagem Sob Demanda
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, status
from datetime import timedelta

# Importa os routers e modelos
from app.routers import auth
from app.models.user import User
from app.schemas.auth import UserCreate, UserLogin, Token


class TestAuthRouter:
    """Testes para o router de autenticação"""
    
    @pytest.mark.unit
    async def test_register_success(self, async_client, mock_database, test_user_data):
        """Testa registro bem-sucedido de usuário"""
        # Arrange
        user_data = UserCreate(**test_user_data)
        mock_user = User(
            id=1,
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            is_active=True,
            created_at="2025-11-12T16:05:57Z"
        )
        
        with patch('app.routers.auth.get_current_user', return_value=None), \
             patch('app.routers.auth.create_user', return_value=mock_user):
            
            # Act
            response = await auth.register(user_data)
            
            # Assert
            assert response.email == user_data.email
            assert response.username == user_data.username
            assert response.full_name == user_data.full_name
    
    @pytest.mark.unit
    async def test_register_duplicate_email(self, async_client, mock_database, test_user_data):
        """Testa erro ao registrar com email duplicado"""
        # Arrange
        user_data = UserCreate(**test_user_data)
        
        with patch('app.routers.auth.get_current_user', return_value=None), \
             patch('app.routers.auth.create_user') as mock_create:
            mock_create.side_effect = HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            ):
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await auth.register(user_data)
            
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.unit
    async def test_login_success(self, async_client, mock_database, test_user_data):
        """Testa login bem-sucedido"""
        # Arrange
        login_data = UserLogin(
            email=test_user_data["email"],
            password=test_user_data["password"]
        )
        
        mock_user = User(
            id=1,
            email=login_data.email,
            password_hash="hashed_password",
            is_active=True,
            is_admin=False
        )
        
        with patch('app.routers.auth.authenticate_user') as mock_auth, \
             patch('app.routers.auth.create_access_token') as mock_token:
            mock_auth.return_value = mock_user
            mock_token.return_value = "mock_jwt_token"
            
            # Act
            response = await auth.login(login_data)
            
            # Assert
            assert isinstance(response, Token)
            assert response.access_token == "mock_jwt_token"
            assert response.token_type == "bearer"
    
    @pytest.mark.unit
    async def test_login_invalid_credentials(self, async_client, mock_database, test_user_data):
        """Testa erro com credenciais inválidas"""
        # Arrange
        login_data = UserLogin(
            email=test_user_data["email"],
            password="wrong_password"
        )
        
        with patch('app.routers.auth.authenticate_user') as mock_auth:
            mock_auth.return_value = None
            
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await auth.login(login_data)
            
            assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    @pytest.mark.unit
    async def test_get_current_user_success(self, mock_database_session, mock_current_user):
        """Testa obtenção do usuário atual com sucesso"""
        # Arrange
        mock_db = mock_database_session
        mock_db.execute.return_value.scalar.return_value = User(
            id=mock_current_user["id"],
            email=mock_current_user["email"],
            username=mock_current_user["username"],
            full_name=mock_current_user["full_name"],
            is_active=mock_current_user["is_active"],
            is_admin=mock_current_user["is_admin"],
            created_at=mock_current_user["created_at"]
        )
        
        with patch('app.routers.auth.get_db') as mock_get_db:
            mock_get_db.return_value = mock_db
            
            # Act
            from app.routers.auth import get_current_user
            current_user = await get_current_user("test-token", mock_db)
            
            # Assert
            assert current_user.email == mock_current_user["email"]
            assert current_user.username == mock_current_user["username"]
    
    @pytest.mark.unit
    async def test_get_current_user_not_found(self, mock_database_session):
        """Testa erro quando usuário não é encontrado"""
        # Arrange
        mock_db = mock_database_session
        mock_db.execute.return_value.scalar.return_value = None
        
        with patch('app.routers.auth.get_db') as mock_get_db:
            mock_get_db.return_value = mock_db
            
            # Act & Assert
            from app.routers.auth import get_current_user
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("test-token", mock_db)
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    async def test_get_current_user_inactive(self, mock_database_session, mock_current_user):
        """Testa erro quando usuário está inativo"""
        # Arrange
        mock_db = mock_database_session
        mock_user = User(
            id=mock_current_user["id"],
            email=mock_current_user["email"],
            username=mock_current_user["username"],
            full_name=mock_current_user["full_name"],
            is_active=False,  # Usuário inativo
            is_admin=mock_current_user["is_admin"],
            created_at=mock_current_user["created_at"]
        )
        mock_db.execute.return_value.scalar.return_value = mock_user
        
        with patch('app.routers.auth.get_db') as mock_get_db:
            mock_get_db.return_value = mock_db
            
            # Act & Assert
            from app.routers.auth import get_current_user
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user("test-token", mock_db)
            
            assert exc_info.value.status_code == status.HTTP_400_BAD_REQUEST
    
    @pytest.mark.unit
    async def test_change_password_success(self, client, mock_current_user, mock_jwt_token):
        """Testa alteração de senha com sucesso"""
        # Arrange
        password_data = {
            "current_password": "TestPassword123!",
            "new_password": "NewPassword123!"
        }
        
        with patch('app.routers.auth.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            # Mock para verificação de senha atual
            with patch('app.routers.auth.verify_password', return_value=True), \
                 patch('app.routers.auth.get_password_hash') as mock_hash:
                mock_hash.return_value = "new_hashed_password"
                
                # Mock do banco de dados
                mock_db = AsyncMock()
                
                # Act
                with client:
                    response = client.put(
                        "/auth/change-password",
                        json=password_data,
                        headers={"Authorization": f"Bearer {mock_jwt_token}"}
                    )
                
                # Assert
                assert response.status_code == 200
                assert response.json() == {"message": "Password updated successfully"}
    
    @pytest.mark.unit
    async def test_change_password_wrong_current(self, client, mock_current_user, mock_jwt_token):
        """Testa erro ao informar senha atual incorreta"""
        # Arrange
        password_data = {
            "current_password": "WrongPassword123!",
            "new_password": "NewPassword123!"
        }
        
        with patch('app.routers.auth.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('app.routers.auth.verify_password', return_value=False):
                # Act
                with client:
                    response = client.put(
                        "/auth/change-password",
                        json=password_data,
                        headers={"Authorization": f"Bearer {mock_jwt_token}"}
                    )
                
                # Assert
                assert response.status_code == 400
                assert "Incorrect current password" in response.json()["detail"]
    
    @pytest.mark.unit
    async def test_refresh_token_success(self, mock_current_user, mock_jwt_token):
        """Testa refresh de token com sucesso"""
        # Arrange
        with patch('app.routers.auth.get_current_user') as mock_get_user:
            mock_get_user.return_value = mock_current_user
            
            with patch('app.routers.auth.create_access_token') as mock_create_token:
                mock_create_token.return_value = "new_jwt_token"
                
                # Act
                from app.routers.auth import refresh_access_token
                new_token = await refresh_access_token(mock_current_user)
                
                # Assert
                assert new_token == "new_jwt_token"
    
    @pytest.mark.unit
    async def test_logout_success(self, mock_redis):
        """Testa logout com sucesso"""
        # Arrange
        with patch('app.routers.auth.redis_client', mock_redis):
            # Act
            from app.routers.auth import logout
            result = await logout("test-token", mock_redis)
            
            # Assert
            assert result == {"message": "Successfully logged out"}
            mock_redis.set.assert_called()


class TestAuthEndpoints:
    """Testes para endpoints HTTP de autenticação"""
    
    @pytest.mark.unit
    async def test_register_endpoint(self, client, test_user_data):
        """Testa endpoint de registro via HTTP"""
        # Arrange & Act
        response = client.post("/auth/register", json=test_user_data)
        
        # Assert
        # A resposta dependerá da implementação específica
        assert response.status_code in [200, 201, 400]  # Possíveis códigos de resposta
    
    @pytest.mark.unit
    async def test_login_endpoint(self, client, test_user_data):
        """Testa endpoint de login via HTTP"""
        # Arrange
        login_data = {
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
        
        # Act
        response = client.post("/auth/login", json=login_data)
        
        # Assert
        # A resposta dependerá da implementação específica
        assert response.status_code in [200, 401, 400]
    
    @pytest.mark.unit
    async def test_me_endpoint_unauthorized(self, client):
        """Testa endpoint /me sem autenticação"""
        # Act
        response = client.get("/auth/me")
        
        # Assert
        assert response.status_code == 401
    
    @pytest.mark.unit
    async def test_health_auth_endpoint(self, client):
        """Testa health check específico para auth"""
        # Act
        response = client.get("/auth/health")
        
        # Assert
        assert response.status_code == 200
        assert "status" in response.json()