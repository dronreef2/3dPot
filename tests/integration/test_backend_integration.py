#!/usr/bin/env python3
"""
Testes de Integração do Backend - 3dPot v2.0
Consolidação dos testes de integração principais do backend.

Este arquivo substitui:
- test_integration.py
- test_integration_core.py
- test_integration_final.py

Mantendo apenas cenários relevantes e únicos.
"""

import os
import sys
from pathlib import Path
import pytest

# Adicionar backend ao path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestBackendCore:
    """Testes de integração dos componentes core do backend."""
    
    def test_configuration_loading(self):
        """Testa se as configurações do sistema são carregadas corretamente."""
        try:
            from backend.core.config import settings, DATABASE_URL, SECRET_KEY
            
            assert settings is not None
            assert settings.API_PREFIX is not None
            assert DATABASE_URL is not None
            assert SECRET_KEY is not None
            assert len(SECRET_KEY) > 0
        except ImportError as e:
            pytest.skip(f"Configurações requerem dependências não instaladas: {str(e)[:50]}")
    
    def test_database_models_import(self):
        """Testa se os modelos do banco de dados podem ser importados."""
        try:
            from backend.models import Base, User, Project, Conversation
            
            assert Base is not None
            assert User is not None
            assert Project is not None
            assert Conversation is not None
        except ImportError as e:
            pytest.skip(f"Modelos requerem dependências não instaladas: {str(e)[:50]}")
    
    def test_schemas_import(self):
        """Testa se os schemas Pydantic podem ser importados."""
        try:
            from backend.schemas import UserCreate, User, ProjectCreate, Project
            
            assert UserCreate is not None
            assert User is not None
            assert ProjectCreate is not None
            assert Project is not None
        except ImportError as e:
            pytest.skip(f"Schemas requerem dependências não instaladas: {str(e)[:50]}")
    
    def test_routers_import(self):
        """Testa se todas as rotas principais podem ser importadas."""
        try:
            from backend.routers.auth import router as auth_router
            from backend.routers.conversational import router as conversational_router
            from backend.routers.modeling import router as modeling_router
            from backend.routers.simulation import router as simulation_router
            from backend.routers.budgeting import router as budgeting_router
            
            assert auth_router is not None
            assert conversational_router is not None
            assert modeling_router is not None
            assert simulation_router is not None
            assert budgeting_router is not None
        except ImportError as e:
            pytest.skip(f"Routers requerem dependências não instaladas: {str(e)[:50]}")
    
    def test_core_services_import(self):
        """Testa se os serviços core podem ser importados."""
        try:
            from backend.services.auth_service import AuthenticationService
            from backend.services.conversational_service import ConversationalService
            from backend.services.budgeting_service import BudgetingService
            
            assert AuthenticationService is not None
            assert ConversationalService is not None
            assert BudgetingService is not None
        except ImportError as e:
            pytest.skip(f"Serviços requerem dependências não instaladas: {str(e)[:50]}")
    
    def test_3d_services_import_optional(self):
        """Testa importação de serviços 3D (opcional se dependências não instaladas)."""
        try:
            from backend.services.modeling_service import ModelingService
            from backend.services.print3d_service import Print3DService
            from backend.services.simulation_service import SimulationService
            
            assert ModelingService is not None
            assert Print3DService is not None
            assert SimulationService is not None
        except ImportError as e:
            # Serviços 3D são opcionais
            pytest.skip(f"Serviços 3D não disponíveis: {str(e)[:50]}")


class TestBackendStructure:
    """Testes de estrutura de arquivos do backend."""
    
    @pytest.fixture
    def project_root(self):
        """Retorna o diretório raiz do projeto."""
        return Path(__file__).parent.parent.parent
    
    def test_critical_files_exist(self, project_root):
        """Verifica se todos os arquivos críticos do backend existem."""
        critical_files = [
            "backend/main.py",
            "backend/models/__init__.py",
            "backend/schemas/__init__.py",
            "backend/routers/auth.py",
            "backend/routers/conversational.py",
            "backend/routers/modeling.py",
            "backend/routers/simulation.py",
            "backend/routers/budgeting.py",
            "backend/core/config.py",
            "backend/middleware/auth.py",
            "backend/services/auth_service.py",
            "backend/services/budgeting_service.py",
        ]
        
        missing_files = []
        for file_path in critical_files:
            full_path = project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        assert len(missing_files) == 0, f"Arquivos críticos faltando: {missing_files}"
    
    def test_service_files_exist(self, project_root):
        """Verifica se os arquivos de serviço principais existem."""
        services_dir = project_root / "backend" / "services"
        
        expected_services = [
            "auth_service.py",
            "budgeting_service.py",
            "conversational_service.py",
            "modeling_service.py",
            "print3d_service.py",
            "simulation_service.py",
            "production_service.py",
        ]
        
        for service_file in expected_services:
            service_path = services_dir / service_file
            assert service_path.exists(), f"Serviço {service_file} não encontrado"


class TestFastAPIApplication:
    """Testes da aplicação FastAPI."""
    
    def test_fastapi_app_creation(self):
        """Testa se a aplicação FastAPI pode ser criada."""
        try:
            from backend.main import app
            
            assert app is not None
            assert hasattr(app, 'routes')
        except ImportError as e:
            pytest.skip(f"FastAPI app requer dependências não instaladas: {str(e)[:50]}")
    
    def test_app_has_openapi_schema(self):
        """Testa se a aplicação tem schema OpenAPI."""
        try:
            from backend.main import app
            
            openapi_schema = app.openapi()
            
            assert openapi_schema is not None
            assert 'paths' in openapi_schema
            assert 'info' in openapi_schema
        except ImportError as e:
            pytest.skip(f"OpenAPI schema requer dependências não instaladas: {str(e)[:50]}")


class TestDependencies:
    """Testa dependências Python críticas."""
    
    def test_core_dependencies_available(self):
        """Verifica se as dependências core estão disponíveis."""
        core_deps = [
            ("fastapi", "FastAPI"),
            ("pydantic", "Pydantic"),
            ("sqlalchemy", "SQLAlchemy"),
        ]
        
        missing = []
        for module_name, friendly_name in core_deps:
            try:
                __import__(module_name)
            except ImportError:
                missing.append(friendly_name)
        
        if missing:
            pytest.skip(f"Dependências não instaladas: {', '.join(missing)}")
    
    def test_optional_3d_dependencies(self):
        """Verifica dependências 3D opcionais."""
        optional_deps = [
            ("trimesh", "Trimesh"),
            ("numpy", "NumPy"),
        ]
        
        available = []
        unavailable = []
        
        for module_name, friendly_name in optional_deps:
            try:
                __import__(module_name)
                available.append(friendly_name)
            except ImportError:
                unavailable.append(friendly_name)
        
        # Não falhamos o teste, apenas reportamos
        if unavailable:
            pytest.skip(
                f"Dependências 3D não disponíveis: {', '.join(unavailable)}"
            )


if __name__ == "__main__":
    print("🔍 TESTE DE INTEGRAÇÃO - BACKEND 3DPOT V2.0")
    print("=" * 60)
    
    # Executar testes com pytest
    pytest.main([__file__, "-v", "--tb=short"])
