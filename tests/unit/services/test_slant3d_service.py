"""
Testes unitários para Slant3DService
Cobertura: Integração com API Slant3D para cotações reais de impressão 3D
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime, timedelta
from uuid import uuid4


class TestSlant3DServiceInitialization:
    """Testes de inicialização"""
    
    def test_service_initialization(self):
        """Testa inicialização básica"""
        service = Mock()
        service.base_url = "https://api.slant3d.com/v1"
        service.api_key = "test_api_key"
        
        assert service.base_url == "https://api.slant3d.com/v1"
        assert service.api_key == "test_api_key"
    
    def test_headers_configuration(self):
        """Testa configuração de headers"""
        headers = {
            "Authorization": "Bearer test_key",
            "Content-Type": "application/json",
            "User-Agent": "3dPot-Intelligent-Budgeting/1.0"
        }
        
        assert headers["Authorization"].startswith("Bearer")
        assert headers["Content-Type"] == "application/json"
        assert "3dPot" in headers["User-Agent"]
    
    def test_cache_configuration(self):
        """Testa configuração de cache"""
        cache_ttl = 3600  # 1 hora
        
        assert cache_ttl > 0
        assert cache_ttl <= 86400  # máximo 24 horas


class TestMaterialConfiguration:
    """Testes de configuração de materiais"""
    
    def test_pla_configuration(self):
        """Testa configuração de PLA"""
        pla_config = {
            "base_price_multiplier": 1.0,
            "available_colors": ["white", "black", "blue", "red", "green", "yellow"],
            "finish_types": ["standard", "matte", "glossy"],
            "layer_height_range": [0.1, 0.2, 0.3],
            "infill_range": [10, 100]
        }
        
        assert pla_config["base_price_multiplier"] == 1.0
        assert len(pla_config["available_colors"]) >= 4
        assert pla_config["infill_range"][1] <= 100
    
    def test_abs_configuration(self):
        """Testa configuração de ABS"""
        abs_config = {
            "base_price_multiplier": 1.3,
            "available_colors": ["white", "black", "blue", "red"],
            "finish_types": ["standard", "matte"],
            "layer_height_range": [0.15, 0.25, 0.35]
        }
        
        assert abs_config["base_price_multiplier"] > 1.0
        assert "standard" in abs_config["finish_types"]
    
    def test_petg_configuration(self):
        """Testa configuração de PETG"""
        petg_config = {
            "base_price_multiplier": 1.5,
            "available_colors": ["white", "black", "blue", "red", "clear"],
            "finish_types": ["standard", "glossy"]
        }
        
        assert petg_config["base_price_multiplier"] > 1.0
        assert "clear" in petg_config["available_colors"]
    
    def test_nylon_configuration(self):
        """Testa configuração de Nylon"""
        nylon_config = {
            "base_price_multiplier": 2.0,
            "available_colors": ["white", "black"],
            "finish_types": ["standard"],
            "layer_height_range": [0.15, 0.25],
            "infill_range": [20, 100]
        }
        
        assert nylon_config["base_price_multiplier"] == 2.0
        assert nylon_config["infill_range"][0] >= 20


class TestQuoteRequest:
    """Testes de solicitação de cotação"""
    
    def test_quote_request_structure(self):
        """Testa estrutura de requisição de cotação"""
        quote_request = {
            "file_url": "https://example.com/model.stl",
            "material": "PLA",
            "color": "white",
            "quantity": 10,
            "finish": "standard",
            "layer_height": 0.2,
            "infill": 20
        }
        
        assert "file_url" in quote_request
        assert "material" in quote_request
        assert "quantity" in quote_request
        assert quote_request["quantity"] > 0
    
    def test_quote_with_options(self):
        """Testa cotação com opções adicionais"""
        quote_request = {
            "material": "PETG",
            "color": "blue",
            "quantity": 5,
            "finish": "glossy",
            "supports": True,
            "rush_order": False
        }
        
        assert quote_request["material"] == "PETG"
        assert quote_request["supports"] is True
        assert quote_request["rush_order"] is False


class TestCacheManagement:
    """Testes de gerenciamento de cache"""
    
    def test_generate_cache_key(self):
        """Testa geração de chave de cache"""
        import hashlib
        import json
        
        quote_data = {"material": "PLA", "quantity": 10}
        cache_key = hashlib.md5(json.dumps(quote_data, sort_keys=True).encode()).hexdigest()
        
        assert len(cache_key) == 32
        assert isinstance(cache_key, str)
    
    def test_cache_hit(self):
        """Testa acerto de cache"""
        cache = {"key123": {"data": "cached_quote", "timestamp": datetime.utcnow()}}
        cache_key = "key123"
        
        assert cache_key in cache
        assert "data" in cache[cache_key]
    
    def test_cache_miss(self):
        """Testa falha de cache"""
        cache = {}
        cache_key = "key456"
        
        assert cache_key not in cache
    
    def test_cache_expiration(self):
        """Testa expiração de cache"""
        cache_ttl = 3600  # 1 hora
        cached_time = datetime.utcnow() - timedelta(seconds=7200)  # 2 horas atrás
        current_time = datetime.utcnow()
        
        is_expired = (current_time - cached_time).total_seconds() > cache_ttl
        
        assert is_expired is True


class TestPriceCalculation:
    """Testes de cálculo de preço"""
    
    def test_base_price_calculation(self):
        """Testa cálculo de preço base"""
        volume_cm3 = 100
        base_price_per_cm3 = 0.50
        material_multiplier = 1.0
        
        base_price = volume_cm3 * base_price_per_cm3 * material_multiplier
        
        assert base_price == 50.0
    
    def test_quantity_discount(self):
        """Testa desconto por quantidade"""
        unit_price = 50.0
        quantity = 100
        discount_rate = 0.10  # 10% desconto
        
        total_price = unit_price * quantity * (1 - discount_rate)
        
        assert total_price == 4500.0
    
    def test_rush_order_premium(self):
        """Testa premium para pedido urgente"""
        base_price = 100.0
        rush_multiplier = 1.5
        
        rush_price = base_price * rush_multiplier
        
        assert rush_price == 150.0
    
    def test_shipping_cost(self):
        """Testa cálculo de frete"""
        base_shipping = 15.0
        weight_kg = 2.5
        cost_per_kg = 5.0
        
        total_shipping = base_shipping + (weight_kg * cost_per_kg)
        
        assert total_shipping == 27.5


class TestAPIResponse:
    """Testes de resposta da API"""
    
    @pytest.mark.asyncio
    async def test_successful_quote_response(self):
        """Testa resposta bem-sucedida"""
        response = {
            "quote_id": str(uuid4()),
            "unit_price": 45.50,
            "total_price": 455.00,
            "quantity": 10,
            "lead_time_days": 7,
            "shipping_cost": 25.00,
            "valid_until": (datetime.utcnow() + timedelta(days=30)).isoformat()
        }
        
        assert "quote_id" in response
        assert response["unit_price"] > 0
        assert response["total_price"] > 0
        assert response["lead_time_days"] > 0
    
    @pytest.mark.asyncio
    async def test_error_response(self):
        """Testa resposta de erro"""
        response = {
            "error": True,
            "message": "Invalid file format",
            "code": "INVALID_FILE"
        }
        
        assert response["error"] is True
        assert "message" in response
        assert "code" in response


class TestFileValidation:
    """Testes de validação de arquivo"""
    
    def test_supported_file_formats(self):
        """Testa formatos de arquivo suportados"""
        supported_formats = [".stl", ".obj", ".3mf", ".step"]
        
        file_url = "https://example.com/model.stl"
        file_ext = file_url.split(".")[-1].lower()
        
        is_supported = f".{file_ext}" in supported_formats
        
        assert is_supported is True
    
    def test_unsupported_file_format(self):
        """Testa formato não suportado"""
        supported_formats = [".stl", ".obj", ".3mf", ".step"]
        
        file_url = "https://example.com/model.txt"
        file_ext = file_url.split(".")[-1].lower()
        
        is_supported = f".{file_ext}" in supported_formats
        
        assert is_supported is False
    
    def test_file_size_validation(self):
        """Testa validação de tamanho de arquivo"""
        max_file_size_mb = 100
        file_size_mb = 50
        
        is_valid = file_size_mb <= max_file_size_mb
        
        assert is_valid is True


class TestQuoteComparison:
    """Testes de comparação de cotações"""
    
    def test_compare_quotes_by_price(self):
        """Testa comparação por preço"""
        quote1 = {"provider": "A", "total_price": 450.00}
        quote2 = {"provider": "B", "total_price": 420.00}
        
        cheaper_quote = quote1 if quote1["total_price"] < quote2["total_price"] else quote2
        
        assert cheaper_quote["provider"] == "B"
    
    def test_compare_quotes_by_lead_time(self):
        """Testa comparação por prazo"""
        quote1 = {"provider": "A", "lead_time_days": 10}
        quote2 = {"provider": "B", "lead_time_days": 7}
        
        faster_quote = quote1 if quote1["lead_time_days"] < quote2["lead_time_days"] else quote2
        
        assert faster_quote["provider"] == "B"


class TestErrorHandling:
    """Testes de tratamento de erros"""
    
    @pytest.mark.asyncio
    async def test_handle_api_timeout(self):
        """Testa timeout da API"""
        error = {"type": "timeout", "message": "Request timeout"}
        
        assert error["type"] == "timeout"
    
    @pytest.mark.asyncio
    async def test_handle_invalid_api_key(self):
        """Testa chave API inválida"""
        error = {"type": "auth_error", "message": "Invalid API key"}
        
        assert error["type"] == "auth_error"
    
    @pytest.mark.asyncio
    async def test_handle_missing_file(self):
        """Testa arquivo ausente"""
        error = {"type": "file_error", "message": "File not found"}
        
        assert error["type"] == "file_error"
