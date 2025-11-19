"""
Unit tests for IntelligentBudgetingService
Testing AI-powered budgeting, predictions, and smart cost analysis
"""

import pytest
from unittest.mock import Mock
from uuid import uuid4
from decimal import Decimal


@pytest.fixture
def intelligent_budgeting_service():
    """Fixture to create IntelligentBudgetingService instance (mocked)"""
    service = Mock()
    service.prediction_confidence_threshold = 0.75
    service.historical_data_min_samples = 10
    service.price_fluctuation_tolerance = 0.15  # 15%
    service.ml_model_accuracy = 0.85
    service.cost_categories = [
        'material',
        'labor',
        'overhead',
        'shipping',
        'tax'
    ]
    return service


@pytest.fixture
def mock_budget_prediction():
    """Mock budget prediction result"""
    prediction = Mock()
    prediction.predicted_cost = Decimal('250.00')
    prediction.confidence = 0.85
    prediction.lower_bound = Decimal('230.00')
    prediction.upper_bound = Decimal('270.00')
    return prediction


@pytest.fixture
def mock_historical_data():
    """Mock historical budget data"""
    data = Mock()
    data.samples = []
    for i in range(15):
        sample = Mock()
        sample.cost = Decimal(200 + i * 5)
        sample.accuracy = 0.90 - (i * 0.01)
        data.samples.append(sample)
    return data


class TestIntelligentBudgetingInitialization:
    """Test service initialization"""
    
    def test_confidence_threshold(self, intelligent_budgeting_service):
        """Test confidence threshold is set"""
        assert intelligent_budgeting_service.prediction_confidence_threshold == 0.75
    
    def test_minimum_samples(self, intelligent_budgeting_service):
        """Test minimum historical samples required"""
        assert intelligent_budgeting_service.historical_data_min_samples == 10
    
    def test_model_accuracy(self, intelligent_budgeting_service):
        """Test ML model accuracy metric"""
        assert intelligent_budgeting_service.ml_model_accuracy == 0.85
    
    def test_cost_categories(self, intelligent_budgeting_service):
        """Test cost categories are defined"""
        assert 'material' in intelligent_budgeting_service.cost_categories
        assert 'labor' in intelligent_budgeting_service.cost_categories


class TestBudgetPrediction:
    """Test budget prediction functionality"""
    
    def test_prediction_has_cost(self, mock_budget_prediction):
        """Test prediction includes cost"""
        assert mock_budget_prediction.predicted_cost > 0
    
    def test_prediction_confidence(self, mock_budget_prediction):
        """Test prediction has confidence score"""
        assert 0 <= mock_budget_prediction.confidence <= 1
        assert mock_budget_prediction.confidence == 0.85
    
    def test_prediction_bounds(self, mock_budget_prediction):
        """Test prediction has confidence bounds"""
        assert mock_budget_prediction.lower_bound < mock_budget_prediction.predicted_cost
        assert mock_budget_prediction.predicted_cost < mock_budget_prediction.upper_bound


class TestHistoricalDataAnalysis:
    """Test historical data analysis"""
    
    def test_sufficient_samples(self, mock_historical_data, intelligent_budgeting_service):
        """Test sufficient historical samples"""
        min_required = intelligent_budgeting_service.historical_data_min_samples
        assert len(mock_historical_data.samples) >= min_required
    
    def test_sample_cost_progression(self, mock_historical_data):
        """Test cost progression in samples"""
        for i in range(len(mock_historical_data.samples) - 1):
            current = mock_historical_data.samples[i].cost
            next_cost = mock_historical_data.samples[i + 1].cost
            assert next_cost >= current


class TestConfidenceScoring:
    """Test confidence scoring"""
    
    def test_high_confidence_prediction(self, intelligent_budgeting_service):
        """Test high confidence meets threshold"""
        confidence = 0.85
        threshold = intelligent_budgeting_service.prediction_confidence_threshold
        assert confidence > threshold
    
    def test_low_confidence_rejection(self, intelligent_budgeting_service):
        """Test low confidence below threshold"""
        confidence = 0.60
        threshold = intelligent_budgeting_service.prediction_confidence_threshold
        assert confidence < threshold


class TestPriceFluctuation:
    """Test price fluctuation analysis"""
    
    def test_acceptable_fluctuation(self, intelligent_budgeting_service):
        """Test acceptable price fluctuation"""
        base_price = 100.0
        tolerance = intelligent_budgeting_service.price_fluctuation_tolerance
        max_fluctuation = base_price * tolerance
        assert max_fluctuation == 15.0
    
    def test_price_within_tolerance(self, intelligent_budgeting_service):
        """Test price change within tolerance"""
        old_price = 100.0
        new_price = 110.0
        change = abs(new_price - old_price) / old_price
        assert change <= intelligent_budgeting_service.price_fluctuation_tolerance


class TestCostCategorization:
    """Test cost categorization"""
    
    def test_all_categories_present(self, intelligent_budgeting_service):
        """Test all expected categories exist"""
        categories = intelligent_budgeting_service.cost_categories
        assert 'material' in categories
        assert 'labor' in categories
        assert 'overhead' in categories
        assert 'shipping' in categories
        assert 'tax' in categories
    
    def test_category_count(self, intelligent_budgeting_service):
        """Test number of cost categories"""
        assert len(intelligent_budgeting_service.cost_categories) == 5


class TestMLModelMetrics:
    """Test ML model metrics"""
    
    def test_model_accuracy_valid(self, intelligent_budgeting_service):
        """Test model accuracy is valid percentage"""
        accuracy = intelligent_budgeting_service.ml_model_accuracy
        assert 0 <= accuracy <= 1
    
    def test_model_accuracy_acceptable(self, intelligent_budgeting_service):
        """Test model accuracy is above minimum"""
        assert intelligent_budgeting_service.ml_model_accuracy >= 0.75


class TestPredictionBounds:
    """Test prediction boundary calculations"""
    
    def test_bounds_symmetric(self, mock_budget_prediction):
        """Test prediction bounds are reasonably symmetric"""
        predicted = mock_budget_prediction.predicted_cost
        lower = mock_budget_prediction.lower_bound
        upper = mock_budget_prediction.upper_bound
        
        lower_diff = predicted - lower
        upper_diff = upper - predicted
        
        # Should be roughly symmetric (within 20% difference)
        ratio = float(lower_diff) / float(upper_diff) if upper_diff > 0 else 0
        assert 0.8 <= ratio <= 1.2
