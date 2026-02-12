"""
Create a dynamic workflow configuration table that can be edited in database.
Allows users to define workflow patterns without code changes.
"""
import sqlite3
from pathlib import Path
import json

DB_PATH = Path(__file__).parent / "workflows.db"

# Default workflow patterns - can be edited in database later
DEFAULT_WORKFLOW_PATTERNS = {
    "electrical": {
        "load_analysis": {
            "description": "Analyze electrical loads and select service",
            "steps": [
                ("Load Survey", "apparent_power_3ph", "Sum connected loads from circuits"),
                ("Demand Factor", None, "Apply type-specific demand factor"),
                ("Diversified Load", None, "Account for simultaneous usage"),
                ("Service Selection", "transformer_kva", "Choose transformer/service size"),
                ("Voltage Verification", "power_ac_3ph", "Check 3-phase balance"),
            ]
        },
        "cable_breaker": {
            "description": "Design cable and breaker protection",
            "steps": [
                ("Current Calculation", "apparent_power_3ph", "Calculate design current"),
                ("Cable Selection", "voltage_drop_3ph", "Choose cable for ampacity"),
                ("Voltage Drop Check", "voltage_drop_3ph", "Verify drop ≤ 3%"),
                ("Breaker Sizing", None, "Size at 1.25x design current"),
                ("Fault Coordination", "short_circuit_mva", "Verify fault current handling"),
            ]
        },
        "grounding": {
            "description": "Design grounding and safety system",
            "steps": [
                ("Fault Current", "short_circuit_mva", "Calculate fault current"),
                ("Ground Electrode", "grounding_rod", "Design for <5Ω resistance"),
                ("Bonding System", None, "Bond all metal structures"),
                ("Conductor Sizing", None, "Size grounding conductors"),
                ("Arc Flash", None, "Assess incident energy and PPE"),
            ]
        },
        "lighting": {
            "description": "Design lighting system for space",
            "steps": [
                ("Lux Requirement", "illumination_lumen_method", "Target light level"),
                ("Total Lumens", "illumination_lumen_method", "Calculate needed lumens"),
                ("Fixture Layout", None, "Arrange fixtures for uniformity"),
                ("Load Calculation", "power_ac_3ph", "Sum connected lighting load"),
                ("Controls", None, "Occupancy, daylighting, timer control"),
            ]
        },
        "motor": {
            "description": "Design motor circuit with protection",
            "steps": [
                ("Motor Power", "power_ac_3ph", "HP/kW input calculation"),
                ("Feeder Cable", "voltage_drop_3ph", "Size for start voltage dip"),
                ("Starter Type", None, "DOL, soft-start, or VFD"),
                ("Overload Setting", None, "Protection per nameplate"),
                ("Disconnect", "apparent_power_3ph", "Switch for disconnect"),
            ]
        },
        "transformer": {
            "description": "Select and size transformer",
            "steps": [
                ("Load Demand", "apparent_power_3ph", "Total demand in kVA"),
                ("Transformer Size", "transformer_kva", "Standard kVA selection"),
                ("Loss Calculation", None, "Copper and iron losses"),
                ("Cooling Type", None, "ONAN, ONAF, OFAF"),
                ("Protection", "short_circuit_mva", "Overcurrent coordination"),
            ]
        },
        "panel": {
            "description": "Schedule main distribution panel",
            "steps": [
                ("Phase Balance", "power_ac_3ph", "Distribute loads evenly"),
                ("Main Breaker", "apparent_power_3ph", "Size main protective device"),
                ("Circuits", None, "Create detailed schedule"),
                ("Busbar", None, "Design for current and heat"),
                ("One-Line", None, "Schematic and directory"),
            ]
        },
        "pf_correction": {
            "description": "Power factor correction",
            "steps": [
                ("Current PF", "power_factor", "Measure/estimate existing"),
                ("Reactive Power", "power_ac_3ph", "kVAR needed for target"),
                ("Capacitor Bank", None, "Fixed or switched unit"),
                ("Controller", "electrical_inductive_reactance", "Auto regulation"),
                ("Detuning", "electrical_impedance_series", "Resonance prevention"),
            ]
        },
        "solar": {
            "description": "Solar PV system design",
            "steps": [
                ("Energy Analysis", None, "Annual consumption review"),
                ("PV Array", None, "Capacity calculation"),
                ("DC Wiring", "voltage_drop_dc", "Array to inverter sizing"),
                ("Inverter", None, "String or central type"),
                ("Grid Integration", "voltage_drop_3ph", "AC interconnection design"),
            ]
        },
        "generator": {
            "description": "Standby generator sizing",
            "steps": [
                ("Critical Loads", "apparent_power_3ph", "Essential load sum"),
                ("Genset Size", None, "1.25x critical with margin"),
                ("Fuel Tank", None, "Run time capacity"),
                ("Transfer Switch", "voltage_drop_3ph", "ATS with loading"),
                ("Testing", None, "Maintenance schedule"),
            ]
        },
    },
    "mechanical": {
        "hvac_load": {
            "description": "HVAC load calculation and equipment sizing",
            "steps": [
                ("Sensible Load", "hvac_sensible_load", "Space cooling/heating"),
                ("Latent Load", "hvac_latent_load", "Dehumidification need"),
                ("Total Capacity", None, "Sensible + latent + margin"),
                ("Equipment", "cop", "Chiller or furnace with COP"),
                ("Distribution", None, "Central vs distributed"),
            ]
        },
        "duct_design": {
            "description": "Ductwork sizing and balancing",
            "steps": [
                ("Airflow", "continuity_flow", "CFM from load and ΔT"),
                ("Main Duct", "darcy_weisbach", "Velocity 400-500 fpm"),
                ("Branches", "darcy_weisbach", "Velocity 200-300 fpm"),
                ("Pressure Drop", "darcy_weisbach", "System total Pa"),
                ("Fan Selection", "fan_power", "CFM and head rating"),
            ]
        },
        "piping": {
            "description": "Hydronic system piping and pump sizing",
            "steps": [
                ("Flow Rate", "continuity_flow", "GPM calculation"),
                ("Pipe Diameter", "darcy_weisbach", "Optimal velocity 3-6 ft/s"),
                ("Friction Loss", "darcy_weisbach", "Pressure drop per meter"),
                ("Valve Losses", None, "Regulators and check valves"),
                ("Pump Power", "pump_power", "kW for total head"),
            ]
        },
        "insulation": {
            "description": "Thermal insulation optimization",
            "steps": [
                ("Heat Transfer", "heat_transfer_conduction", "Bare surface loss"),
                ("Insulation", "heat_transfer_conduction", "Thickness modeling"),
                ("Annual Savings", None, "kWh and cost reduction"),
                ("Payback", None, "ROI calculation"),
                ("Vapor Barrier", None, "Moisture protection"),
            ]
        },
        "heat_exchanger": {
            "description": "Heat exchanger sizing and selection",
            "steps": [
                ("Heat Duty", "mechanical_heat_exchanger", "kW to transfer"),
                ("Temperatures", "mechanical_heat_exchanger", "Inlet/outlet temps"),
                ("LMTD", "mechanical_heat_exchanger", "Log-mean temperature"),
                ("Selection", None, "Plate, shell-tube, brazed"),
                ("Fouling", "continuity_flow", "Velocity control"),
            ]
        },
        "pump": {
            "description": "Pump system design and motor sizing",
            "steps": [
                ("Flow", "continuity_flow", "Required GPM"),
                ("Head", "pump_power", "Static + friction total"),
                ("Pump", "pump_power", "Operating point selection"),
                ("Motor", "pump_power", "Power requirement"),
                ("Control", None, "VFD or throttle control"),
            ]
        },
        "compressor": {
            "description": "Air compressor and storage tank design",
            "steps": [
                ("Air Demand", "continuity_flow", "SCFM at pressure"),
                ("Peak Load", None, "Simultaneous usage"),
                ("Storage", "ideal_gas", "Receiver tank volume"),
                ("Compressor", "compressor_power", "Type and size"),
                ("Power Cost", "compressor_power", "Annual electricity"),
            ]
        },
        "cooling_tower": {
            "description": "Cooling tower sizing and selection",
            "steps": [
                ("Heat Load", "cop", "Condenser heat rejection"),
                ("Approach", None, "Water-to-wet-bulb temp"),
                ("Water Flow", "continuity_flow", "Circulation GPM"),
                ("Tower Type", None, "Cross-flow vs counter-flow"),
                ("Fan Power", "fan_power", "Fan motor kW"),
            ]
        },
        "boiler": {
            "description": "Boiler sizing for heating and DHW",
            "steps": [
                ("Space Heat", "heat_transfer_conduction", "Building load calculation"),
                ("DHW", None, "Domestic hot water demand"),
                ("Capacity", None, "BTU/hr at 1.2x peak"),
                ("Fuel Type", None, "Gas, oil, or electric"),
                ("Efficiency", None, "AFUE rating selection"),
            ]
        },
        "vibration": {
            "description": "Vibration isolation mount design",
            "steps": [
                ("Frequency", "reynolds_number", "Equipment operating Hz"),
                ("Target", None, "Natural freq at 1/3 operating"),
                ("Mount Type", None, "Spring vs elastomeric"),
                ("Deflection", None, "Static/dynamic check"),
                ("Installation", None, "Leveling and alignment"),
            ]
        },
    },
    "civil": {
        "structural_analysis": {
            "description": "Structural load analysis and member design",
            "steps": [
                ("Dead Load", "beam_bending_stress", "Self-weight calculation"),
                ("Live Load", "beam_bending_stress", "Occupancy load per code"),
                ("Environmental", "beam_bending_stress", "Wind and seismic"),
                ("Load Cases", None, "LRFD/ASD combinations"),
                ("Critical Members", None, "Max moment/shear identification"),
            ]
        },
        "beam_design": {
            "description": "Beam bending and shear design",
            "steps": [
                ("Span", "beam_bending_stress", "Geometry and loading"),
                ("Moment", "beam_bending_stress", "Maximum bending moment"),
                ("Shear", "beam_bending_stress", "Maximum shear force"),
                ("Section", "beam_bending_stress", "Member selection"),
                ("Deflection", "beam_deflection_ss_udl", "L/240 or L/360 limit"),
            ]
        },
        "column_design": {
            "description": "Column axial load and buckling design",
            "steps": [
                ("Axial Load", "axial_stress", "Sum loads from above"),
                ("Length", "column_buckling", "Unsupported length KL"),
                ("Slenderness", "column_buckling", "KL/r ratio"),
                ("Allowable", "column_buckling", "Stress verification"),
                ("Rebar", None, "Reinforcement design"),
            ]
        },
        "foundation": {
            "description": "Foundation design for bearing and settlement",
            "steps": [
                ("Loads", "axial_stress", "Column loads transfer"),
                ("Bearing", "bearing_pressure", "Soil capacity check"),
                ("Footing Area", "bearing_pressure", "Size for service load"),
                ("Settlement", "settlement_elastic", "Elastic and consolidation"),
                ("Rebar", None, "Moment and shear reinforcement"),
            ]
        },
        "concrete": {
            "description": "Concrete mix proportioning",
            "steps": [
                ("Strength", None, "f'c requirement from design"),
                ("W/C Ratio", None, "Water-cement relationship"),
                ("Slump", None, "Workability selection"),
                ("Air Content", None, "Entrained air for durability"),
                ("Proportions", None, "Cement:Sand:Aggregate:Water"),
            ]
        },
        "retaining_wall": {
            "description": "Retaining wall stability design",
            "steps": [
                ("Height", "retaining_wall_active_pressure", "Wall geometry"),
                ("Earth Pressure", "retaining_wall_active_pressure", "Active/passive pressure"),
                ("Overturning", None, "Moment resistance check"),
                ("Sliding", None, "Friction resistance check"),
                ("Bearing", "bearing_pressure", "Base pressure within limits"),
            ]
        },
        "slope": {
            "description": "Slope stability analysis",
            "steps": [
                ("Geometry", None, "Height, angle, profile"),
                ("Soil Data", None, "Friction angle, cohesion"),
                ("Failure Surface", None, "Critical circle search"),
                ("Factor of Safety", None, "Bishop or Fellenius method"),
                ("Remediation", None, "Stabilization if FS inadequate"),
            ]
        },
        "pavement": {
            "description": "Flexible pavement design",
            "steps": [
                ("Traffic", None, "Design ESALs over life"),
                ("Subgrade", None, "CBR testing/estimation"),
                ("SN", None, "AASHTO structural number"),
                ("Layers", None, "Asphalt, base, subbase (mm)"),
                ("Drainage", None, "Permeable base, edge drains"),
            ]
        },
        "stormwater": {
            "description": "Stormwater runoff and drainage design",
            "steps": [
                ("Rainfall", None, "Design storm frequency"),
                ("Runoff", None, "Coefficient by surface type"),
                ("Peak Flow", "manning_flow", "Rational or SCS method"),
                ("Pipes", "manning_flow", "Manning equation sizing"),
                ("Detention", None, "Pond volume calculation"),
            ]
        },
        "excavation": {
            "description": "Excavation and earthworks planning",
            "steps": [
                ("Existing", None, "Baseline elevation survey"),
                ("Design", None, "Required pad elevation"),
                ("Volumes", None, "Cut/fill by average end area"),
                ("Balance", None, "Borrow vs excess determination"),
                ("Compaction", None, "Method and specification"),
            ]
        },
    }
}

def create_workflow_config_table():
    """Create table to store workflow patterns dynamically."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Check if table exists
    cur.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='workflow_templates'
    """)
    
    if cur.fetchone():
        print("⚠️  Table workflow_templates already exists. Skipping creation.")
        conn.close()
        return
    
    # Create table
    cur.execute("""
        CREATE TABLE workflow_templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain VARCHAR(50) NOT NULL,
            template_name VARCHAR(100) NOT NULL,
            description TEXT,
            steps_config JSON,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(domain, template_name)
        )
    """)
    
    conn.commit()
    
    # Populate with default patterns
    print("Populating workflow templates from defaults...")
    for domain, patterns in DEFAULT_WORKFLOW_PATTERNS.items():
        for pattern_name, pattern_data in patterns.items():
            steps_config = json.dumps({
                "description": pattern_data["description"],
                "steps": [
                    {
                        "name": step[0],
                        "calculation": step[1],
                        "description": step[2]
                    }
                    for step in pattern_data["steps"]
                ]
            })
            
            cur.execute("""
                INSERT INTO workflow_templates 
                (domain, template_name, description, steps_config)
                VALUES (?, ?, ?, ?)
            """, (domain, pattern_name, pattern_data["description"], steps_config))
    
    conn.commit()
    
    # Show what we created
    cur.execute("""
        SELECT domain, COUNT(*) as count 
        FROM workflow_templates 
        GROUP BY domain
    """)
    
    print("\n✅ Workflow templates created:")
    for domain, count in cur.fetchall():
        print(f"   {domain}: {count} templates")
    
    conn.close()

if __name__ == "__main__":
    create_workflow_config_table()
