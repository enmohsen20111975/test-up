"""
Transform generic workflows into practical multi-step engineering workflows.
Links each workflow to a smart chain of calculations from the database.
Acts as an engineer designing real workflow sequences.
"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "workflows.db"

# Engineering workflow patterns - real-world problem solving chains
WORKFLOW_CHAINS = {
    "electrical": {
        "load_analysis_and_service_sizing": [
            ("Connected Load Calculation", "apparent_power_3ph", "Sum all connected electrical loads in circuit"),
            ("Demand Factor Application", None, "Apply demand factor based on building type and occupancy"),
            ("Diversified Load Calculation", None, "Apply diversity factor for simultaneous use"),
            ("Service Sizing", "transformer_kva", "Select standard transformer size for system"),
            ("Three-Phase Parameters", "power_ac_3ph", "Verify three-phase power balance and supply"),
        ],
        
        "cable_and_protection_design": [
            ("Circuit Current Calculation", "apparent_power_3ph", "Calculate design current from kVA and voltage"),
            ("Cable Selection", "voltage_drop_3ph", "Select cable size based on ampacity and voltage drop"),
            ("Voltage Drop Verification", "voltage_drop_3ph", "Ensure voltage drop is within 3% (max 5%)"),
            ("Breaker Sizing", None, "Size breaker at 1.25x design current (protection rule)"),
            ("Short Circuit Coordination", "short_circuit_mva", "Verify breaker withstand for fault current"),
        ],
        
        "grounding_and_safety": [
            ("Fault Current Calculation", "short_circuit_mva", "Calculate 3-phase and single-line-to-ground fault"),
            ("Grounding Electrode Design", "grounding_rod", "Size grounding rods or mat for system"),
            ("Ground Resistance Check", "grounding_rod", "Verify electrode resistance < 5Ω (or per standard)"),
            ("Bonding Requirements", None, "Bond all metal equipment and building frame"),
            ("Arc Flash Assessment", None, "Calculate incident energy for PPE requirements"),
        ],
        
        "lighting_system": [
            ("Space Illumination Requirement", "illumination_lumen_method", "Calculate total lumens needed for target lux"),
            ("Fixture Layout", "illumination_lumen_method", "Determine fixture spacing and uniformity"),
            ("Connected Load", "power_ac_3ph", "Calculate total connected lighting load in watts"),
            ("Circuit Organization", None, "Group fixtures into logical circuits (20A/15A)"),
            ("Control Strategy", None, "Specify occupancy sensors, daylight harvesting, scheduling"),
        ],
        
        "motor_circuit_design": [
            ("Motor Input Power", "power_ac_3ph", "Calculate input kW from output HP/kW"),
            ("Feeder Cable Sizing", "voltage_drop_3ph", "Size motor feeder cable for expected voltage drop"),
            ("Starter Selection", None, "Select motor starter type (DOL, soft-start, VFD)"),
            ("Overload Protection", None, "Set overload relay per motor nameplate FLA"),
            ("Disconnect Rating", "apparent_power_3ph", "Provide disconnect switch rated for circuit"),
        ],
        
        "transformer_selection": [
            ("Load Demand", "apparent_power_3ph", "Calculate total demand load in kVA"),
            ("Transformer Size", "transformer_kva", "Select standard transformer (25/37.5/50 kVA)"),
            ("Loss Calculation", None, "Calculate transformer losses at 75% loading"),
            ("Cooling Method", None, "Specify cooling (ONAN/ONAF/OFAF)"),
            ("Protection Coordination", "short_circuit_mva", "Coordinate primary and secondary protection"),
        ],
        
        "distribution_panel_design": [
            ("Phase Load Balance", "power_ac_3ph", "Distribute loads evenly across three phases"),
            ("Main Breaker Sizing", "apparent_power_3ph", "Size main breaker for total connected load"),
            ("Branch Circuit Schedule", None, "Create schedule of all circuits with ratings"),
            ("Busbar Configuration", None, "Design busbar for current capacity and heat"),
            ("Labeling and Documentation", None, "Create one-line diagram and circuit directory"),
        ],
        
        "power_factor_correction": [
            ("Existing Power Factor", "power_factor", "Measure or estimate current power factor"),
            ("Reactive Power Need", "power_ac_3ph", "Calculate kVAR for correction to target PF"),
            ("Capacitor Bank Sizing", None, "Size fixed or switched capacitor bank"),
            ("Switching Device", "electrical_inductive_reactance", "Select automatic power factor controller"),
            ("Harmonic Detuning", "electrical_impedance_series", "Add detuning reactor if needed"),
        ],
        
        "solar_pv_system": [
            ("Annual Energy Need", None, "Analyze building annual consumption"),
            ("Solar Array Size", None, "Calculate PV capacity needed (accounting for losses)"),
            ("DC Wiring", "voltage_drop_dc", "Size DC wiring from array to inverter"),
            ("Inverter Selection", None, "Choose inverter type and capacity"),
            ("AC Integration", "voltage_drop_3ph", "Design AC feeder and protection to grid/load"),
        ],
        
        "standby_generator": [
            ("Critical Load Analysis", "apparent_power_3ph", "Identify and sum critical loads during outage"),
            ("Generator Sizing", None, "Size genset at 1.25x critical load + inrush"),
            ("Fuel System", None, "Design fuel tank for required run time"),
            ("Automatic Transfer Switch", "voltage_drop_3ph", "Specify ATS with load transfer logic"),
            ("Simulation Testing", None, "Plan functional testing and maintenance schedule"),
        ],
    },
    
    "mechanical": {
        "hvac_load_and_system_selection": [
            ("Sensible Cooling Load", "hvac_sensible_load", "Calculate sensible load from building envelope"),
            ("Latent Cooling Load", "hvac_latent_load", "Calculate moisture removal requirement"),
            ("Total Cooling Demand", None, "Sum sensible and latent into total kW"),
            ("Equipment Selection", "cop", "Select chiller with appropriate COP"),
            ("Distribution System", None, "Choose central, distributed, or hybrid chilled water"),
        ],
        
        "duct_design_and_sizing": [
            ("Airflow Requirement", "continuity_flow", "Calculate CFM from cooling load and ∆T"),
            ("Duct Velocity Analysis", "darcy_weisbach", "Size main duct for 400-500 fpm (optimal)"),
            ("Branch Sizing", "darcy_weisbach", "Size branch ducts for 200-300 fpm"),
            ("Pressure Drop", "darcy_weisbach", "Calculate total system pressure loss"),
            ("Fan Selection", "fan_power", "Select supply and return fans for CFM and pressure"),
        ],
        
        "piping_and_pressure_drop": [
            ("Flow Rate Calculation", "continuity_flow", "Calculate chilled water or hot water flow"),
            ("Pipe Sizing", "darcy_weisbach", "Select pipe diameter for acceptable velocity"),
            ("Friction Loss", "darcy_weisbach", "Calculate piping friction pressure drop"),
            ("Valve Losses", None, "Account for control valves, balancing valves, etc."),
            ("Pump Power", "pump_power", "Calculate pump power needed for total head"),
        ],
        
        "thermal_insulation_optimization": [
            ("Heat Loss (Bare)", "heat_transfer_conduction", "Calculate heat transfer without insulation"),
            ("Insulation Thickness", "heat_transfer_conduction", "Determine optimal thickness for payback"),
            ("Annual Savings", None, "Calculate energy cost savings from insulation"),
            ("Vapor Barrier Requirement", None, "Specify moisture protection strategy"),
            ("Installation Cost", None, "Estimate material and labor cost"),
        ],
        
        "heat_exchanger_design": [
            ("Heat Transfer Rate", "mechanical_heat_exchanger", "Determine kW to be transferred"),
            ("Temperature Approach", "mechanical_heat_exchanger", "Define entering/leaving water temperatures"),
            ("LMTD Calculation", "mechanical_heat_exchanger", "Calculate log-mean temperature difference"),
            ("Exchanger Selection", None, "Choose plate-frame, shell-tube, or brazed plate"),
            ("Flow Velocity Check", "continuity_flow", "Verify water velocity for fouling control"),
        ],
        
        "pump_system_design": [
            ("System Flow Rate", "continuity_flow", "Determine GPM for application"),
            ("Total Dynamic Head", "pump_power", "Calculate friction + static head"),
            ("Pump Selection", "pump_power", "Choose pump type and size from curve"),
            ("Motor Sizing", "pump_power", "Calculate required motor power"),
            ("Throttling Control", None, "Specify variable frequency drive or control valve"),
        ],
        
        "compressor_selection": [
            ("Air Demand", "continuity_flow", "Estimate CFM at working pressure"),
            ("Peak vs Average", None, "Determine simultaneous vs stored compressed air"),
            ("Storage Tank", "ideal_gas", "Size air receiver for peak demand"),
            ("Compressor Type", "compressor_power", "Choose rotary screw vs reciprocating"),
            ("Power Consumption", "compressor_power", "Calculate annual energy cost"),
        ],
        
        "cooling_tower_design": [
            ("Condenser Heat Load", "cop", "Calculate heat rejection from chiller"),
            ("Approach Temperature", None, "Define cooled water to outdoor wet-bulb difference"),
            ("Water Flow Rate", "continuity_flow", "Calculate GPM for cooling tower"),
            ("Tower Type", None, "Select cooling tower type (counterflow, crossflow)"),
            ("Fan Power", "fan_power", "Calculate cooling tower fan motor requirement"),
        ],
        
        "boiler_sizing": [
            ("Space Heating Load", "heat_transfer_conduction", "Calculate building heating requirement"),
            ("Domestic Hot Water", None, "Add DHW demand for recovery time"),
            ("Boiler Capacity", None, "Size boiler at 1.2x peak load"),
            ("Fuel Type", None, "Choose natural gas, oil, or electric"),
            ("Efficiency Rating", None, "Select AFUE class (85-95%)"),
        ],
        
        "vibration_isolation": [
            ("Equipment Frequency", "reynolds_number", "Identify operating frequency (Hz)"),
            ("Natural Frequency Target", None, "Set isolation target at 1/3 operating frequency"),
            ("Mount Selection", None, "Choose elastomeric or spring mounts"),
            ("Deflection Check", None, "Verify mount deflection at operating condition"),
            ("Installation Verification", None, "Confirm proper leveling and alignment"),
        ],
    },
    
    "civil": {
        "structural_load_analysis": [
            ("Dead Load Calculation", "beam_bending_stress", "Calculate structural self-weight"),
            ("Live Load Application", "beam_bending_stress", "Apply occupancy-based live load"),
            ("Environmental Load", "beam_bending_stress", "Include wind and seismic as applicable"),
            ("Load Combinations", None, "Create LRFD/ASD load cases"),
            ("Critical Members", None, "Identify members with maximum forces"),
        ],
        
        "beam_design": [
            ("Span and Loading", "beam_bending_stress", "Establish beam geometry and load pattern"),
            ("Bending Moment", "beam_bending_stress", "Calculate maximum moment and shear"),
            ("Section Selection", "beam_bending_stress", "Choose section for stress allowable"),
            ("Deflection Check", "beam_deflection_ss_udl", "Verify L/240 limit"),
            ("Connection Design", None, "Design beam-column connections"),
        ],
        
        "column_design": [
            ("Axial Load", "axial_stress", "Sum all loads on column from above"),
            ("Slenderness Ratio", "column_buckling", "Calculate KL/r for buckling check"),
            ("Buckling Analysis", "column_buckling", "Verify allowable axial stress"),
            ("Reinforcement Layout", None, "Design rebar for axial + moments"),
            ("Tier Connection", None, "Detail column splice and bearing plates"),
        ],
        
        "foundation_design": [
            ("Column Load", "axial_stress", "Obtain design loads from superstructure"),
            ("Bearing Capacity", "bearing_pressure", "Calculate allowable soil bearing pressure"),
            ("Footing Area", "bearing_pressure", "Size footing for service load pressure"),
            ("Settlement Estimation", "settlement_elastic", "Calculate elastic and consolidation settlement"),
            ("Reinforcement Design", None, "Design footing rebar for moment"),
        ],
        
        "concrete_mix": [
            ("Strength Requirement", None, "Determine f'c from structural design"),
            ("Water-Cement Ratio", None, "Establish w/c from strength relationship"),
            ("Slump Selection", None, "Choose workability for placement method"),
            ("Air Content", None, "Account for entrained air for durability"),
            ("Proportioning", None, "Calculate cement, sand, coarse aggregate, water"),
        ],
        
        "retaining_wall": [
            ("Wall Height", "retaining_wall_active_pressure", "Establish design height"),
            ("Earth Pressure", "retaining_wall_active_pressure", "Calculate active pressure diagram"),
            ("Overturning Check", None, "Verify overturning moment resistance"),
            ("Sliding Check", None, "Verify frictional resistance to sliding"),
            ("Bearing Check", "bearing_pressure", "Verify base pressure within allowable"),
        ],
        
        "slope_stability": [
            ("Slope Geometry", None, "Define height, angle, soil profile"),
            ("Soil Properties", None, "Obtain friction angle and cohesion"),
            ("Critical Surface", None, "Identify critical failure surface"),
            ("Factor of Safety", None, "Calculate FS using Bishop or Fellenius method"),
            ("Stabilization Design", None, "Add berms, drains, or walls if FS inadequate"),
        ],
        
        "pavement_design": [
            ("Traffic Analysis", None, "Calculate design ESALs over life"),
            ("Subgrade CBR", None, "Test or estimate subgrade California Bearing Ratio"),
            ("Structural Number", None, "Use AASHTO to find required SN"),
            ("Layer Thickness", None, "Design asphalt, base, subbase layers"),
            ("Drainage Design", None, "Specify permeable base and edge drainage"),
        ],
        
        "stormwater_drainage": [
            ("Runoff Coefficient", None, "Determine for development site type"),
            ("Rainfall Intensity", None, "Use IDF curve for design storm frequency"),
            ("Peak Flow", "manning_flow", "Calculate using Rational Method or SCS"),
            ("Pipe Sizing", "manning_flow", "Size pipes with Manning equation"),
            ("Detention Pond", None, "Size basin for maximum 10-year runoff"),
        ],
        
        "excavation_and_earthworks": [
            ("Existing Grades", None, "Survey existing ground level"),
            ("Design Grades", None, "Establish finished pad elevation"),
            ("Cut/Fill Volumes", None, "Calculate using average end area method"),
            ("Borrow/Haul", None, "Determine if borrow pit or excess disposal needed"),
            ("Compaction Requirement", None, "Specify compaction percentage and method"),
        ],
    }
}

def get_calculation_id(conn, calc_name):
    """Find calculation ID in database by partial name match."""
    cur = conn.cursor()
    
    # Try exact match first
    cur.execute("SELECT id FROM equations WHERE name LIKE ? LIMIT 1", (f"%{calc_name}%",))
    result = cur.fetchone()
    return result[0] if result else None

def update_workflow_steps(db_path):
    """Transform workflows into multi-step engineering workflows."""
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    print("=" * 70)
    print("ENGINEERING WORKFLOW TRANSFORMATION")
    print("=" * 70)
    
    try:
        for domain, workflow_chains in WORKFLOW_CHAINS.items():
            print(f"\n🔧 {domain.upper()} Domain - Creating workflow step chains...")
            
            for workflow_pattern, step_definitions in workflow_chains.items():
                # Find workflow matching this pattern (by title containing key words)
                keywords = workflow_pattern.split('_')[:2]  # Take first 2 words
                search_pattern = '%'.join(keywords)
                
                # Query for workflows matching pattern
                cur.execute("""
                    SELECT id, workflow_id, title
                    FROM workflows
                    WHERE domain = ? AND title LIKE ?
                    LIMIT 1
                """, (domain, f"%{search_pattern}%"))
                
                workflow = cur.fetchone()
                if not workflow:
                    # Try to find any unlinked workflow in this domain
                    cur.execute("""
                        SELECT id, workflow_id, title
                        FROM workflows
                        WHERE domain = ? 
                        AND id NOT IN (SELECT DISTINCT workflow_id FROM workflow_steps WHERE calculation_id IS NOT NULL)
                        LIMIT 1
                    """, (domain,))
                    workflow = cur.fetchone()
                
                if not workflow:
                    print(f"  ⚠️  No workflows found for {workflow_pattern}")
                    continue
                
                wf_id, wf_id_str, wf_title = workflow
                
                # Clear existing steps for this workflow
                cur.execute("DELETE FROM workflow_steps WHERE workflow_id = ?", (wf_id,))
                conn.commit()
                
                # Insert new step chain
                for step_num, (step_name, calc_name, description) in enumerate(step_definitions, 1):
                    calculation_id = None
                    
                    # If calculation name provided, find it
                    if calc_name:
                        cur.execute("""
                            SELECT id FROM equations
                            WHERE name LIKE ?
                            LIMIT 1
                        """, (f"%{calc_name}%",))
                        result = cur.fetchone()
                        calculation_id = result[0] if result else None
                    
                    # Get equation from calculation if found
                    equation = None
                    if calculation_id:
                        cur.execute("SELECT equation FROM equations WHERE id = ?", (calculation_id,))
                        eq_result = cur.fetchone()
                        equation = eq_result[0] if eq_result else None
                    
                    # Insert step
                    cur.execute("""
                        INSERT INTO workflow_steps 
                        (workflow_id, step_number, name, description, calculation_id, equation)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (wf_id, step_num, step_name, description, calculation_id, equation))
                
                conn.commit()
                print(f"  ✅ {wf_title}: {len(step_definitions)} steps linked")
        
        print("\n" + "=" * 70)
        print("✨ Workflow transformation complete!")
        print("=" * 70)
        
    finally:
        conn.close()

if __name__ == "__main__":
    update_workflow_steps(DB_PATH)
