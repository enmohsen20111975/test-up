"""
Comprehensive workflow engineering transformation - covers ALL 800 workflows.
Creates diverse, practical workflow patterns for each domain.
"""
import sqlite3
from datetime import datetime
from pathlib import Path
import random

DB_PATH = Path(__file__).parent / "workflows.db"

# Extended engineering workflow patterns - diverse real-world scenarios
ELECTRICAL_PATTERNS = [
    ("load_analysis_service_sizing", [
        ("Load Survey", "apparent_power_3ph", "Sum connected loads by circuit and area"),
        ("Demand Factor", None, "Apply type-specific demand factor from tables"),
        ("Diversity Factor", None, "Apply simultaneity factor for diversity"),
        ("Service Selection", "transformer_kva", "Choose service/transformer size"),
        ("Voltage Coordination", "power_ac_3ph", "Verify 3-phase balance and supply"),
    ]),
    ("cable_breaker_protection", [
        ("Current Calculation", "apparent_power_3ph", "Calculate design circuit current"),
        ("Cable Ampacity", "voltage_drop_3ph", "Select cable for ampacity with derating"),
        ("Voltage Drop", "voltage_drop_3ph", "Ensure ≤3% feeder, ≤5% total"),
        ("Breaker Rating", None, "Size at 1.25x design current"),
        ("Fault Coordination", "short_circuit_mva", "Verify fault current handling"),
    ]),
    ("grounding_safety_system", [
        ("Fault Currents", "short_circuit_mva", "Calculate 3φ and SLG fault current"),
        ("Ground Electrode", "grounding_rod", "Design rods/mats for <5Ω resistance"),
        ("Bonding Paths", None, "Bond structure, equipment, utilities"),
        ("Ground Conductor", None, "Size grounding conductors for fault"),
        ("Arc Flash Risk", None, "Assess PPE categories and incident energy"),
    ]),
    ("lighting_illumination_system", [
        ("Target Lux", "illumination_lumen_method", "Determine required foot-candles/lux"),
        ("Total Lumens", "illumination_lumen_method", "Calculate lumens from fixtures"),
        ("Fixture Layout", None, "Arrange for uniform spacing (L/H ratio)"),
        ("Circuit Load", "power_ac_3ph", "Sum connected lighting load in watts"),
        ("Controls Design", None, "Specify occupancy sensors, daylighting, schedule"),
    ]),
    ("motor_starting_protection", [
        ("Motor Power", "power_ac_3ph", "Calculate motor input from output"),
        ("Starting Current", None, "Estimate start/inrush current (5-7x FLA)"),
        ("Feeder Cable", "voltage_drop_3ph", "Size for start voltage dip <7%"),
        ("Starter Device", None, "Select DOL, soft-start, or VFD"),
        ("Overload Relay", None, "Set protection per motor nameplate"),
    ]),
    ("transformer_selection_placement", [
        ("Load Demand", "apparent_power_3ph", "Calculate total demand load (kVA)"),
        ("Transformer Size", "transformer_kva", "Select standard kVA rating"),
        ("Losses", None, "Calculate copper/iron losses at 75% load"),
        ("Cooling Type", None, "Specify ONAN, ONAF, or OFAF cooling"),
        ("Protection", "short_circuit_mva", "Coordinate primary/secondary protection"),
    ]),
    ("panel_circuit_scheduling", [
        ("Phase Loading", "power_ac_3ph", "Balance loads across three phases"),
        ("Main Breaker", "apparent_power_3ph", "Size main protective device"),
        ("Branch Circuits", None, "Create detailed circuit schedule"),
        ("Busbar Sizing", None, "Design busbar for current and heat"),
        ("One-Line Diagram", None, "Create schematic and circuit directory"),
    ]),
    ("power_factor_correction", [
        ("Current PF", "power_factor", "Measure or estimate existing PF"),
        ("Reactive Power", "power_ac_3ph", "Calculate kVAR for target PF"),
        ("Capacitor Bank", None, "Size fixed or switched capacitor unit"),
        ("Controller", "electrical_inductive_reactance", "Select auto PF controller"),
        ("Detuning", "electrical_impedance_series", "Add reactor if resonance risk"),
    ]),
    ("renewable_solar_installation", [
        ("Energy Audit", None, "Analyze annual load and generation"),
        ("PV Array", None, "Calculate capacity for offset goals"),
        ("DC Wiring", "voltage_drop_dc", "Size conductors from array to inverter"),
        ("Inverter", None, "Select string, multi-string, or central"),
        ("Grid Interconnection", "voltage_drop_3ph", "Design AC feeder and protection"),
    ]),
    ("backup_generator_design", [
        ("Critical Loads", "apparent_power_3ph", "Identify and sum essential loads"),
        ("Gen Sizing", None, "1.25x critical load with inrush margin"),
        ("Fuel System", None, "Design tank for 8-24 hour run time"),
        ("ATS Logic", "voltage_drop_3ph", "Transfer switch with load sequencing"),
        ("Test Schedule", None, "Plan monthly exercising and maintenance"),
    ]),
]

MECHANICAL_PATTERNS = [
    ("hvac_load_equipment_sizing", [
        ("Sensible Load", "hvac_sensible_load", "Calculate space cooling/heating watts"),
        ("Latent Load", "hvac_latent_load", "Calculate dehumidification needs"),
        ("Total Capacity", None, "Sum sensible + latent, add safety margin"),
        ("Equipment Selection", "cop", "Choose chiller or furnace with COP"),
        ("Distribution", None, "Select central vs distributed system"),
    ]),
    ("duct_sizing_and_balance", [
        ("Air Volume", "continuity_flow", "Calculate CFM from load and ΔT"),
        ("Main Duct", "darcy_weisbach", "Diameter for 400-500 fpm velocity"),
        ("Branches", "darcy_weisbach", "Size for 200-300 fpm in branches"),
        ("Pressure Loss", "darcy_weisbach", "Total system pressure drop (Pa)"),
        ("Fan Selection", "fan_power", "Choose supply/return fans for CFM/head"),
    ]),
    ("piping_flow_and_head", [
        ("Flow Rate", "continuity_flow", "Calculate GPM for chilled/hot water"),
        ("Pipe Diameter", "darcy_weisbach", "Select for optimal velocity (3-6 ft/s)"),
        ("Friction Drop", "darcy_weisbach", "Calculate pipe friction loss (Pa/m)"),
        ("Valve Losses", None, "Account for regulators, check, isolating"),
        ("Pump Power", "pump_power", "Calculate kW for total head and flow"),
    ]),
    ("thermal_insulation_economics", [
        ("Heat Transfer", "heat_transfer_conduction", "Calculate loss through bare surface"),
        ("Insulation Option", "heat_transfer_conduction", "Model with various thicknesses"),
        ("Annual Savings", None, "Calculate kWh and cost reduction"),
        ("Payback Period", None, "Determine ROI vs installed cost"),
        ("Vapor Control", None, "Specify barrier for wet/dry conditions"),
    ]),
    ("heat_exchanger_sizing", [
        ("Duty", "mechanical_heat_exchanger", "Calculate kW to transfer"),
        ("Temperatures", "mechanical_heat_exchanger", "Define inlet/outlet conditions"),
        ("LMTD", "mechanical_heat_exchanger", "Log-mean temperature difference"),
        ("Selection", None, "Choose plate-frame, shell-tube, or brazed"),
        ("Fouling Control", "continuity_flow", "Verify water velocity for cleanliness"),
    ]),
    ("pump_system_engineering", [
        ("System Flow", "continuity_flow", "Determine GPM requirement"),
        ("Total Head", "pump_power", "Sum static + friction head loss"),
        ("Pump Curve", "pump_power", "Select operating point on curve"),
        ("Motor Power", "pump_power", "Estimate required motor size (kW)"),
        ("Flow Control", None, "Specify VFD or pressure reducing valve"),
    ]),
    ("compressor_and_storage", [
        ("Air Demand", "continuity_flow", "Survey SCFM at working pressure"),
        ("Peak Demand", None, "Determine simultaneous vs peak usage"),
        ("Storage Tank", "ideal_gas", "Size receiver for peak flow"),
        ("Compressor Type", "compressor_power", "Select rotary, screw, or piston"),
        ("Power Cost", "compressor_power", "Calculate annual electricity expense"),
    ]),
    ("cooling_tower_evaluation", [
        ("Heat Rejection", "cop", "Calculate condenser heat from chiller"),
        ("Approach", None, "Water temp above outdoor wet-bulb"),
        ("Water Flow", "continuity_flow", "Calculate circulation GPM"),
        ("Tower Type", None, "Select crossflow vs counterflow design"),
        ("Fan Power", "fan_power", "Calculate cooling Tower fan motor kW"),
    ]),
    ("boiler_and_steam_system", [
        ("Space Heat", "heat_transfer_conduction", "Building envelope heat loss"),
        ("Domestic Hot Water", None, "Add DHW demand for recovery"),
        ("Boiler Capacity", None, "Size at 1.2x peak load (BTU/hr)"),
        ("Fuel Type", None, "Natural gas, oil, or electric"),
        ("Efficiency", None, "Select AFUE rating (85-95%)"),
    ]),
    ("vibration_and_noise_control", [
        ("Operating Frequency", "reynolds_number", "Identify equipment RPM/Hz"),
        ("Isolation Target", None, "Set natural freq at 1/3 operating"),
        ("Mount Selection", None, "Elastomeric vs spring mounts"),
        ("Deflection", None, "Verify mount static/dynamic deflection"),
        ("Installation", None, "Confirm proper leveling and alignment"),
    ]),
]

CIVIL_PATTERNS = [
    ("structural_analysis_loads", [
        ("Dead Load", "beam_bending_stress", "Calculate structural self-weight"),
        ("Live Load", "beam_bending_stress", "Apply per occupancy code (kN/m²)"),
        ("Wind Load", "beam_bending_stress", "Environmental pressure from design"),
        ("Load Cases", None, "Create LRFD/ASD combinations"),
        ("Critical Members", None, "Identify maximum moment/shear members"),
    ]),
    ("beam_and_bending_design", [
        ("Span", "beam_bending_stress", "Establish geometry and loading"),
        ("Moment", "beam_bending_stress", "Calculate maximum bending moment"),
        ("Shear", "beam_bending_stress", "Calculate maximum shear force"),
        ("Section", "beam_bending_stress", "Select member for allowable stress"),
        ("Deflection", "beam_deflection_ss_udl", "Check L/240 or L/360 limit"),
    ]),
    ("column_axial_buckling", [
        ("Axial Load", "axial_stress", "Sum all loads from above"),
        ("Unsupported Length", "column_buckling", "Establish KL for buckling"),
        ("Slenderness", "column_buckling", "Calculate KL/r ratio"),
        ("Allowable Stress", "column_buckling", "Verify stress ≤ allowable"),
        ("Reinforcement", None, "Design rebar for axial and moment"),
    ]),
    ("foundation_bearing_settlement", [
        ("Loads", "axial_stress", "Obtain from structure analysis"),
        ("Soil Strength", "bearing_pressure", "Test or estimate bearing capacity"),
        ("Footing Area", "bearing_pressure", "Size for service load"),
        ("Settlement", "settlement_elastic", "Calculate elastic + consolidation"),
        ("Rebar Design", None, "Reinforcement for moment and shear"),
    ]),
    ("concrete_proportioning_mix", [
        ("Strength (f'c)", None, "From structural design requirement"),
        ("Water-Cement", None, "Calculate w/c from strength relation"),
        ("Slump", None, "Choose per placement method"),
        ("Air Content", None, "Entrained air for durability"),
        ("Proportions", None, "Cement:Sand:Coarse:Water ratio"),
    ]),
    ("retaining_wall_stability", [
        ("Height", "retaining_wall_active_pressure", "Wall geometry"),
        ("Earth Pressure", "retaining_wall_active_pressure", "Active and passive diagrams"),
        ("Overturning", None, "Moment resistance check"),
        ("Sliding", None, "Friction resistance check"),
        ("Base Bearing", "bearing_pressure", "Pressure within allowable"),
    ]),
    ("slope_and_embankment_stability", [
        ("Geometry", None, "Height, angle, profile"),
        ("Soil Data", None, "Friction angle, cohesion, unit weight"),
        ("Critical Circle", None, "Find minimum FS failure surface"),
        ("Factor of Safety", None, "Bishop or Fellenius method"),
        ("Remediation", None, "Berms, drains, walls if FS < limit"),
    ]),
    ("asphalt_pavement_design", [
        ("Traffic", None, "ESALs over design life"),
        ("Subgrade", None, "CBR testing or estimation"),
        ("Structural Number", None, "AASHTO SN requirement"),
        ("Layers", None, "Asphalt, base, subbase thickness (mm)"),
        ("Drainage", None, "Permeable base, edge drains, slope"),
    ]),
    ("stormwater_runoff_design", [
        ("Rainfall", None, "Design storm (10-year, 100-year)"),
        ("Runoff Coeff", None, "By surface type and slope"),
        ("Peak Flow", "manning_flow", "Rational Method or SCS calculation"),
        ("Pipe Sizing", "manning_flow", "Manning equation for capacity"),
        ("Detention", None, "Pond volume for max runoff storage"),
    ]),
    ("excavation_and_fill", [
        ("Existing Grade", None, "Survey baseline elevation"),
        ("Design Grade", None, "Required pad elevation"),
        ("Cut/Fill Volume", None, "Average end area method"),
        ("Balance", None, "Borrow vs haul-away determination"),
        ("Compaction", None, "Method and specification (%)"),
    ]),
]

def assign_workflows_to_patterns():
    """Assign all 800 workflows to engineering patterns."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("=" * 70)
    print("COMPREHENSIVE WORKFLOW ENGINEERING TRANSFORMATION")
    print("=" * 70)
    
    try:
        # Get all workflows grouped by domain
        for domain, patterns in [("electrical", ELECTRICAL_PATTERNS), 
                                  ("mechanical", MECHANICAL_PATTERNS),
                                  ("civil", CIVIL_PATTERNS)]:
            
            print(f"\n🏗️  {domain.upper()} - Assigning {len(patterns)} engineering patterns...")
            
            # Get all workflows for this domain
            cur.execute("SELECT id FROM workflows WHERE domain = ? ORDER BY id", (domain,))
            workflow_ids = [row[0] for row in cur.fetchall()]
            
            # Assign workflows to patterns in round-robin fashion
            for idx, wf_id in enumerate(workflow_ids):
                pattern_idx = idx % len(patterns)
                pattern_name, steps = patterns[pattern_idx]
                
                # Clear existing steps
                cur.execute("DELETE FROM workflow_steps WHERE workflow_id = ?", (wf_id,))
                
                # Insert new steps
                for step_num, (step_name, calc_name, description) in enumerate(steps, 1):
                    calculation_id = None
                    equation = None
                    
                    # Find calculation in database
                    if calc_name:
                        cur.execute("""
                            SELECT id, equation FROM equations
                            WHERE name LIKE ? AND domain = ?
                            LIMIT 1
                        """, (f"%{calc_name}%", domain))
                        result = cur.fetchone()
                        if result:
                            calculation_id, equation = result
                    
                    # Insert step
                    cur.execute("""
                        INSERT INTO workflow_steps
                        (workflow_id, step_number, name, description, calculation_id, equation)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (wf_id, step_num, step_name, description, calculation_id, equation))
                
                conn.commit()
                
                if (idx + 1) % 50 == 0:
                    print(f"  ✅ {idx + 1} workflows processed...")
            
            print(f"  ✅ All {len(workflow_ids)} {domain} workflows assigned!")
        
        print("\n" + "=" * 70)
        print("✨ TRANSFORMATION COMPLETE!")
        print("=" * 70)
        
        # Show statistics
        cur.execute("""
            SELECT domain, COUNT(*) as workflows, AVG(step_count) as avg_steps
            FROM (
              SELECT domain, COUNT(*) as step_count
              FROM workflows w
              LEFT JOIN workflow_steps ws ON w.id = ws.workflow_id
              GROUP BY w.id
            )
            GROUP BY domain
        """)
        
        print("\n📊 Results:")
        for domain, wf_count, avg_steps in cur.fetchall():
            print(f"  {domain}: {wf_count} workflows × {avg_steps:.1f} steps avg")
        
    finally:
        conn.close()

if __name__ == "__main__":
    assign_workflows_to_patterns()
