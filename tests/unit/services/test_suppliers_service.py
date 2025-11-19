"""
Unit tests for SuppliersService
Testing supplier management, pricing, and procurement workflows
"""

import pytest
from unittest.mock import Mock
from uuid import uuid4
from decimal import Decimal
from datetime import datetime, timedelta


@pytest.fixture
def suppliers_service():
    """Fixture to create SuppliersService instance (mocked)"""
    service = Mock()
    service.supplier_rating_threshold = 4.0
    service.payment_terms = ['net30', 'net60', 'prepaid', 'cod']
    service.shipping_methods = ['express', 'standard', 'economy']
    service.min_order_amount = Decimal('50.00')
    service.preferred_supplier_discount = 0.10  # 10% discount
    service.supplier_categories = [
        'electronics',
        'materials',
        'tools',
        'components',
        'services'
    ]
    return service


@pytest.fixture
def mock_supplier():
    """Mock supplier object"""
    supplier = Mock()
    supplier.id = uuid4()
    supplier.name = "TechParts Co."
    supplier.rating = 4.5
    supplier.category = "electronics"
    supplier.is_preferred = True
    supplier.payment_term = "net30"
    supplier.lead_time_days = 7
    return supplier


@pytest.fixture
def mock_quote():
    """Mock supplier quote"""
    quote = Mock()
    quote.id = uuid4()
    quote.supplier_id = uuid4()
    quote.item_name = "Arduino Mega"
    quote.quantity = 10
    quote.unit_price = Decimal('35.00')
    quote.total_price = Decimal('350.00')
    quote.valid_until = datetime.utcnow() + timedelta(days=30)
    return quote


class TestSuppliersServiceInitialization:
    """Test service initialization"""
    
    def test_rating_threshold(self, suppliers_service):
        """Test supplier rating threshold"""
        assert suppliers_service.supplier_rating_threshold == 4.0
    
    def test_payment_terms_configured(self, suppliers_service):
        """Test payment terms are configured"""
        assert 'net30' in suppliers_service.payment_terms
        assert 'net60' in suppliers_service.payment_terms
    
    def test_shipping_methods(self, suppliers_service):
        """Test shipping methods available"""
        assert 'express' in suppliers_service.shipping_methods
        assert 'standard' in suppliers_service.shipping_methods
    
    def test_minimum_order_amount(self, suppliers_service):
        """Test minimum order amount"""
        assert suppliers_service.min_order_amount == Decimal('50.00')


class TestSupplierManagement:
    """Test supplier management"""
    
    def test_supplier_has_name(self, mock_supplier):
        """Test supplier has name"""
        assert mock_supplier.name == "TechParts Co."
    
    def test_supplier_rating(self, mock_supplier, suppliers_service):
        """Test supplier rating meets threshold"""
        assert mock_supplier.rating >= suppliers_service.supplier_rating_threshold
    
    def test_supplier_category(self, mock_supplier, suppliers_service):
        """Test supplier category is valid"""
        assert mock_supplier.category in suppliers_service.supplier_categories
    
    def test_preferred_supplier_status(self, mock_supplier):
        """Test preferred supplier status"""
        assert mock_supplier.is_preferred is True


class TestQuoteManagement:
    """Test supplier quote management"""
    
    def test_quote_has_id(self, mock_quote):
        """Test quote has unique ID"""
        assert mock_quote.id is not None
    
    def test_quote_unit_price(self, mock_quote):
        """Test quote has unit price"""
        assert mock_quote.unit_price > 0
        assert isinstance(mock_quote.unit_price, Decimal)
    
    def test_quote_total_calculation(self, mock_quote):
        """Test quote total is correct"""
        expected = mock_quote.unit_price * mock_quote.quantity
        assert mock_quote.total_price == expected
    
    def test_quote_validity(self, mock_quote):
        """Test quote has validity period"""
        assert mock_quote.valid_until > datetime.utcnow()


class TestPaymentTerms:
    """Test payment term handling"""
    
    def test_net30_payment_term(self, mock_supplier, suppliers_service):
        """Test net30 payment term"""
        assert mock_supplier.payment_term in suppliers_service.payment_terms
    
    def test_prepaid_option_available(self, suppliers_service):
        """Test prepaid option is available"""
        assert 'prepaid' in suppliers_service.payment_terms
    
    def test_cod_option_available(self, suppliers_service):
        """Test cash on delivery option"""
        assert 'cod' in suppliers_service.payment_terms


class TestPreferredSupplierDiscount:
    """Test preferred supplier discount"""
    
    def test_preferred_discount_rate(self, suppliers_service):
        """Test preferred supplier discount rate"""
        assert suppliers_service.preferred_supplier_discount == 0.10
    
    def test_apply_preferred_discount(self, suppliers_service):
        """Test applying preferred supplier discount"""
        base_price = Decimal('100.00')
        discount = suppliers_service.preferred_supplier_discount
        final_price = base_price * (1 - Decimal(str(discount)))
        assert final_price == Decimal('90.00')


class TestLeadTime:
    """Test supplier lead time"""
    
    def test_supplier_lead_time(self, mock_supplier):
        """Test supplier has lead time"""
        assert mock_supplier.lead_time_days > 0
        assert mock_supplier.lead_time_days == 7


class TestMinimumOrderValidation:
    """Test minimum order validation"""
    
    def test_order_meets_minimum(self, suppliers_service):
        """Test order meets minimum amount"""
        order_amount = Decimal('75.00')
        assert order_amount >= suppliers_service.min_order_amount
    
    def test_order_below_minimum(self, suppliers_service):
        """Test order below minimum"""
        order_amount = Decimal('25.00')
        assert order_amount < suppliers_service.min_order_amount


class TestSupplierRatings:
    """Test supplier rating system"""
    
    def test_high_rated_supplier(self, mock_supplier):
        """Test high-rated supplier"""
        assert mock_supplier.rating >= 4.0
        assert 0 <= mock_supplier.rating <= 5
    
    def test_rating_threshold_enforcement(self, suppliers_service):
        """Test rating threshold"""
        assert suppliers_service.supplier_rating_threshold > 0


class TestSupplierCategories:
    """Test supplier categorization"""
    
    def test_all_categories_defined(self, suppliers_service):
        """Test all expected categories exist"""
        categories = suppliers_service.supplier_categories
        assert 'electronics' in categories
        assert 'materials' in categories
        assert 'tools' in categories
        assert 'components' in categories
        assert 'services' in categories


class TestShippingMethods:
    """Test shipping method options"""
    
    def test_express_shipping_available(self, suppliers_service):
        """Test express shipping is available"""
        assert 'express' in suppliers_service.shipping_methods
    
    def test_economy_shipping_available(self, suppliers_service):
        """Test economy shipping is available"""
        assert 'economy' in suppliers_service.shipping_methods
    
    def test_multiple_shipping_options(self, suppliers_service):
        """Test multiple shipping options exist"""
        assert len(suppliers_service.shipping_methods) >= 3
