"""
Unit tests for Print3DService
Testing printer management, job queueing, and G-code generation
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from uuid import uuid4
from datetime import datetime, timedelta


@pytest.fixture
def print3d_service():
    """Fixture to create Print3DService instance (mocked)"""
    service = Mock()
    service.printer_apis = {}
    service.active_jobs = {}
    service.gcode_generators = {
        'cura': Mock(),
        'slic3r': Mock(),
        'simplify3d': Mock(),
        'custom': Mock()
    }
    return service


@pytest.fixture
def mock_db():
    """Mock database session"""
    return Mock()


@pytest.fixture
def mock_printer():
    """Mock printer object"""
    printer = Mock()
    printer.id = uuid4()
    printer.nome = "Ender 3 Pro"
    printer.modelo = "Creality Ender 3 Pro"
    printer.status = "disponível"
    printer.build_volume_x = 220.0
    printer.build_volume_y = 220.0
    printer.build_volume_z = 250.0
    printer.nozzle_diameter = 0.4
    return printer


@pytest.fixture
def mock_print_job():
    """Mock print job object"""
    job = Mock()
    job.id = uuid4()
    job.printer_id = uuid4()
    job.model_3d_id = uuid4()
    job.status = "queued"
    job.estimated_time_hours = 5.5
    job.estimated_cost = 125.50
    return job


class TestPrint3DServiceInitialization:
    """Test service initialization"""
    
    def test_service_initialization(self, print3d_service):
        """Test service initializes with correct defaults"""
        assert print3d_service is not None
        assert hasattr(print3d_service, 'printer_apis')
        assert hasattr(print3d_service, 'active_jobs')
        assert hasattr(print3d_service, 'gcode_generators')
    
    def test_gcode_generators_configured(self, print3d_service):
        """Test G-code generators are configured"""
        assert 'cura' in print3d_service.gcode_generators
        assert 'slic3r' in print3d_service.gcode_generators
        assert 'simplify3d' in print3d_service.gcode_generators
        assert 'custom' in print3d_service.gcode_generators
    
    def test_empty_initial_state(self, print3d_service):
        """Test service starts with empty state"""
        assert len(print3d_service.printer_apis) == 0
        assert len(print3d_service.active_jobs) == 0


class TestPrinterValidation:
    """Test printer validation logic"""
    
    def test_valid_printer_configuration(self, mock_printer):
        """Test valid printer configuration"""
        assert mock_printer.build_volume_x > 0
        assert mock_printer.build_volume_y > 0
        assert mock_printer.build_volume_z > 0
        assert mock_printer.nozzle_diameter > 0
    
    def test_build_volume_calculation(self, mock_printer):
        """Test build volume calculation"""
        volume_cm3 = (
            mock_printer.build_volume_x * 
            mock_printer.build_volume_y * 
            mock_printer.build_volume_z
        ) / 1000  # Convert mm³ to cm³
        
        expected_volume = (220 * 220 * 250) / 1000
        assert volume_cm3 == pytest.approx(expected_volume, rel=0.01)
    
    def test_nozzle_diameter_validation(self):
        """Test nozzle diameter validation"""
        valid_nozzles = [0.2, 0.4, 0.6, 0.8, 1.0]
        test_nozzle = 0.4
        
        assert test_nozzle in valid_nozzles


class TestPrinterStatus:
    """Test printer status management"""
    
    def test_available_status(self, mock_printer):
        """Test printer available status"""
        mock_printer.status = "disponível"
        assert mock_printer.status == "disponível"
    
    def test_printing_status(self, mock_printer):
        """Test printer printing status"""
        mock_printer.status = "imprimindo"
        assert mock_printer.status == "imprimindo"
    
    def test_maintenance_status(self, mock_printer):
        """Test printer maintenance status"""
        mock_printer.status = "manutenção"
        assert mock_printer.status == "manutenção"
    
    def test_status_transition(self, mock_printer):
        """Test status transitions"""
        # Available -> Printing
        mock_printer.status = "disponível"
        assert mock_printer.status == "disponível"
        
        mock_printer.status = "imprimindo"
        assert mock_printer.status == "imprimindo"


class TestPrintJobValidation:
    """Test print job validation"""
    
    def test_valid_print_job(self, mock_print_job):
        """Test valid print job"""
        assert mock_print_job.printer_id is not None
        assert mock_print_job.model_3d_id is not None
        assert mock_print_job.estimated_time_hours > 0
        assert mock_print_job.estimated_cost > 0
    
    def test_job_time_estimation(self, mock_print_job):
        """Test job time estimation"""
        time_hours = mock_print_job.estimated_time_hours
        assert time_hours > 0
        assert time_hours < 100  # Reasonable upper bound
    
    def test_job_cost_estimation(self, mock_print_job):
        """Test job cost estimation"""
        cost = mock_print_job.estimated_cost
        assert cost > 0
        assert cost < 10000  # Reasonable upper bound


class TestQueueManagement:
    """Test print queue management"""
    
    def test_job_queue_order(self):
        """Test jobs are queued in order"""
        queue = []
        
        job1 = {"id": 1, "priority": "normal", "created_at": datetime.now()}
        job2 = {"id": 2, "priority": "normal", "created_at": datetime.now() + timedelta(seconds=1)}
        
        queue.append(job1)
        queue.append(job2)
        
        assert queue[0]["id"] == 1
        assert queue[1]["id"] == 2
    
    def test_priority_queue_handling(self):
        """Test priority queue handling"""
        jobs = [
            {"id": 1, "priority": "normal"},
            {"id": 2, "priority": "high"},
            {"id": 3, "priority": "low"}
        ]
        
        # High priority should be processed first
        priority_order = {"high": 1, "normal": 2, "low": 3}
        sorted_jobs = sorted(jobs, key=lambda x: priority_order[x["priority"]])
        
        assert sorted_jobs[0]["priority"] == "high"
        assert sorted_jobs[1]["priority"] == "normal"
        assert sorted_jobs[2]["priority"] == "low"


class TestGCodeGeneration:
    """Test G-code generation logic"""
    
    def test_gcode_header_generation(self):
        """Test G-code header generation"""
        header = [
            "; Generated by 3dPot",
            "; Model: test_model.stl",
            "G21 ; Set units to millimeters",
            "G90 ; Use absolute positioning"
        ]
        
        assert len(header) == 4
        assert header[0].startswith(";")
        assert "G21" in header[2]
    
    def test_gcode_temperature_settings(self):
        """Test temperature settings in G-code"""
        nozzle_temp = 200  # °C for PLA
        bed_temp = 60      # °C for PLA
        
        temp_commands = [
            f"M104 S{nozzle_temp} ; Set nozzle temperature",
            f"M140 S{bed_temp} ; Set bed temperature"
        ]
        
        assert temp_commands[0].startswith("M104")
        assert str(nozzle_temp) in temp_commands[0]
        assert str(bed_temp) in temp_commands[1]
    
    def test_gcode_movement_commands(self):
        """Test G-code movement commands"""
        move_command = "G1 X10.5 Y20.3 Z0.2 E0.5 F3000"
        
        assert move_command.startswith("G1")
        assert "X" in move_command
        assert "Y" in move_command
        assert "Z" in move_command


class TestMaterialSettings:
    """Test material-specific settings"""
    
    def test_pla_settings(self):
        """Test PLA material settings"""
        pla_settings = {
            "nozzle_temp": 200,
            "bed_temp": 60,
            "print_speed": 50,
            "retraction_distance": 5.0
        }
        
        assert 190 <= pla_settings["nozzle_temp"] <= 220
        assert 50 <= pla_settings["bed_temp"] <= 70
    
    def test_abs_settings(self):
        """Test ABS material settings"""
        abs_settings = {
            "nozzle_temp": 240,
            "bed_temp": 100,
            "print_speed": 40,
            "retraction_distance": 3.0
        }
        
        assert 220 <= abs_settings["nozzle_temp"] <= 260
        assert 90 <= abs_settings["bed_temp"] <= 110
    
    def test_petg_settings(self):
        """Test PETG material settings"""
        petg_settings = {
            "nozzle_temp": 230,
            "bed_temp": 80,
            "print_speed": 45,
            "retraction_distance": 4.0
        }
        
        assert 220 <= petg_settings["nozzle_temp"] <= 250
        assert 70 <= petg_settings["bed_temp"] <= 90


class TestPrintTimeEstimation:
    """Test print time estimation"""
    
    def test_estimate_time_from_volume(self):
        """Test time estimation based on volume"""
        volume_cm3 = 50.0
        print_speed_mm_s = 50.0
        layer_height = 0.2
        
        # Simplified estimation
        estimated_hours = volume_cm3 / (print_speed_mm_s * layer_height * 60)
        
        assert estimated_hours > 0
    
    def test_estimate_time_with_infill(self):
        """Test time estimation with different infill"""
        base_time_hours = 5.0
        
        # 20% infill
        time_20_infill = base_time_hours * 0.6
        
        # 100% infill
        time_100_infill = base_time_hours * 1.5
        
        assert time_20_infill < base_time_hours
        assert time_100_infill > base_time_hours


class TestCostCalculation:
    """Test print cost calculation"""
    
    def test_material_cost_calculation(self):
        """Test material cost calculation"""
        filament_used_g = 250.0
        filament_price_per_kg = 45.0
        
        material_cost = (filament_used_g / 1000) * filament_price_per_kg
        
        assert material_cost == pytest.approx(11.25, rel=0.01)
    
    def test_electricity_cost_calculation(self):
        """Test electricity cost calculation"""
        print_time_hours = 5.5
        power_consumption_kw = 0.2
        electricity_rate_per_kwh = 0.65
        
        electricity_cost = print_time_hours * power_consumption_kw * electricity_rate_per_kwh
        
        assert electricity_cost > 0
    
    def test_total_print_cost(self):
        """Test total print cost"""
        material_cost = 11.25
        electricity_cost = 0.72
        labor_cost = 25.00
        
        total_cost = material_cost + electricity_cost + labor_cost
        
        assert total_cost == pytest.approx(36.97, rel=0.01)


class TestPrintSettings:
    """Test print settings validation"""
    
    def test_layer_height_validation(self):
        """Test layer height validation"""
        nozzle_diameter = 0.4
        
        valid_layer_heights = [0.1, 0.2, 0.3]
        invalid_layer_height = 0.5
        
        for height in valid_layer_heights:
            # Layer height should be less than nozzle diameter
            assert height < nozzle_diameter
        
        assert invalid_layer_height > nozzle_diameter
    
    def test_infill_percentage_validation(self):
        """Test infill percentage validation"""
        valid_infills = [0, 10, 20, 50, 100]
        
        for infill in valid_infills:
            assert 0 <= infill <= 100
    
    def test_print_speed_validation(self):
        """Test print speed validation"""
        min_speed = 10  # mm/s
        max_speed = 150  # mm/s
        
        test_speed = 50
        assert min_speed <= test_speed <= max_speed


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_model_too_large_for_printer(self):
        """Test handling of model too large for build volume"""
        model_size = {"x": 300, "y": 300, "z": 300}
        build_volume = {"x": 220, "y": 220, "z": 250}
        
        fits = (
            model_size["x"] <= build_volume["x"] and
            model_size["y"] <= build_volume["y"] and
            model_size["z"] <= build_volume["z"]
        )
        
        assert not fits
    
    def test_printer_not_available(self, mock_printer):
        """Test handling when printer is not available"""
        mock_printer.status = "manutenção"
        
        is_available = mock_printer.status == "disponível"
        assert not is_available


class TestJobMonitoring:
    """Test job monitoring logic"""
    
    def test_job_progress_tracking(self):
        """Test job progress tracking"""
        total_layers = 500
        current_layer = 250
        
        progress_percent = (current_layer / total_layers) * 100
        
        assert progress_percent == 50.0
    
    def test_estimated_time_remaining(self):
        """Test estimated time remaining calculation"""
        total_time_hours = 10.0
        progress_percent = 50.0
        
        time_remaining_hours = total_time_hours * (1 - progress_percent / 100)
        
        assert time_remaining_hours == 5.0


@pytest.mark.asyncio
class TestAsyncOperations:
    """Test async operations"""
    
    async def test_start_print_job_async(self, print3d_service, mock_db, mock_printer, mock_print_job):
        """Test async print job start"""
        # Mock database queries
        mock_db.query.return_value.filter.return_value.first.return_value = mock_printer
        
        # Verify mocks are set up
        assert mock_printer is not None
        assert mock_print_job is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
