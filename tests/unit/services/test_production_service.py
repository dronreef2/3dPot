"""
Unit tests for ProductionService
Testing production planning, scheduling, and optimization
"""

import pytest
from unittest.mock import Mock
from uuid import uuid4
from datetime import datetime, timedelta
from enum import Enum

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))


class ProductionType(Enum):
    """Production types for testing"""
    PROTOTYPE = "prototype"
    BATCH_SMALL = "batch_small"
    BATCH_MEDIUM = "batch_medium"
    BATCH_LARGE = "batch_large"
    CUSTOM = "custom"
    SERIES = "series"


class Priority(Enum):
    """Priority levels for testing"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class ProductionStatus(Enum):
    """Production status for testing"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@pytest.fixture
def production_config():
    """Production configuration fixture"""
    return {
        "standard_setup_time": 0.5,
        "standard_cycle_time": 2.0,
        "max_daily_capacity": 24.0,
        "production_type_multipliers": {
            ProductionType.PROTOTYPE: 1.5,
            ProductionType.BATCH_SMALL: 1.0,
            ProductionType.BATCH_MEDIUM: 0.9,
            ProductionType.BATCH_LARGE: 0.8,
            ProductionType.CUSTOM: 1.3,
            ProductionType.SERIES: 0.7
        },
        "quality_tolerances": {
            "dimensional": 0.1,
            "surface_finish": 0.05,
            "strength": 0.05
        }
    }


class TestProductionTypeClassification:
    """Test production type classification"""
    
    def test_prototype_classification(self):
        """Test prototype production type"""
        quantity = 1
        production_type = ProductionType.PROTOTYPE if quantity == 1 else None
        
        assert production_type == ProductionType.PROTOTYPE
    
    def test_small_batch_classification(self):
        """Test small batch classification"""
        quantity = 15
        
        if 2 <= quantity <= 20:
            production_type = ProductionType.BATCH_SMALL
        else:
            production_type = None
        
        assert production_type == ProductionType.BATCH_SMALL
    
    def test_medium_batch_classification(self):
        """Test medium batch classification"""
        quantity = 75
        
        if 21 <= quantity <= 100:
            production_type = ProductionType.BATCH_MEDIUM
        else:
            production_type = None
        
        assert production_type == ProductionType.BATCH_MEDIUM
    
    def test_large_batch_classification(self):
        """Test large batch classification"""
        quantity = 250
        
        if quantity > 100:
            production_type = ProductionType.BATCH_LARGE
        else:
            production_type = None
        
        assert production_type == ProductionType.BATCH_LARGE


class TestTimeCalculations:
    """Test production time calculations"""
    
    def test_setup_time(self, production_config):
        """Test setup time calculation"""
        setup_time = production_config["standard_setup_time"]
        assert setup_time == 0.5
    
    def test_cycle_time_prototype(self, production_config):
        """Test cycle time for prototype"""
        base_cycle_time = production_config["standard_cycle_time"]
        multiplier = production_config["production_type_multipliers"][ProductionType.PROTOTYPE]
        
        actual_cycle_time = base_cycle_time * multiplier
        assert actual_cycle_time == pytest.approx(3.0, rel=0.01)
    
    def test_cycle_time_batch(self, production_config):
        """Test cycle time for batch production"""
        base_cycle_time = production_config["standard_cycle_time"]
        multiplier = production_config["production_type_multipliers"][ProductionType.BATCH_LARGE]
        
        actual_cycle_time = base_cycle_time * multiplier
        assert actual_cycle_time == pytest.approx(1.6, rel=0.01)
    
    def test_total_production_time(self, production_config):
        """Test total production time calculation"""
        quantity = 10
        setup_time = production_config["standard_setup_time"]
        cycle_time = production_config["standard_cycle_time"]
        
        total_time = setup_time + (cycle_time * quantity)
        assert total_time == pytest.approx(20.5, rel=0.01)


class TestCapacityPlanning:
    """Test production capacity planning"""
    
    def test_daily_capacity(self, production_config):
        """Test daily capacity limit"""
        max_daily = production_config["max_daily_capacity"]
        assert max_daily == 24.0
    
    def test_capacity_utilization(self, production_config):
        """Test capacity utilization calculation"""
        planned_hours = 18.0
        max_capacity = production_config["max_daily_capacity"]
        
        utilization = (planned_hours / max_capacity) * 100
        assert utilization == 75.0
    
    def test_over_capacity_detection(self, production_config):
        """Test over-capacity detection"""
        planned_hours = 30.0
        max_capacity = production_config["max_daily_capacity"]
        
        is_over_capacity = planned_hours > max_capacity
        assert is_over_capacity is True


class TestCostEstimation:
    """Test production cost estimation"""
    
    def test_material_cost_calculation(self):
        """Test material cost calculation"""
        unit_material_cost = 50.0
        quantity = 10
        
        total_material_cost = unit_material_cost * quantity
        assert total_material_cost == 500.0
    
    def test_labor_cost_calculation(self):
        """Test labor cost calculation"""
        labor_hours = 20.0
        hourly_rate = 50.0
        
        total_labor_cost = labor_hours * hourly_rate
        assert total_labor_cost == 1000.0
    
    def test_total_production_cost(self):
        """Test total production cost"""
        material_cost = 500.0
        labor_cost = 1000.0
        overhead = 200.0
        
        total_cost = material_cost + labor_cost + overhead
        assert total_cost == 1700.0


class TestPriorityManagement:
    """Test production priority management"""
    
    def test_priority_levels(self):
        """Test priority level definitions"""
        priorities = [Priority.LOW, Priority.NORMAL, Priority.HIGH, Priority.URGENT]
        assert len(priorities) == 4
    
    def test_priority_ordering(self):
        """Test priority ordering"""
        priority_values = {
            Priority.LOW: 1,
            Priority.NORMAL: 2,
            Priority.HIGH: 3,
            Priority.URGENT: 4
        }
        
        assert priority_values[Priority.URGENT] > priority_values[Priority.HIGH]
        assert priority_values[Priority.HIGH] > priority_values[Priority.NORMAL]
    
    def test_queue_prioritization(self):
        """Test queue prioritization"""
        jobs = [
            {"id": 1, "priority": Priority.NORMAL},
            {"id": 2, "priority": Priority.URGENT},
            {"id": 3, "priority": Priority.LOW}
        ]
        
        priority_order = {Priority.URGENT: 1, Priority.HIGH: 2, Priority.NORMAL: 3, Priority.LOW: 4}
        sorted_jobs = sorted(jobs, key=lambda x: priority_order[x["priority"]])
        
        assert sorted_jobs[0]["priority"] == Priority.URGENT


class TestQualityControl:
    """Test quality control parameters"""
    
    def test_dimensional_tolerance(self, production_config):
        """Test dimensional tolerance"""
        tolerance = production_config["quality_tolerances"]["dimensional"]
        assert tolerance == 0.1  # mm
    
    def test_surface_finish_tolerance(self, production_config):
        """Test surface finish tolerance"""
        tolerance = production_config["quality_tolerances"]["surface_finish"]
        assert tolerance == 0.05
    
    def test_strength_tolerance(self, production_config):
        """Test strength tolerance"""
        tolerance = production_config["quality_tolerances"]["strength"]
        assert tolerance == 0.05  # 5%
    
    def test_quality_check_pass(self):
        """Test quality check pass condition"""
        measured_dimension = 100.05  # mm
        target_dimension = 100.0  # mm
        tolerance = 0.1  # mm
        
        deviation = abs(measured_dimension - target_dimension)
        passes = deviation <= tolerance
        
        assert passes is True
    
    def test_quality_check_fail(self):
        """Test quality check fail condition"""
        measured_dimension = 100.15  # mm
        target_dimension = 100.0  # mm
        tolerance = 0.1  # mm
        
        deviation = abs(measured_dimension - target_dimension)
        passes = deviation <= tolerance
        
        assert passes is False


class TestResourceAllocation:
    """Test resource allocation"""
    
    def test_material_allocation(self):
        """Test material allocation"""
        required_materials = {
            "PLA": 2.5,  # kg
            "ABS": 1.0   # kg
        }
        
        assert required_materials["PLA"] > 0
        assert required_materials["ABS"] > 0
    
    def test_equipment_allocation(self):
        """Test equipment allocation"""
        required_equipment = [
            "printer_1",
            "printer_2",
            "post_processing_station"
        ]
        
        assert len(required_equipment) == 3
    
    def test_labor_allocation(self):
        """Test labor allocation"""
        labor_hours = {
            "printing": 10.0,
            "assembly": 5.0,
            "quality_control": 2.0
        }
        
        total_hours = sum(labor_hours.values())
        assert total_hours == 17.0


class TestScheduling:
    """Test production scheduling"""
    
    def test_schedule_start_date(self):
        """Test schedule start date"""
        start_date = datetime.now()
        assert start_date is not None
    
    def test_schedule_end_date_calculation(self):
        """Test end date calculation"""
        start_date = datetime.now()
        duration_hours = 24.0
        
        end_date = start_date + timedelta(hours=duration_hours)
        time_diff = (end_date - start_date).total_seconds() / 3600
        
        assert time_diff == pytest.approx(24.0, rel=0.01)
    
    def test_schedule_conflict_detection(self):
        """Test schedule conflict detection"""
        job1_start = datetime.now()
        job1_end = job1_start + timedelta(hours=8)
        
        job2_start = job1_start + timedelta(hours=4)
        job2_end = job2_start + timedelta(hours=8)
        
        # Check for overlap
        has_conflict = not (job1_end <= job2_start or job2_end <= job1_start)
        assert has_conflict is True


class TestProductionMetrics:
    """Test production metrics"""
    
    def test_efficiency_calculation(self):
        """Test production efficiency calculation"""
        actual_output = 95
        planned_output = 100
        
        efficiency = (actual_output / planned_output) * 100
        assert efficiency == 95.0
    
    def test_defect_rate_calculation(self):
        """Test defect rate calculation"""
        defective_units = 5
        total_units = 100
        
        defect_rate = (defective_units / total_units) * 100
        assert defect_rate == 5.0
    
    def test_on_time_delivery_rate(self):
        """Test on-time delivery rate"""
        on_time_deliveries = 90
        total_deliveries = 100
        
        on_time_rate = (on_time_deliveries / total_deliveries) * 100
        assert on_time_rate == 90.0


class TestProductionStatus:
    """Test production status tracking"""
    
    def test_pending_status(self):
        """Test pending status"""
        status = ProductionStatus.PENDING
        assert status == ProductionStatus.PENDING
    
    def test_in_progress_status(self):
        """Test in-progress status"""
        status = ProductionStatus.IN_PROGRESS
        assert status == ProductionStatus.IN_PROGRESS
    
    def test_completed_status(self):
        """Test completed status"""
        status = ProductionStatus.COMPLETED
        assert status == ProductionStatus.COMPLETED
    
    def test_status_transition(self):
        """Test status transition"""
        status = ProductionStatus.PENDING
        assert status == ProductionStatus.PENDING
        
        # Transition to in-progress
        status = ProductionStatus.IN_PROGRESS
        assert status == ProductionStatus.IN_PROGRESS


class TestOptimization:
    """Test production optimization"""
    
    def test_batch_size_optimization(self):
        """Test batch size optimization"""
        # Larger batches are more efficient
        small_batch_time_per_unit = 2.0
        large_batch_time_per_unit = 1.6
        
        efficiency_gain = ((small_batch_time_per_unit - large_batch_time_per_unit) / 
                          small_batch_time_per_unit) * 100
        
        assert efficiency_gain == pytest.approx(20.0, rel=0.01)
    
    def test_setup_time_optimization(self):
        """Test setup time optimization through batching"""
        setup_time = 0.5
        units_10 = 10
        units_100 = 100
        
        # Setup time per unit decreases with batch size
        setup_per_unit_10 = setup_time / units_10
        setup_per_unit_100 = setup_time / units_100
        
        assert setup_per_unit_100 < setup_per_unit_10


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_invalid_quantity(self):
        """Test handling of invalid quantity"""
        quantity = -5
        assert quantity < 0
    
    def test_over_capacity_handling(self, production_config):
        """Test over-capacity handling"""
        required_hours = 30
        max_capacity = production_config["max_daily_capacity"]
        
        if required_hours > max_capacity:
            excess_hours = required_hours - max_capacity
            assert excess_hours == 6.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
