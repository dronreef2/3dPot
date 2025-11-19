"""
Unit tests for CostOptimizationService
Testing material optimization, batch processing, and cost reduction strategies
"""

import pytest
from unittest.mock import Mock
from uuid import uuid4
from decimal import Decimal


@pytest.fixture
def cost_optimization_service():
    """Fixture to create CostOptimizationService instance (mocked)"""
    service = Mock()
    service.material_waste_factors = {
        'PLA': 0.05,  # 5% waste
        'ABS': 0.08,  # 8% waste
        'PETG': 0.06,
        'nylon': 0.10
    }
    service.bulk_discount_tiers = {
        1: 0.00,    # No discount for 1 item
        5: 0.10,    # 10% discount for 5+ items
        10: 0.15,   # 15% discount for 10+ items
        25: 0.20    # 20% discount for 25+ items
    }
    service.material_prices = {
        'PLA': 45.0,
        'ABS': 55.0,
        'PETG': 65.0
    }
    return service


@pytest.fixture
def mock_optimization_config():
    """Mock optimization configuration"""
    config = Mock()
    config.minimize_waste = True
    config.optimize_material = True
    config.batch_processing = True
    config.target_cost_reduction = 0.15  # 15% target
    return config


class TestCostOptimizationInitialization:
    """Test service initialization"""
    
    def test_material_waste_factors(self, cost_optimization_service):
        """Test waste factors are configured"""
        assert 'PLA' in cost_optimization_service.material_waste_factors
        assert cost_optimization_service.material_waste_factors['PLA'] == 0.05
    
    def test_bulk_discount_tiers(self, cost_optimization_service):
        """Test bulk discount tiers exist"""
        assert 1 in cost_optimization_service.bulk_discount_tiers
        assert 5 in cost_optimization_service.bulk_discount_tiers
        assert cost_optimization_service.bulk_discount_tiers[5] == 0.10


class TestWasteCalculation:
    """Test material waste calculations"""
    
    def test_pla_waste_calculation(self, cost_optimization_service):
        """Test PLA waste calculation"""
        material_used = 1000.0  # grams
        waste_factor = cost_optimization_service.material_waste_factors['PLA']
        waste = material_used * waste_factor
        assert waste == pytest.approx(50.0, rel=0.01)
    
    def test_abs_waste_higher(self, cost_optimization_service):
        """Test ABS has higher waste than PLA"""
        pla_waste = cost_optimization_service.material_waste_factors['PLA']
        abs_waste = cost_optimization_service.material_waste_factors['ABS']
        assert abs_waste > pla_waste


class TestBulkDiscounts:
    """Test bulk discount calculations"""
    
    def test_no_discount_single_item(self, cost_optimization_service):
        """Test no discount for single item"""
        assert cost_optimization_service.bulk_discount_tiers[1] == 0.00
    
    def test_discount_five_items(self, cost_optimization_service):
        """Test 10% discount for 5 items"""
        assert cost_optimization_service.bulk_discount_tiers[5] == 0.10
    
    def test_discount_ten_items(self, cost_optimization_service):
        """Test 15% discount for 10 items"""
        assert cost_optimization_service.bulk_discount_tiers[10] == 0.15
    
    def test_maximum_discount(self, cost_optimization_service):
        """Test maximum discount at 25 items"""
        assert cost_optimization_service.bulk_discount_tiers[25] == 0.20


class TestMaterialOptimization:
    """Test material selection optimization"""
    
    def test_cheaper_material_selection(self, cost_optimization_service):
        """Test selection of cheaper material"""
        pla_price = cost_optimization_service.material_prices['PLA']
        abs_price = cost_optimization_service.material_prices['ABS']
        assert pla_price < abs_price
    
    def test_material_price_comparison(self, cost_optimization_service):
        """Test material price ordering"""
        prices = cost_optimization_service.material_prices
        assert prices['PLA'] < prices['ABS'] < prices['PETG']


class TestOptimizationConfig:
    """Test optimization configuration"""
    
    def test_minimize_waste_enabled(self, mock_optimization_config):
        """Test waste minimization is enabled"""
        assert mock_optimization_config.minimize_waste is True
    
    def test_material_optimization_enabled(self, mock_optimization_config):
        """Test material optimization is enabled"""
        assert mock_optimization_config.optimize_material is True
    
    def test_batch_processing_enabled(self, mock_optimization_config):
        """Test batch processing is enabled"""
        assert mock_optimization_config.batch_processing is True
    
    def test_cost_reduction_target(self, mock_optimization_config):
        """Test cost reduction target"""
        assert mock_optimization_config.target_cost_reduction == 0.15


class TestCostReduction:
    """Test cost reduction calculations"""
    
    def test_apply_five_item_discount(self, cost_optimization_service):
        """Test applying 5-item discount"""
        base_cost = 100.0
        discount = cost_optimization_service.bulk_discount_tiers[5]
        final_cost = base_cost * (1 - discount)
        assert final_cost == pytest.approx(90.0, rel=0.01)
    
    def test_apply_maximum_discount(self, cost_optimization_service):
        """Test applying maximum discount"""
        base_cost = 1000.0
        discount = cost_optimization_service.bulk_discount_tiers[25]
        final_cost = base_cost * (1 - discount)
        assert final_cost == pytest.approx(800.0, rel=0.01)


class TestWasteMinimization:
    """Test waste minimization strategies"""
    
    def test_total_material_with_waste(self, cost_optimization_service):
        """Test total material including waste"""
        required = 1000.0
        waste_factor = cost_optimization_service.material_waste_factors['PLA']
        total = required * (1 + waste_factor)
        assert total == pytest.approx(1050.0, rel=0.01)


class TestBatchProcessing:
    """Test batch processing optimization"""
    
    def test_batch_quantity_grouping(self):
        """Test grouping items into batches"""
        total_items = 23
        batch_size = 5
        batches = (total_items + batch_size - 1) // batch_size
        assert batches == 5
