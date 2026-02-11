#!/usr/bin/env python3
"""
Test script to verify the functionality of the backend calculators.
This script will test each calculator discipline with sample inputs.
"""

import sys
import os

# Add backend directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from calculators.services.civil import CivilCalculators
from calculators.services.electrical import ElectricalCalculators
from calculators.services.mechanical import MechanicalCalculators


def test_civil_calculators():
    """Test civil engineering calculators"""
    print("Testing Civil Calculators...")
    
    # Test concrete volume
    result = CivilCalculators.concrete_volume(10, 5, 0.2)
    if result['success']:
        print(f"OK Concrete Volume: {result['results']['volume']} m3")
    else:
        print(f"ERROR Concrete Volume: {result['error']}")
    
    # Test steel weight
    result = CivilCalculators.steel_weight(16, 12, 10)
    if result['success']:
        print(f"OK Steel Weight: {result['results']['total_weight']} kg")
    else:
        print(f"ERROR Steel Weight: {result['error']}")
    
    # Test beam load
    result = CivilCalculators.beam_load(10, 6, 600, 300, 25, 415, 'IS456')
    if result['success']:
        print(f"OK Beam Load: {result['results']['max_moment']} kN·m")
    else:
        print(f"ERROR Beam Load: {result['error']}")
    
    # Test foundation area
    result = CivilCalculators.foundation_area(1000, 150)
    if result['success']:
        print(f"OK Foundation Area: {result['results']['required_area']} m2")
    else:
        print(f"ERROR Foundation Area: {result['error']}")
    
    # Test column design
    result = CivilCalculators.column_design(1500, 3000, 25, 415, 'bothFixed', 'IS456')
    if result['success']:
        print(f"OK Column Design: {result['results']['column_size']}")
    else:
        print(f"ERROR Column Design: {result['error']}")
    
    # Test earthwork volume
    result = CivilCalculators.earthwork_volume(20, 5, 0.5, 0.8)
    if result['success']:
        print(f"OK Earthwork Volume: {result['results']['volume']} m3")
    else:
        print(f"ERROR Earthwork Volume: {result['error']}")
    
    # Test seismic load
    result = CivilCalculators.seismic_load(10000, 3, 'medium', 1.0)
    if result['success']:
        print(f"OK Seismic Load: {result['results']['base_shear']} kN")
    else:
        print(f"ERROR Seismic Load: {result['error']}")
    
    print()


def test_electrical_calculators():
    """Test electrical engineering calculators"""
    print("Testing Electrical Calculators...")
    
    # Test load calculation
    result = ElectricalCalculators.load_calculation(100, 0.8, 0.85, '3phase', 400, 0.85)
    if result['success']:
        print(f"OK Load Calculation: {result['results']['design_current']} A")
    else:
        print(f"ERROR Load Calculation: {result['error']}")
    
    # Test cable sizing
    result = ElectricalCalculators.cable_sizing(100, 50, 400, 'IEC', 'power', 'conduit', 'copper', 40, 1.0)
    if result['success']:
        print(f"OK Cable Sizing: {result['results']['cable_size']} mm2")
    else:
        print(f"ERROR Cable Sizing: {result['error']}")
    
    # Test transformer sizing
    result = ElectricalCalculators.transformer_sizing(100, 1.25, 0.98, 'IEC', 'ONAN')
    if result['success']:
        print(f"OK Transformer Sizing: {result['results']['standard_size']} kVA")
    else:
        print(f"ERROR Transformer Sizing: {result['error']}")
    
    # Test power factor correction
    result = ElectricalCalculators.power_factor_correction(100, 0.75, 0.95, 400, 'IEC')
    if result['success']:
        print(f"OK Power Factor Correction: {result['results']['required_kvar']} kVAR")
    else:
        print(f"ERROR Power Factor Correction: {result['error']}")
    
    # Test generator sizing
    result = ElectricalCalculators.generator_sizing(80, 20, 0, 25, 'diesel')
    if result['success']:
        print(f"OK Generator Sizing: {result['results']['recommended_size']} kW")
    else:
        print(f"ERROR Generator Sizing: {result['error']}")
    
    # Test short circuit
    result = ElectricalCalculators.short_circuit(400, 500, 5, 'IEC')
    if result['success']:
        print(f"OK Short Circuit: {result['results']['pscc_ka']} kA")
    else:
        print(f"ERROR Short Circuit: {result['error']}")
    
    print()


def test_mechanical_calculators():
    """Test mechanical engineering calculators"""
    print("Testing Mechanical Calculators...")
    
    # Test HVAC load
    result = MechanicalCalculators.hvac_load(50, 3, 10, 'moderate')
    if result['success']:
        print(f"OK HVAC Load: {result['results']['total_cooling_load']} kW")
    else:
        print(f"ERROR HVAC Load: {result['error']}")
    
    # Test pump sizing
    result = MechanicalCalculators.pump_sizing(10, 20, 75, 1450)
    if result['success']:
        print(f"OK Pump Sizing: {result['results']['motor_power']} kW")
    else:
        print(f"ERROR Pump Sizing: {result['error']}")
    
    # Test pipe sizing
    result = MechanicalCalculators.pipe_sizing(100, 2, 'schedule40')
    if result['success']:
        print(f"OK Pipe Sizing: {result['results']['standard_size']} mm")
    else:
        print(f"ERROR Pipe Sizing: {result['error']}")
    
    # Test duct sizing
    result = MechanicalCalculators.duct_sizing(1000, 10)
    if result['success']:
        print(f"OK Duct Sizing: {result['results']['circular_diameter']} mm")
    else:
        print(f"ERROR Duct Sizing: {result['error']}")
    
    # Test psychrometrics
    result = MechanicalCalculators.psychrometrics(25, 60, 0)
    if result['success']:
        print(f"OK Psychrometrics: {result['results']['humidity_ratio']} g/kg")
    else:
        print(f"ERROR Psychrometrics: {result['error']}")
    
    # Test stress analysis
    result = MechanicalCalculators.stress_strain_analysis(10000, 100, 1000, 'Steel', 'tensile', 2.0)
    if result['success']:
        print(f"OK Stress Analysis: {result['results']['stress']} MPa")
    else:
        print(f"ERROR Stress Analysis: {result['error']}")
    
    print()


def main():
    """Main test function"""
    print("=== EngiSuite Analytics Backend Calculator Tests ===")
    print()
    
    try:
        test_civil_calculators()
        test_electrical_calculators()
        test_mechanical_calculators()
        
        print("=== All tests completed ===")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        print(traceback.format_exc())
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())