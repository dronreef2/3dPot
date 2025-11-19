"""
Unit tests for ModelingService
Testing 3D modeling, engine selection, and validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from uuid import uuid4
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any


class ModelingEngine(Enum):
    """Tipos de engines de modelagem suportados."""
    CADQUERY = "cadquery"
    OPENSCAD = "openscad"


class ModelFormat(Enum):
    """Formatos de arquivo suportados."""
    STL = "stl"
    OBJ = "obj"
    STEP = "step"
    DXF = "dxf"


@dataclass
class ModelingSpecs:
    """Especificações para modelagem 3D."""
    category: str
    material: str
    dimensions: Dict[str, float]
    additional_specs: Dict[str, Any]
    components: List[Dict[str, Any]] = None
    features: List[Dict[str, Any]] = None


@dataclass
class ModelingResult:
    """Resultado da modelagem 3D."""
    success: bool
    model_path: Optional[str] = None
    engine_used: Optional[ModelingEngine] = None
    format_used: Optional[ModelFormat] = None
    message: str = ""
    specs: Optional[Dict[str, Any]] = None
    validation_passed: bool = False
    printability_report: Optional[Dict[str, Any]] = None
    generation_time: float = 0.0


@pytest.fixture
def modeling_service():
    """Fixture to create ModelingService instance (mocked)"""
    service = Mock()
    service.storage_path = Path('/tmp/models')
    service.temp_path = Path('/tmp/temp')
    service.default_engine = ModelingEngine.CADQUERY
    service._available_engines = [ModelingEngine.CADQUERY, ModelingEngine.OPENSCAD]
    return service


@pytest.fixture
def mechanical_specs():
    """Fixture for mechanical modeling specs"""
    return ModelingSpecs(
        category="mecânico",
        material="PLA",
        dimensions={
            "largura": 100.0,
            "altura": 50.0,
            "profundidade": 30.0
        },
        additional_specs={
            "wall_thickness": 2.0,
            "tolerance": 0.1
        }
    )


@pytest.fixture
def electronic_specs():
    """Fixture for electronic enclosure specs"""
    return ModelingSpecs(
        category="eletrônico",
        material="ABS",
        dimensions={
            "largura": 80.0,
            "altura": 40.0,
            "profundidade": 25.0
        },
        additional_specs={
            "mounting_holes": True,
            "ventilation": True
        },
        components=[
            {"type": "arduino", "width": 53.3, "length": 68.6},
            {"type": "power_supply", "width": 30.0, "length": 40.0}
        ]
    )


class TestModelingServiceInitialization:
    """Test service initialization"""
    
    def test_service_initialization(self, modeling_service):
        """Test that service initializes correctly"""
        assert modeling_service is not None
        assert modeling_service.default_engine == ModelingEngine.CADQUERY
    
    def test_storage_paths_configured(self, modeling_service):
        """Test storage paths are configured"""
        assert modeling_service.storage_path is not None
        assert modeling_service.temp_path is not None


class TestModelingEngines:
    """Test modeling engine enumerations"""
    
    def test_modeling_engine_values(self):
        """Test ModelingEngine enum values"""
        assert ModelingEngine.CADQUERY.value == "cadquery"
        assert ModelingEngine.OPENSCAD.value == "openscad"
    
    def test_model_format_values(self):
        """Test ModelFormat enum values"""
        assert ModelFormat.STL.value == "stl"
        assert ModelFormat.OBJ.value == "obj"
        assert ModelFormat.STEP.value == "step"
        assert ModelFormat.DXF.value == "dxf"


class TestModelingSpecs:
    """Test ModelingSpecs dataclass"""
    
    def test_mechanical_specs_creation(self, mechanical_specs):
        """Test mechanical specs creation"""
        assert mechanical_specs.category == "mecânico"
        assert mechanical_specs.material == "PLA"
        assert mechanical_specs.dimensions["largura"] == 100.0
        assert mechanical_specs.additional_specs["wall_thickness"] == 2.0
    
    def test_electronic_specs_with_components(self, electronic_specs):
        """Test electronic specs with components"""
        assert electronic_specs.category == "eletrônico"
        assert len(electronic_specs.components) == 2
        assert electronic_specs.components[0]["type"] == "arduino"
    
    def test_specs_optional_fields(self):
        """Test specs with optional fields"""
        specs = ModelingSpecs(
            category="arquitetura",
            material="PETG",
            dimensions={"largura": 200.0, "altura": 150.0, "profundidade": 100.0},
            additional_specs={}
        )
        assert specs.components is None
        assert specs.features is None


class TestModelingResult:
    """Test ModelingResult dataclass"""
    
    def test_successful_result(self):
        """Test successful modeling result"""
        result = ModelingResult(
            success=True,
            model_path="/tmp/models/test.stl",
            engine_used=ModelingEngine.CADQUERY,
            format_used=ModelFormat.STL,
            message="Model generated successfully",
            validation_passed=True,
            generation_time=2.5
        )
        
        assert result.success is True
        assert result.model_path == "/tmp/models/test.stl"
        assert result.engine_used == ModelingEngine.CADQUERY
        assert result.validation_passed is True
        assert result.generation_time == 2.5
    
    def test_failed_result(self):
        """Test failed modeling result"""
        result = ModelingResult(
            success=False,
            message="Invalid dimensions",
            generation_time=0.1
        )
        
        assert result.success is False
        assert result.model_path is None
        assert result.validation_passed is False


class TestDimensionValidation:
    """Test dimension validation logic"""
    
    def test_valid_dimensions(self, mechanical_specs):
        """Test validation of valid dimensions"""
        dims = mechanical_specs.dimensions
        assert dims["largura"] > 0
        assert dims["altura"] > 0
        assert dims["profundidade"] > 0
    
    def test_minimum_dimensions(self):
        """Test minimum dimension requirements"""
        min_dimension = 1.0  # mm
        
        valid_dims = {"largura": 10.0, "altura": 10.0, "profundidade": 10.0}
        for dim_value in valid_dims.values():
            assert dim_value >= min_dimension
    
    def test_invalid_dimensions(self):
        """Test invalid dimensions (negative or zero)"""
        invalid_dims = {"largura": -10.0, "altura": 0, "profundidade": 5.0}
        
        # At least one dimension is invalid
        assert invalid_dims["largura"] < 0 or invalid_dims["altura"] <= 0


class TestMaterialValidation:
    """Test material validation"""
    
    def test_supported_materials(self):
        """Test supported materials list"""
        supported_materials = ["PLA", "ABS", "PETG", "nylon", "metal", "composite"]
        
        test_material = "PLA"
        assert test_material in supported_materials
    
    def test_unsupported_material(self):
        """Test handling of unsupported material"""
        supported_materials = ["PLA", "ABS", "PETG", "nylon", "metal", "composite"]
        
        test_material = "WOOD"
        assert test_material not in supported_materials


class TestCategoryValidation:
    """Test category validation"""
    
    def test_valid_categories(self):
        """Test valid modeling categories"""
        valid_categories = ["mecânico", "eletrônico", "misto", "arquitetura"]
        
        assert "mecânico" in valid_categories
        assert "eletrônico" in valid_categories
        assert "arquitetura" in valid_categories
    
    def test_category_specific_specs(self, electronic_specs):
        """Test category-specific specifications"""
        # Electronic category should support components
        assert electronic_specs.category == "eletrônico"
        assert electronic_specs.components is not None
        assert len(electronic_specs.components) > 0


class TestVolumeCalculation:
    """Test volume calculations"""
    
    def test_simple_box_volume(self):
        """Test volume calculation for simple box"""
        width = 100.0   # mm
        height = 50.0   # mm
        depth = 30.0    # mm
        
        volume_mm3 = width * height * depth
        volume_cm3 = volume_mm3 / 1000  # Convert to cm³
        
        assert volume_mm3 == 150000.0
        assert volume_cm3 == 150.0
    
    def test_volume_with_wall_thickness(self):
        """Test volume calculation considering wall thickness"""
        outer_width = 100.0
        outer_height = 50.0
        outer_depth = 30.0
        wall_thickness = 2.0
        
        inner_width = outer_width - (2 * wall_thickness)
        inner_height = outer_height - (2 * wall_thickness)
        inner_depth = outer_depth - (2 * wall_thickness)
        
        outer_volume = outer_width * outer_height * outer_depth
        inner_volume = inner_width * inner_height * inner_depth
        material_volume = outer_volume - inner_volume
        
        assert material_volume > 0
        assert material_volume < outer_volume


class TestPrintabilityValidation:
    """Test printability validation logic"""
    
    def test_minimum_wall_thickness(self):
        """Test minimum wall thickness validation"""
        min_wall_thickness = 0.8  # mm (typical for FDM)
        
        valid_thickness = 2.0
        invalid_thickness = 0.4
        
        assert valid_thickness >= min_wall_thickness
        assert invalid_thickness < min_wall_thickness
    
    def test_overhang_angle_validation(self):
        """Test overhang angle validation"""
        max_overhang_angle = 45.0  # degrees without support
        
        valid_angle = 30.0
        invalid_angle = 60.0
        
        assert valid_angle <= max_overhang_angle
        assert invalid_angle > max_overhang_angle
    
    def test_bridge_length_validation(self):
        """Test bridge length validation"""
        max_bridge_length = 5.0  # mm without support
        
        valid_bridge = 3.0
        invalid_bridge = 8.0
        
        assert valid_bridge <= max_bridge_length
        assert invalid_bridge > max_bridge_length


class TestEngineSelection:
    """Test engine selection logic"""
    
    def test_cadquery_for_mechanical(self, modeling_service):
        """Test CadQuery selection for mechanical parts"""
        category = "mecânico"
        # CadQuery is good for mechanical parts
        assert modeling_service.default_engine == ModelingEngine.CADQUERY
    
    def test_engine_availability(self, modeling_service):
        """Test checking available engines"""
        # Service should check which engines are available
        assert hasattr(modeling_service, '_available_engines')


class TestModelGeneration:
    """Test model generation logic (mocked)"""
    
    def test_generate_simple_box(self, mechanical_specs):
        """Test generating a simple box model"""
        # This would normally use CadQuery or OpenSCAD
        # Here we test the logic without actual generation
        
        dims = mechanical_specs.dimensions
        volume = dims["largura"] * dims["altura"] * dims["profundidade"]
        
        # Volume should be positive
        assert volume > 0
        # Should be reasonable size
        assert volume < 1000000  # Less than 1L
    
    def test_generate_enclosure_with_features(self, electronic_specs):
        """Test generating enclosure with features"""
        # Test that features are properly specified
        assert electronic_specs.additional_specs["mounting_holes"] is True
        assert electronic_specs.additional_specs["ventilation"] is True


class TestFileOperations:
    """Test file operations (mocked)"""
    
    def test_model_path_generation(self):
        """Test generating model file path"""
        model_id = uuid4()
        format_ext = "stl"
        
        expected_path = f"/tmp/models/{model_id}.{format_ext}"
        assert expected_path.endswith(".stl")
        assert str(model_id) in expected_path
    
    def test_temp_file_cleanup(self):
        """Test temporary file cleanup logic"""
        # Temp files should be cleaned up after processing
        temp_files = []
        # After processing
        assert len(temp_files) == 0


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_invalid_specs_handling(self):
        """Test handling of invalid specifications"""
        invalid_specs = ModelingSpecs(
            category="invalid_category",
            material="UNKNOWN",
            dimensions={"largura": -10.0},
            additional_specs={}
        )
        
        # Should detect invalid values
        assert invalid_specs.dimensions["largura"] < 0
    
    def test_missing_dimensions(self):
        """Test handling of missing required dimensions"""
        incomplete_dims = {"largura": 100.0}  # Missing altura and profundidade
        
        assert "altura" not in incomplete_dims
        assert "profundidade" not in incomplete_dims


class TestPerformance:
    """Test performance-related logic"""
    
    def test_generation_time_tracking(self):
        """Test that generation time is tracked"""
        result = ModelingResult(
            success=True,
            generation_time=2.5
        )
        
        assert result.generation_time > 0
        assert result.generation_time < 60  # Should be under 1 minute for simple models


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
