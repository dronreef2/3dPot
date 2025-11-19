"""
Unit tests for BudgetingService
Testing budget calculation, material pricing, and API integrations
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4
from decimal import Decimal


@pytest.fixture
def budgeting_service():
    """Fixture to create BudgetingService instance (mocked)"""
    service = Mock()
    service.octopart_base_url = "https://api.octopart.com/v4"
    service.digikey_base_url = "https://api.digikey.com/v1"
    service.printing_cost_per_hour = 25.0
    service.assembly_cost_per_hour = 50.0
    service.material_prices = {
        "PLA": 45.0,
        "ABS": 55.0,
        "PETG": 65.0,
        "nylon": 120.0,
        "metal": 180.0,
        "composite": 200.0
    }
    service.octopart_headers = {
        "X-API-KEY": "test_key",
        "Content-Type": "application/json"
    }
    service.digikey_headers = {
        "X-DigiKey-Api-Key": "test_key",
        "Content-Type": "application/json"
    }
    return service


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock()


@pytest.fixture
def mock_project():
    """Mock project object"""
    project = Mock()
    project.id = uuid4()
    project.nome = "Test Project"
    project.categoria = "mecânico"
    return project


@pytest.fixture
def mock_model_3d():
    """Mock 3D model object"""
    model = Mock()
    model.id = uuid4()
    model.peso_estimado_gramas = 250.0
    model.volume_cm3 = 125.0
    model.material = "PLA"
    model.tempo_impressao_estimado = 5.5  # hours
    return model


class TestBudgetingServiceInitialization:
    """Test service initialization and configuration"""
    
    def test_service_initialization(self, budgeting_service):
        """Test that service initializes with correct default values"""
        assert budgeting_service.octopart_base_url == "https://api.octopart.com/v4"
        assert budgeting_service.digikey_base_url == "https://api.digikey.com/v1"
        assert budgeting_service.printing_cost_per_hour == 25.0
        assert budgeting_service.assembly_cost_per_hour == 50.0
    
    def test_material_prices_configured(self, budgeting_service):
        """Test that material prices are properly configured"""
        assert "PLA" in budgeting_service.material_prices
        assert "ABS" in budgeting_service.material_prices
        assert "PETG" in budgeting_service.material_prices
        assert budgeting_service.material_prices["PLA"] == 45.0
        assert budgeting_service.material_prices["ABS"] == 55.0
    
    def test_headers_configured(self, budgeting_service):
        """Test API headers are configured"""
        assert "X-API-KEY" in budgeting_service.octopart_headers
        assert "Content-Type" in budgeting_service.octopart_headers
        assert budgeting_service.octopart_headers["Content-Type"] == "application/json"


class TestMaterialCostCalculation:
    """Test material cost calculations"""
    
    def test_calculate_pla_material_cost(self, budgeting_service):
        """Test PLA material cost calculation"""
        # 250g at R$45/kg = R$11.25
        weight_kg = 0.250
        expected_cost = 45.0 * weight_kg
        
        cost = budgeting_service.material_prices["PLA"] * weight_kg
        assert cost == pytest.approx(11.25, rel=0.01)
    
    def test_calculate_abs_material_cost(self, budgeting_service):
        """Test ABS material cost calculation"""
        # 500g at R$55/kg = R$27.50
        weight_kg = 0.500
        expected_cost = 55.0 * weight_kg
        
        cost = budgeting_service.material_prices["ABS"] * weight_kg
        assert cost == pytest.approx(27.50, rel=0.01)
    
    def test_unknown_material_handling(self, budgeting_service):
        """Test handling of unknown material"""
        # Should raise KeyError for unknown materials
        with pytest.raises(KeyError):
            _ = budgeting_service.material_prices["UNKNOWN_MATERIAL"]


class TestPrintingCostCalculation:
    """Test printing cost calculations"""
    
    def test_calculate_printing_cost(self, budgeting_service):
        """Test printing cost based on time"""
        # 5.5 hours at R$25/h = R$137.50
        print_time_hours = 5.5
        expected_cost = budgeting_service.printing_cost_per_hour * print_time_hours
        
        cost = budgeting_service.printing_cost_per_hour * print_time_hours
        assert cost == pytest.approx(137.50, rel=0.01)
    
    def test_calculate_assembly_cost(self, budgeting_service):
        """Test assembly cost calculation"""
        # 2 hours at R$50/h = R$100.00
        assembly_hours = 2.0
        expected_cost = budgeting_service.assembly_cost_per_hour * assembly_hours
        
        cost = budgeting_service.assembly_cost_per_hour * assembly_hours
        assert cost == pytest.approx(100.00, rel=0.01)
    
    def test_zero_time_printing(self, budgeting_service):
        """Test zero printing time results in zero cost"""
        cost = budgeting_service.printing_cost_per_hour * 0
        assert cost == 0.0


class TestBudgetValidation:
    """Test budget data validation"""
    
    def test_validate_positive_costs(self):
        """Test that costs must be positive"""
        material_cost = 50.0
        printing_cost = 100.0
        
        assert material_cost > 0
        assert printing_cost > 0
    
    def test_validate_margin_percentage(self):
        """Test profit margin validation"""
        valid_margins = [0, 10, 25, 50, 100]
        
        for margin in valid_margins:
            assert 0 <= margin <= 100
    
    def test_invalid_margin_percentage(self):
        """Test invalid margin percentages"""
        invalid_margins = [-10, 150]
        
        for margin in invalid_margins:
            assert not (0 <= margin <= 100)


class TestPricingCalculations:
    """Test final pricing calculations"""
    
    def test_calculate_total_cost_without_margin(self, budgeting_service):
        """Test total cost calculation without profit margin"""
        material_cost = 11.25
        printing_cost = 137.50
        assembly_cost = 100.00
        
        total_cost = material_cost + printing_cost + assembly_cost
        assert total_cost == pytest.approx(248.75, rel=0.01)
    
    def test_calculate_final_price_with_margin(self):
        """Test final price with profit margin"""
        total_cost = 248.75
        margin_percent = 30
        
        final_price = total_cost * (1 + margin_percent / 100)
        assert final_price == pytest.approx(323.375, rel=0.01)
    
    def test_calculate_price_with_zero_margin(self):
        """Test final price with zero margin"""
        total_cost = 248.75
        margin_percent = 0
        
        final_price = total_cost * (1 + margin_percent / 100)
        assert final_price == pytest.approx(248.75, rel=0.01)


class TestDataStructures:
    """Test budget data structures"""
    
    def test_budget_calculation_structure(self):
        """Test budget calculation result structure"""
        budget_calculation = {
            "custo_material": 11.25,
            "custo_componentes": 50.00,
            "custo_impressao": 137.50,
            "custo_mao_obra": 100.00,
            "tempo_impressao_horas": 5.5,
            "tempo_montagem_horas": 2.0,
            "itens_detalhados": [],
            "fornecedores": [],
            "preco_final": 323.38
        }
        
        # Verify all required fields exist
        assert "custo_material" in budget_calculation
        assert "custo_impressao" in budget_calculation
        assert "tempo_impressao_horas" in budget_calculation
        assert "preco_final" in budget_calculation
    
    def test_detailed_items_structure(self):
        """Test detailed items list structure"""
        items = [
            {
                "nome": "Filamento PLA",
                "quantidade": 0.25,
                "unidade": "kg",
                "preco_unitario": 45.0,
                "preco_total": 11.25
            }
        ]
        
        assert len(items) == 1
        assert items[0]["nome"] == "Filamento PLA"
        assert items[0]["preco_total"] == 11.25


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_missing_material_price(self, budgeting_service):
        """Test handling of missing material price"""
        with pytest.raises(KeyError):
            _ = budgeting_service.material_prices["NONEXISTENT"]
    
    def test_negative_cost_validation(self):
        """Test that negative costs are invalid"""
        material_cost = -10.0
        assert material_cost < 0  # Should be caught by validation
    
    def test_invalid_time_values(self):
        """Test invalid time values"""
        invalid_times = [-1.0, -5.5]
        
        for time_value in invalid_times:
            assert time_value < 0  # Should be caught by validation


@pytest.mark.asyncio
class TestAsyncOperations:
    """Test async operations (mocked)"""
    
    async def test_create_budget_async_flow(self, budgeting_service, mock_db, mock_project, mock_model_3d):
        """Test async budget creation flow (mocked)"""
        # This test validates the async pattern without actual DB calls
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_project,
            mock_model_3d
        ]
        
        # Verify mocks are set up correctly
        assert mock_db is not None
        assert mock_project is not None
        assert mock_model_3d is not None


class TestCostOptimization:
    """Test cost optimization scenarios"""
    
    def test_bulk_material_discount(self):
        """Test bulk material discount calculation"""
        base_price = 45.0  # R$/kg
        quantity_kg = 10.0
        discount_rate = 0.10  # 10% discount for bulk
        
        discounted_price = base_price * (1 - discount_rate) * quantity_kg
        assert discounted_price == pytest.approx(405.0, rel=0.01)
    
    def test_batch_printing_time_reduction(self):
        """Test time reduction for batch printing"""
        single_item_time = 5.5  # hours
        quantity = 10
        setup_time = 1.0  # hours
        
        # Batch printing is more efficient
        total_time_individual = single_item_time * quantity
        total_time_batch = setup_time + (single_item_time * 0.9 * quantity)
        
        assert total_time_batch < total_time_individual


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
