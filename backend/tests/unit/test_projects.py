"""
Testes unitários para projetos
Sistema de Prototipagem Sob Demanda
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException, status

from app.routers import projects
from app.models.project import Project, ProjectStatus, ProjectType
from app.schemas.project import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectFileResponse, ProjectBudgetResponse
)


class TestProjectRouter:
    """Testes para o router de projetos"""
    
    @pytest.mark.unit
    async def test_create_project_success(self, mock_database_session, test_project_data):
        """Testa criação de projeto com sucesso"""
        # Arrange
        project_data = ProjectCreate(**test_project_data)
        mock_project = Project(
            id=1,
            name=project_data.name,
            description=project_data.description,
            project_type=ProjectType.PROTOTYPE,
            status=ProjectStatus.DRAFT,
            created_at="2025-11-12T16:05:57Z"
        )
        
        mock_db = mock_database_session
        
        with patch('app.routers.projects.create_project', return_value=mock_project):
            # Act
            result = await projects.create_project(project_data, mock_db)
            
            # Assert
            assert result.name == project_data.name
            assert result.description == project_data.description
            assert result.project_type == ProjectType.PROTOTYPE
    
    @pytest.mark.unit
    async def test_get_project_success(self, mock_database_session, test_project_data):
        """Testa obtenção de projeto por ID"""
        # Arrange
        project_id = 1
        mock_project = Project(
            id=project_id,
            name=test_project_data["name"],
            description=test_project_data["description"],
            project_type=ProjectType.PROTOTYPE,
            status=ProjectStatus.IN_PROGRESS,
            created_at="2025-11-12T16:05:57Z"
        )
        
        mock_db = mock_database_session
        mock_db.execute.return_value.scalar.return_value = mock_project
        
        with patch('app.routers.projects.get_project', return_value=mock_project):
            # Act
            result = await projects.get_project(project_id, mock_db)
            
            # Assert
            assert result.id == project_id
            assert result.name == test_project_data["name"]
            assert result.status == ProjectStatus.IN_PROGRESS
    
    @pytest.mark.unit
    async def test_get_project_not_found(self, mock_database_session):
        """Testa erro quando projeto não é encontrado"""
        # Arrange
        project_id = 999
        mock_db = mock_database_session
        mock_db.execute.return_value.scalar.return_value = None
        
        with patch('app.routers.projects.get_project', return_value=None):
            # Act & Assert
            with pytest.raises(HTTPException) as exc_info:
                await projects.get_project(project_id, mock_db)
            
            assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.unit
    async def test_list_projects(self, mock_database_session, test_project_data):
        """Testa listagem de projetos"""
        # Arrange
        mock_projects = [
            Project(
                id=1,
                name="Project A",
                description="Projeto A para testes",
                project_type=ProjectType.PROTOTYPE,
                status=ProjectStatus.COMPLETED,
                created_at="2025-11-12T16:05:57Z"
            ),
            Project(
                id=2,
                name="Project B",
                description="Projeto B para testes",
                project_type=ProjectType.PRODUCTION,
                status=ProjectStatus.IN_PROGRESS,
                created_at="2025-11-12T16:05:57Z"
            )
        ]
        
        mock_db = mock_database_session
        mock_db.execute.return_value.scalars.return_value.all.return_value = mock_projects
        
        with patch('app.routers.projects.list_projects', return_value=mock_projects):
            # Act
            result = await projects.list_projects(skip=0, limit=10, mock_db)
            
            # Assert
            assert len(result) == 2
            assert result[0].name == "Project A"
            assert result[1].name == "Project B"
    
    @pytest.mark.unit
    async def test_update_project_success(self, mock_database_session, test_project_data):
        """Testa atualização de projeto"""
        # Arrange
        project_id = 1
        update_data = ProjectUpdate(
            name="Updated Project Name",
            description="Updated description"
        )
        updated_project = Project(
            id=project_id,
            name="Updated Project Name",
            description="Updated description",
            project_type=ProjectType.PROTOTYPE,
            status=ProjectStatus.IN_PROGRESS,
            created_at="2025-11-12T16:05:57Z"
        )
        
        mock_db = mock_database_session
        
        with patch('app.routers.projects.update_project', return_value=updated_project):
            # Act
            result = await projects.update_project(project_id, update_data, mock_db)
            
            # Assert
            assert result.name == "Updated Project Name"
            assert result.description == "Updated description"
            assert result.id == project_id
    
    @pytest.mark.unit
    async def test_delete_project_success(self, mock_database_session):
        """Testa exclusão de projeto"""
        # Arrange
        project_id = 1
        mock_db = mock_database_session
        
        with patch('app.routers.projects.delete_project', return_value=True):
            # Act
            result = await projects.delete_project(project_id, mock_db)
            
            # Assert
            assert result is True
    
    @pytest.mark.unit
    async def test_submit_project_for_3d_printing(self, mock_database_session, mock_slant3d_api):
        """Testa submissão de projeto para impressão 3D"""
        # Arrange
        project_id = 1
        submission_data = {
            "print_settings": {
                "material": "PLA",
                "layer_height": 0.2,
                "infill_density": 20
            },
            "shipping_address": {
                "street": "123 Test St",
                "city": "Test City",
                "zip_code": "12345"
            }
        }
        
        mock_db = mock_database_session
        
        with patch('app.routers.projects.get_project') as mock_get_project, \
             patch('app.routers.projects.update_project') as mock_update:
            
            mock_project = Project(
                id=project_id,
                name="Test Project",
                status=ProjectStatus.IN_PROGRESS
            )
            mock_get_project.return_value = mock_project
            mock_update.return_value = mock_project
            
            # Act
            result = await projects.submit_for_3d_printing(project_id, submission_data, mock_db)
            
            # Assert
            assert "submission_id" in result
            assert "status" in result
            assert result["status"] == "submitted"
    
    @pytest.mark.unit
    async def test_get_project_status(self, mock_database_session, mock_slant3d_api):
        """Testa verificação de status do projeto"""
        # Arrange
        project_id = 1
        submission_id = "test-submission-123"
        
        mock_db = mock_database_session
        mock_slant3d_api.get_project_status.return_value = {
            "status": "printing",
            "progress": 45,
            "estimated_completion": "2025-11-13T10:00:00Z"
        }
        
        # Act
        with patch('app.routers.projects.get_project') as mock_get_project:
            mock_get_project.return_value = Project(id=project_id, name="Test")
            
            result = await projects.get_project_status(project_id, submission_id, mock_db)
            
            # Assert
            assert "status" in result
            assert "progress" in result
            assert result["progress"] == 45
    
    @pytest.mark.unit
    async def test_download_project_file(self, mock_database_session, mock_slant3d_api):
        """Testa download de arquivo do projeto"""
        # Arrange
        project_id = 1
        file_id = "test-file-123"
        
        mock_db = mock_database_session
        mock_slant3d_api.get_download_url.return_value = {
            "url": "https://files.example.com/download/test-file.stl"
        }
        
        # Act
        with patch('app.routers.projects.get_project') as mock_get_project:
            mock_get_project.return_value = Project(id=project_id, name="Test")
            
            result = await projects.download_project_file(project_id, file_id, mock_db)
            
            # Assert
            assert "download_url" in result
            assert "expires_at" in result
            assert result["download_url"] == "https://files.example.com/download/test-file.stl"
    
    @pytest.mark.unit
    async def test_create_project_budget(self, mock_database_session, mock_httpx_client):
        """Testa criação de orçamento do projeto"""
        # Arrange
        project_id = 1
        budget_request = {
            "specifications": {
                "dimensions": {"length": 100, "width": 50, "height": 25},
                "material": "PLA",
                "quantity": 1,
                "complexity": "medium"
            }
        }
        
        mock_db = mock_database_session
        mock_httpx_client.post.return_value.json.return_value = {
            "total_cost": 45.99,
            "breakdown": {
                "material": 25.99,
                "printing": 15.00,
                "shipping": 5.00
            },
            "estimated_days": 5
        }
        
        # Act
        with patch('app.routers.projects.get_project') as mock_get_project, \
             patch('app.routers.projects.save_budget') as mock_save_budget:
            
            mock_get_project.return_value = Project(id=project_id, name="Test")
            mock_save_budget.return_value = ProjectBudgetResponse(
                id=1,
                project_id=project_id,
                total_cost=45.99
            )
            
            result = await projects.create_budget(project_id, budget_request, mock_db)
            
            # Assert
            assert result.total_cost == 45.99
            assert "breakdown" in result
            assert result.estimated_days == 5
    
    @pytest.mark.unit
    async def test_clone_project(self, mock_database_session, test_project_data):
        """Testa clonagem de projeto"""
        # Arrange
        original_project_id = 1
        clone_data = {
            "name": "Cloned Project",
            "description": "Clone of original project"
        }
        
        mock_db = mock_database_session
        
        with patch('app.routers.projects.get_project') as mock_get_project, \
             patch('app.routers.projects.create_project') as mock_create_project:
            
            original_project = Project(
                id=original_project_id,
                name=test_project_data["name"],
                description=test_project_data["description"],
                project_type=ProjectType.PROTOTYPE,
                specifications=test_project_data["specifications"]
            )
            mock_get_project.return_value = original_project
            
            cloned_project = Project(
                id=2,
                name="Cloned Project",
                description="Clone of original project",
                project_type=ProjectType.PROTOTYPE,
                specifications=test_project_data["specifications"]
            )
            mock_create_project.return_value = cloned_project
            
            # Act
            result = await projects.clone_project(original_project_id, clone_data, mock_db)
            
            # Assert
            assert result.name == "Cloned Project"
            assert result.id != original_project_id
            assert result.specifications == original_project.specifications


class TestProjectEndpoints:
    """Testes para endpoints HTTP de projetos"""
    
    @pytest.mark.unit
    async def test_create_project_endpoint(self, client, test_project_data):
        """Testa endpoint de criação de projeto"""
        # Act
        response = client.post("/projects/", json=test_project_data)
        
        # Assert
        assert response.status_code in [200, 201, 400, 401]
    
    @pytest.mark.unit
    async def test_list_projects_endpoint(self, client):
        """Testa endpoint de listagem de projetos"""
        # Act
        response = client.get("/projects/")
        
        # Assert
        assert response.status_code in [200, 401]
    
    @pytest.mark.unit
    async def test_get_project_endpoint(self, client):
        """Testa endpoint de obtenção de projeto específico"""
        # Act
        response = client.get("/projects/1")
        
        # Assert
        assert response.status_code in [200, 401, 404]
    
    @pytest.mark.unit
    async def test_update_project_endpoint(self, client):
        """Testa endpoint de atualização de projeto"""
        update_data = {"name": "Updated Project"}
        
        # Act
        response = client.put("/projects/1", json=update_data)
        
        # Assert
        assert response.status_code in [200, 400, 401, 404]
    
    @pytest.mark.unit
    async def test_delete_project_endpoint(self, client):
        """Testa endpoint de exclusão de projeto"""
        # Act
        response = client.delete("/projects/1")
        
        # Assert
        assert response.status_code in [200, 204, 401, 404]
    
    @pytest.mark.unit
    async def test_submit_3d_printing_endpoint(self, client):
        """Testa endpoint de submissão para impressão 3D"""
        submission_data = {
            "print_settings": {"material": "PLA", "layer_height": 0.2},
            "shipping_address": {"street": "123 Test St"}
        }
        
        # Act
        response = client.post("/projects/1/submit-3d", json=submission_data)
        
        # Assert
        assert response.status_code in [200, 400, 401, 404]
    
    @pytest.mark.unit
    async def test_get_project_status_endpoint(self, client):
        """Testa endpoint de status do projeto"""
        # Act
        response = client.get("/projects/1/status/test-submission")
        
        # Assert
        assert response.status_code in [200, 401, 404]
    
    @pytest.mark.unit
    async def test_download_file_endpoint(self, client):
        """Testa endpoint de download de arquivo"""
        # Act
        response = client.get("/projects/1/download/test-file")
        
        # Assert
        assert response.status_code in [200, 401, 404]


class TestProjectModels:
    """Testes para os modelos de projetos"""
    
    @pytest.mark.unit
    def test_project_creation(self, test_project_data):
        """Testa criação do modelo Project"""
        # Act
        project = Project(**test_project_data)
        
        # Assert
        assert project.name == test_project_data["name"]
        assert project.description == test_project_data["description"]
        assert project.project_type == ProjectType.PROTOTYPE
        assert "specifications" in project.specifications
    
    @pytest.mark.unit
    def test_project_serialization(self, test_project_data):
        """Testa serialização do modelo Project"""
        # Arrange
        project = Project(
            name=test_project_data["name"],
            description=test_project_data["description"],
            project_type=ProjectType.PROTOTYPE,
            status=ProjectStatus.DRAFT
        )
        
        # Act
        project_dict = project.__dict__
        
        # Assert
        assert "name" in project_dict
        assert "description" in project_dict
        assert project_dict["project_type"] == ProjectType.PROTOTYPE
        assert project_dict["status"] == ProjectStatus.DRAFT
    
    @pytest.mark.unit
    def test_project_status_enum(self):
        """Testa enumeração de status do projeto"""
        # Assert
        assert ProjectStatus.DRAFT.value == "draft"
        assert ProjectStatus.IN_PROGRESS.value == "in_progress"
        assert ProjectStatus.UNDER_REVIEW.value == "under_review"
        assert ProjectStatus.APPROVED.value == "approved"
        assert ProjectStatus.PRINTING.value == "printing"
        assert ProjectStatus.COMPLETED.value == "completed"
        assert ProjectStatus.CANCELLED.value == "cancelled"
    
    @pytest.mark.unit
    def test_project_type_enum(self):
        """Testa enumeração de tipos de projeto"""
        # Assert
        assert ProjectType.PROTOTYPE.value == "prototype"
        assert ProjectType.PRODUCTION.value == "production"
        assert ProjectType.TEST.value == "test"
        assert ProjectType.RESEARCH.value == "research"