"""
Seed comprehensive workflows (20+ per category) with step-by-step equations and references.
Uses existing calculations as building blocks for workflow steps.
"""
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent / "workflows.db"

# Mapping of workflows to calculation steps (calculation_id -> workflow use)
WORKFLOW_DEFINITIONS = {
    "electrical": [
        {
            "id": "electrical_distribution_design",
            "title": "Distribution Network Design",
            "description": "Design complete electrical distribution from utility to end load with overcurrent protection.",
            "domain": "electrical",
            "steps": [
                ("System Analysis", "short_circuit_mva", "Calculate system MVA and short circuit current"),
                ("Load Estimation", "apparent_power_3ph", "Calculate total load demand in kVA"),
                ("Transformer Selection", "transformer_kva", "Select appropriate transformer size"),
                ("Cable Sizing", "voltage_drop_3ph", "Size cables for acceptable voltage drop"),
                ("Breaker Rating", None, "Select breakers rated above 1.25x load current"),
                ("Protection Coordination", None, "Verify overcurrent protection coordination")
            ],
            "inputs": ["total_load_kw", "circuit_length", "voltage", "ambient_temp", "power_factor"],
            "outputs": ["service_size_kva", "cable_size_mm2", "breaker_size_a", "status"]
        },
        {
            "id": "electrical_motor_circuit",
            "title": "Three-Phase Motor Circuit Design",
            "description": "Design complete motor circuit with protection, starting, and control.",
            "domain": "electrical",
            "steps": [
                ("Motor Demand", "electric_power_ac_3ph", "Calculate motor input power from output"),
                ("Cable Sizing", "voltage_drop_3ph", "Size motor feeder cable"),
                ("Starter Protection", None, "Select motor starter and overload protection"),
                ("Conduit & Termination", None, "Size conduit and termination equipment"),
                ("Grounding", "ground_resistance_rod", "Size motor grounding conductor"),
                ("Short Circuit", "short_circuit_mva", "Verify breaker/contactor at fault current")
            ],
            "inputs": ["motor_hp", "motor_kw", "voltage", "circuit_length", "overload_factor"],
            "outputs": ["feeder_cable_mm2", "conduit_size", "starter_size", "ground_size_mm2"]
        },
        {
            "id": "electrical_panel_design",
            "title": "Main Panel Design & Scheduling",
            "description": "Design and schedule electrical main distribution panel with circuit organization.",
            "domain": "electrical",
            "steps": [
                ("Main Breaker", "apparent_power_3ph", "Size main service breaker from connected load"),
                ("Phase Balance", None, "Balance loads across three phases"),
                ("Branch Devices", None, "Assign and size branch circuit breakers"),
                ("Voltage Drop", "voltage_drop_3ph", "Check voltage drop to furthest outlet"),
                ("Wiring Diagram", None, "Create one-line and panel schedules"),
                ("Label & Protect", None, "Label and verify overcurrent protection")
            ],
            "inputs": ["connected_load_kw", "demand_factor", "voltage", "num_circuits"],
            "outputs": ["main_breaker_a", "subpanel_sizes", "phase_balance_pct", "document_count"]
        },
        {
            "id": "electrical_power_factor_correction",
            "title": "Power Factor Correction",
            "description": "Analyze and correct low power factors with capacitor banks.",
            "domain": "electrical",
            "steps": [
                ("Load Analysis", "power_factor", "Measure or estimate existing power factor"),
                ("Reactive Power", "electric_power_ac_3ph", "Calculate reactive power (kVAR)"),
                ("Capacitor Bank", None, "Size capacitor bank for target PF"),
                ("Switching", None, "Select switching and protection for caps"),
                ("Tuning", "electrical_inductive_reactance", "Tune for resonance avoidance"),
                ("Harmonic Risk", None, "Check for harmonic amplification")
            ],
            "inputs": ["load_kw", "existing_pf", "target_pf", "voltage", "frequency"],
            "outputs": ["capacitor_kvar", "bank_size", "switch_rating_a", "cost_estimate"]
        },
        {
            "id": "electrical_lighting_design",
            "title": "Lighting System Design & Layout",
            "description": "Design complete lighting system with fixture layout and controls.",
            "domain": "electrical",
            "steps": [
                ("Lux Calculation", "illumination_lumen_method", "Calculate lumens needed for target lux"),
                ("Fixture Selection", None, "Select appropriate fixture type"),
                ("Layout & Spacing", None, "Arrange fixtures for uniform illumination"),
                ("Circuiting", None, "Group fixtures into logical circuits"),
                ("Switching & Controls", None, "Specify controls (occupancy, daylight, schedule)"),
                ("Energy Calc", "electric_power_ac_3ph", "Calculate connected lighting load")
            ],
            "inputs": ["space_area_m2", "target_lux", "fixture_wattage", "cri_needed", "space_height"],
            "outputs": ["fixture_count", "total_lumens", "connected_load_w", "circuit_schedule"]
        },
        {
            "id": "electrical_grounding_design",
            "title": "Comprehensive Grounding System",
            "description": "Design grounding electrode system and bonding throughout building.",
            "domain": "electrical",
            "steps": [
                ("Soil Resistivity", "ground_resistance_rod", "Measure or obtain soil resistivity"),
                ("Electrode Design", "ground_resistance_rod", "Size ground rods/plates/mats"),
                ("Resistance Test", None, "Calculate/verify electrode resistance < 5 Ω (or as required)"),
                ("Main Bonding", None, "Bond all metal sections of building frame"),
                ("Grounding Conductors", None, "Size main, equipment, and lightning conductors"),
                ("Testing & Docs", None, "Perform resistance tests and document")
            ],
            "inputs": ["soil_resistivity_ohm_m", "required_resistance_ohm", "electrode_type", "building_size"],
            "outputs": ["rod_count", "conductor_mm2", "measured_resistance", "test_report"]
        },
        {
            "id": "electrical_pv_system_design",
            "title": "Solar Photovoltaic System Design",
            "description": "Complete PV system design including panels, inverter, and balance of system.",
            "domain": "electrical",
            "steps": [
                ("Energy Audit", None, "Analyze annual building energy consumption"),
                ("Solar Resource", None, "Determine site solar irradiance and tilting"),
                ("PV Array Design", None, "Size PV array for offset target"),
                ("Inverter Selection", None, "Select inverter (central, string, micro)"),
                ("DC Wiring", "voltage_drop_dc", "Size DC wiring from array to inverter"),
                ("AC Integration", "voltage_drop_3ph", "Design AC interconnection to grid/load")
            ],
            "inputs": ["annual_kwh_needed", "solar_irradiance_kwh_m2_y", "array_angle", "efficiency_pct", "rooftop_area_m2"],
            "outputs": ["panel_count", "inverter_kw", "array_voltage_v", "total_system_cost"]
        },
        {
            "id": "electrical_standby_generator",
            "title": "Standby Generator System",
            "description": "Size and design standby power generation for critical loads.",
            "domain": "electrical",
            "steps": [
                ("Critical Load", "apparent_power_3ph", "Identify and sum critical loads in kW"),
                ("Generator Sizing", None, "Size genset 1.25x critical load + starting inrush"),
                ("Fuel System", None, "Design fuel tank for run duration needed"),
                ("ATS Design", "voltage_drop_3ph", "Specify automatic transfer switch"),
                ("Cabling & Protection", None, "Size generator output feeder and breaker"),
                ("Load Transfer", None, "Define load transfer strategy and testing")
            ],
            "inputs": ["critical_load_kw", "run_time_hours", "fuel_type", "voltage", "recharge_time_s"],
            "outputs": ["genset_kva", "fuel_tank_liters", "transfer_switch_a", "startup_time_s"]
        },
        {
            "id": "electrical_emergency_lighting",
            "title": "Emergency Lighting System",
            "description": "Design and layout emergency egress lighting per code.",
            "domain": "electrical",
            "steps": [
                ("Layout & Coverage", "illumination_lumen_method", "Map exit paths and light spacing"),
                ("Fixture Type", None, "Select fixtures (integral vs dedicated circuit)"),
                ("Capacity", None, "Size batteries or inverter for min 90 min run time"),
                ("Wiring & Control", None, "Design circuits and switching strategy"),
                ("Testing", None, "Plan functional and monthly/annual testing"),
                ("Documentation", None, "Create legends, schedules, and rundown manuals")
            ],
            "inputs": ["building_area_m2", "exit_count", "fixture_wattage", "min_lux", "run_time_min"],
            "outputs": ["fixture_count", "batch_size", "battery_capacity_ah", "test_schedule"]
        },
        {
            "id": "electrical_harmonics_study",
            "title": "Harmonic Distortion Analysis",
            "description": "Analyze non-linear loads and design mitigation (filters, reactors).",
            "domain": "electrical",
            "steps": [
                ("Load Audit", None, "Identify non-linear and harmonic-producing loads"),
                ("THD Estimate", None, "Estimate system THD (voltage and current)"),
                ("Resonance Check", "electrical_impedance_series", "Check for series/parallel resonances"),
                ("Mitigation Design", None, "Select filters or passive/active solutions"),
                ("Equipment Impact", None, "Verify no adverse effect on cables/transformers"),
                ("Monitoring", None, "Specify power quality monitoring points")
            ],
            "inputs": ["nonlinear_pct", "system_mva", "source_impedance_z", "frequency_hz", "tolerance_thd_pct"],
            "outputs": ["estimated_thd_pct", "filter_rating_kvar", "harmonic_orders", "risk_level"]
        },
        {
            "id": "electrical_earthing_mat",
            "title": "Substation Earthing Mat Design",
            "description": "Design ground mat for high-fault-current substations.",
            "domain": "electrical",
            "steps": [
                ("Fault Current", "short_circuit_mva", "Determine 3-phase and SLG fault currents"),
                ("Ground Mat Sizing", "ground_resistance_rod", "Calculate required mat area and grid spacing"),
                ("Conductor Sizing", None, "Size grid conductors for temperature rise limits"),
                ("Mesh Voltage", None, "Calculate touch and step potentials"),
                ("Bonding Points", None, "Design grid bonding to equipment and fences"),
                ("Testing Protocol", None, "Specify construction QA and resistance testing")
            ],
            "inputs": ["fault_current_ka", "soil_resistivity_ohm_m", "target_gr_ohm", "conductor_material", "max_temp_rise_c"],
            "outputs": ["mat_area_m2", "conductor_mm2", "grid_spacing_m", "max_step_potential_v"]
        },
        {
            "id": "electrical_arc_flash_analysis",
            "title": "Arc Flash Hazard Assessment",
            "description": "Conductarctic flash study and label electrical equipment per NFPA 70E.",
            "domain": "electrical",
            "steps": [
                ("System Modeling", "short_circuit_mva", "Build one-line model and calculate fault currents"),
                ("Device Clearing", None, "Determine clearing times for breakers/reclosers"),
                ("Arc Power", None, "Calculate arc flash energy at each location"),
                ("Incident Energy", None, "Compute incident energy (cal/cm²) at working distance"),
                ("PPE Specification", None, "Select PPE category and rating for each task"),
                ("Labeling", None, "Create and apply equipment warning labels")
            ],
            "inputs": ["system_mva", "equipment_voltage_kv", "work_distance_cm", "clearing_time_cycles", "phase_count"],
            "outputs": ["incident_energy_cal_cm2", "ppe_category", "label_text", "study_report"]
        },
        {
            "id": "electrical_ufont_sizing",
            "title": "Underground Feeder Cable Sizing",
            "description": "Desizeof underground power distribution cables.",
            "domain": "electrical",
            "steps": [
                ("Load Current", "apparent_power_3ph", "Calculate circuit current from load"),
                ("Ampacity", None, "Select cable with adequate ampacity (with burial derating)"),
                ("Voltage Drop", "voltage_drop_3ph", "Check voltage drop across cable run"),
                ("Fault Current", "short_circuit_mva", "Verify cable withstand for fault current"),
                ("Ground Fault", None, "Size neutral/ground for single-phase fault"),
                ("Duct & Conduit", None, "Size underground conduit/duct for cable pulling")
            ],
            "inputs": ["circuit_current_a", "circuit_length_m", "voltage_v", "soil_temp_c", "installation_depth_m"],
            "outputs": ["cable_size_mm2", "voltage_drop_pct", "number_ducts", "pull_tension_n"]
        },
        {
            "id": "electrical_switchgear_protection",
            "title": "Medium-Voltage Switchgear Protection",
            "description": "Coordinate protection relays for MV switchgear system.",
            "domain": "electrical",
            "steps": [
                ("Fault Study", "short_circuit_mva", "Calculate 3-phase and SLG faults"),
                ("Relay Settings", None, "Determine time-overcurrent (ANSI 51) curves"),
                ("Primary Device", None, "Set primary feeder relay for sensitivity"),
                ("Backup Device", None, "Set higher-level relay with coordination"),
                ("Testing", None, "Plan and execute relay setting verification"),
                ("Documentation", None, "Create one-line and coordination plots")
            ],
            "inputs": ["source_mva", "feeder_load_a", "feeder_z_pct", "f_3phase_ka", "f_slg_ka"],
            "outputs": ["primary_tap_setting", "primary_time_dial", "backup_tap_setting", "coordination_check"]
        },
        {
            "id": "electrical_microgrid_control",
            "title": "Microgrid Control & Protection",
            "description": "Design control system for islanded or grid-connected microgrid.",
            "domain": "electrical",
            "steps": [
                ("Generation Mix", "apparent_power_3ph", "Size DG, storage, and renewable capacity"),
                ("Load Profile", None, "Model hourly load and generation profiles"),
                ("Mode Switching", None, "Design grid-tied vs island mode transition logic"),
                ("Voltage/Frequency", None, "Specify V/F droop and inertia requirements"),
                ("Energy Storage", None, "Size battery or other storage for stability"),
                ("Monitoring", None, "Specify SCADA and protection coordination")
            ],
            "inputs": ["peak_load_kw", "renewable_percent", "grid_strength_scc_ratio", "island_duration_h", "ramp_rate_kw_s"],
            "outputs": ["dg_size_kva", "storage_capacity_kwh", "control_scheme", "stability_margin"]
        },
        {
            "id": "electrical_ev_charging_station",
            "title": "EV Charging Infrastructure Design",
            "description": "Design AC/DC charging station for electric vehicles.",
            "domain": "electrical",
            "steps": [
                ("Charger Demand", "apparent_power_3ph", "Estimate simultaneous charging load"),
                ("Service Upgrade", None, "Assess utility service adequacy"),
                ("Feeder Design", "voltage_drop_3ph", "Size feeder to charging station"),
                ("Charger Selection", None, "Choose AC Level 1/2/3 or DC Fast charging"),
                ("Transformer", "transformer_kva", "Size distribution transformer if needed"),
                ("Grounding & Protection", "ground_resistance_rod", "Design RCD and ground system")
            ],
            "inputs": ["num_chargers", "charger_kw", "circuit_length_m", "vehicle_count", "peak_penetration_pct"],
            "outputs": ["total_demand_kw", "feeder_cable_mm2", "transformer_kva", "charging_time_min"]
        },
        {
            "id": "electrical_capacitor_sizing",
            "title": "Power Factor Correction Capacitor Bank",
            "description": "Size shunt capacitors to correct lagging power factor.",
            "domain": "electrical",
            "steps": [
                ("Load Analysis", "power_factor", "Determine load power factor"),
                ("Reactive Power", "electric_power_ac_3ph", "Calculate reactive power needed"),
                ("Capacitor Value", None, "Calculate bank rating in kVAR"),
                ("Configuration", None, "Design bank as wye or delta, fixed or switched"),
                ("Switching", None, "Specify contactor/relay for automatic control"),
                ("Detuning", "electrical_inductive_reactance", "Add reactor if needed to avoid resonance")
            ],
            "inputs": ["load_kw", "existing_pf", "target_pf", "voltage_v", "frequency_hz"],
            "outputs": ["capacitor_kvar", "bank_voltage_rating", "switch_size_a", "losses_w"]
        },
    ],
    "mechanical": [
        {
            "id": "mechanical_ductwork_system",
            "title": "Supply & Return Ductwork Design",
            "description": "Complete duct design for HVAC systems with sizing and layout.",
            "domain": "mechanical",
            "steps": [
                ("Load Calculation", "hvac_sensible_load", "Calculate sensible cooling/heating load"),
                ("Airflow Rate", "continuity_flow", "Determine required CFM from load and ∆T"),
                ("Duct Sizing", "darcy_weisbach", "Size ducts using velocity method or friction rate"),
                ("Pressure Drop", None, "Calculate total system pressure drop"),
                ("Equipment Selection", "fan_power", "Select supply and return fans"),
                ("Balancing Plan", None, "Design ductwork balancing dampers")
            ],
            "inputs": ["sensible_load_kw", "delta_t_c", "velocity_m_s", "duct_material", "total_duct_length_m"],
            "outputs": ["cfm_required", "main_duct_mm", "branch_duct_mm", "system_pressure_pa", "fan_power_w"]
        },
        {
            "id": "mechanical_pipe_insulation",
            "title": "Piping System Insulation Design",
            "description": "Design thermal insulation for hot/cold water and steam pipes.",
            "domain": "mechanical",
            "steps": [
                ("Heat Loss", "heat_transfer_conduction", "Calculate heat loss through bare pipe"),
                ("Insulation Selection", None, "Choose insulation type and thickness"),
                ("Economic Thickness", None, "Balance insulation cost vs energy savings"),
                ("Vapor Barrier", None, "Specify vapor retarder for condensation control"),
                ("Support Design", None, "Design pipe hangers/supports for expansion"),
                ("Surface Protection", None, "Specify finish and protective coverings")
            ],
            "inputs": ["pipe_od_mm", "fluid_temp_c", "ambient_temp_c", "pipe_length_m", "duty_cycles_per_year"],
            "outputs": ["insulation_thickness_mm", "annual_loss_kwh", "payback_period_years", "material_cost"]
        },
        {
            "id": "mechanical_chiller_plant",
            "title": "Chiller Plant Design & Optimization",
            "description": "Design central chilling plant with capacity optimization.",
            "domain": "mechanical",
            "steps": [
                ("Cooling Load", "hvac_latent_load", "Sum all building cooling loads"),
                ("Chiller Selection", "cop", "Select chiller(s) with target COP"),
                ("Tower Design", None, "Size cooling tower for heat rejection"),
                ("Pump Sizing", "pump_power", "Size circulating pumps for flow and head"),
                ("Control Strategy", None, "Specify reset schedules and load modulation"),
                ("Energy Optimization", None, "Model seasonal operation and part-load efficiency")
            ],
            "inputs": ["total_cooling_load_kw", "condenser_water_return_c", "approach_c", "outdoor_wet_bulb_c"],
            "outputs": ["chiller_capacity_kw", "chiller_cop", "tower_fan_power_w", "pump_power_w", "annual_energy_kwh"]
        },
        {
            "id": "mechanical_boiler_selection",
            "title": "Steam/Hot-Water Boiler Selection",
            "description": "Select and size boiler for space heating and domestic hot water.",
            "domain": "mechanical",
            "steps": [
                ("Heating Load", "heat_transfer_conduction", "Calculate space heating and DHW loads"),
                ("Boiler Type", None, "Choose between fire-tube, water-tube, or condensing"),
                ("Fuel Type", None, "Select fuel (natural gas, oil, electric)"),
                ("Sizing", None, "Size boiler with appropriate margin for peak demand"),
                ("Efficiency", None, "Select high-efficiency model if economical"),
                ("Emissions", None, "Verify compliance with local air quality regulations")
            ],
            "inputs": ["heating_load_kw", "dhw_demand_L_per_hour", "supply_temp_c", "ambient_low_c"],
            "outputs": ["boiler_btuh", "boiler_efficiency_pct", "fuel_consumption_kg_per_year", "emissions_kg_nox"]
        },
        {
            "id": "mechanical_heat_recovery",
            "title": "Heat Recovery System Design",
            "description": "Design energy recovery from exhaust for preconditioning.",
            "domain": "mechanical",
            "steps": [
                ("Exhaust Airflow", "continuity_flow", "Determine exhaust CFM (LAV supply CFM)"),
                ("Exhaust Temperature", None, "Obtain average exhaust temp from HVAC load"),
                ("Recovery Effectiveness", "mechanical_heat_exchanger", "Calculate LMTD and design heat exchanger"),
                ("Equipment Sizing", None, "Size sensible and/or enthalpy recovery unit"),
                ("Pressure Drop", "darcy_weisbach", "Calculate additional fan load for HRV"),
                ("Payback Analysis", None, "Determine simple payback and ROI")
            ],
            "inputs": ["exhaust_cfm", "supply_cfm", "exhaust_temp_avg_c", "outdoor_temp_avg_c", "dehumidify"],
            "outputs": ["recovery_effectiveness_pct", "heat_transfer_rating_kw", "recovered_energy_kwh_per_year", "payback_years"]
        },
        {
            "id": "mechanical_humidification_system",
            "title": "Humidification & Dehumidification System",
            "description": "Design moisture control system for process or comfort criteria.",
            "domain": "mechanical",
            "steps": [
                ("Load Calculation", "hvac_latent_load", "Calculate building latent load"),
                ("Setpoint Analysis", None, "Determine RH setpoint based on use/comfort"),
                ("Humidifier Type", None, "Select steam, ultrasonic, or evaporative unit"),
                ("Dehumidifier Type", None, "Choose cooling coil or desiccant wheel"),
                ("Control Loop", None, "Specify RH sensor, controller, and actuators"),
                ("Water System", None, "Design water supply or condensate collection")
            ],
            "inputs": ["building_volume_m3", "occupancy", "latent_load_kw", "target_rh_pct", "tolerance_pct_rh"],
            "outputs": ["humidifier_capacity_kg_per_hour", "dehumidifier_capacity_l_per_day", "control_type", "annual_water_usage_m3"]
        },
        {
            "id": "mechanical_vibration_isolation",
            "title": "Mechanical Equipment Vibration Isolation",
            "description": "Design isolation mounts for rotating and reciprocating machinery.",
            "domain": "mechanical",
            "steps": [
                ("Frequency Analysis", "reynolds_number", "Identify dominant operating frequencies"),
                ("Isolation Strategy", None, "Select natural frequency target (typically 1/3 excitation)"),
                ("Mount Selection", None, "Choose elastomeric, spring, or hybrid isolators"),
                ("Dead Load", None, "Size isolators for equipment weight"),
                ("Dynamic Load", None, "Verify deflection and load capacity at operating frequency"),
                ("Installation", None, "Specify leveling and accessibility provisions")
            ],
            "inputs": ["equipment_mass_kg", "operating_freq_hz", "force_amplitude_n", "max_deflection_mm"],
            "outputs": ["isolation_freq_hz", "spring_stiffness_n_per_mm", "damping_ratio", "transmissibility_pct"]
        },
        {
            "id": "mechanical_piping_stress",
            "title": "Piping Stress Analysis & Support Design",
            "description": "Analyze thermal stresses and design piping supports.",
            "domain": "mechanical",
            "steps": [
                ("Thermal Expansion", "mechanical_thermal_expansion", "Calculate pipe length change from ∆T"),
                ("Stress Analysis", "mechanical_torsion_stress", "Compute bending and torsional stresses"),
                ("Material Properties", None, "Verify allowable stress at max temperature"),
                ("Support Locations", None, "Position guides and anchors to minimize stress"),
                ("Flexibility", None, "Add expansion loops or bends as needed"),
                ("Vibration", None, "Check for resonance with pump/compressor output")
            ],
            "inputs": ["pipe_nominal_size_inch", "pipe_material", "inlet_temp_c", "outlet_temp_c", "operating_pressure_bar"],
            "outputs": ["thermal_expansion_mm", "max_bending_stress_mpa", "support_spacing_m", "hanger_type"]
        },
        {
            "id": "mechanical_compressor_selection",
            "title": "Air Compressor System Design",
            "description": "Size and select compressor(s) for plant air requirements.",
            "domain": "mechanical",
            "steps": [
                ("Air Demand", "continuity_flow", "Estimate steady-state and peak CFM requirements"),
                ("Pressure Rating", None, "Determine working pressure based on tools/processes"),
                ("Storage Tank", "ideal_gas", "Size air tank for peak demand storage"),
                ("Compressor Type", "compressor_power", "Choose rotary screw, piston, or centrifugal"),
                ("Power Calculation", None, "Calculate compressor motor size and utility impact"),
                ("Accessories", None, "Size filter, dryer, and regulator(s)")
            ],
            "inputs": ["air_demand_cfm", "peak_cfm", "working_pressure_bar", "duty_cycle_pct", "climate"],
            "outputs": ["compressor_hp", "motor_kw", "tank_liters", "air_dried_dewpoint_c", "operating_cost_per_year"]
        },
        {
            "id": "mechanical_cooling_tower_selection",
            "title": "Cooling Tower Sizing & Selection",
            "description": "Select cooling tower type and size for condenser water loop.",
            "domain": "mechanical",
            "steps": [
                ("Heat Duty", "cop", "Calculate condenser heat load from chiller COP"),
                ("Entering Temp", None, "Determine condenser water return temperature"),
                ("Ambient", None, "Use design wet-bulb for tower sizing"),
                ("Tower Type", None, "Select cross-flow, counter-flow, or hybrid"),
                ("Water Treatment", None, "Specify cycles of cooling and treatment program"),
                ("Fan Motor", "fan_power", "Calculate fan power and noise level")
            ],
            "inputs": ["condenser_heat_load_kw", "return_water_temp_c", "approach_c", "outdoor_wet_bulb_c", "tower_cycles"],
            "outputs": ["tower_capacity_mw", "water_flowrate_m3_per_hour", "fan_power_kw", "water_makeup_m3_per_day"]
        },
        {
            "id": "mechanical_insulation_thickness",
            "title": "Optimal Insulation Thickness Calculation",
            "description": "Economically optimize insulation thickness for energy efficiency.",
            "domain": "mechanical",
            "steps": [
                ("Heat Transfer", "heat_transfer_conduction", "Model heat transfer through insulation"),
                ("Cost Analysis", None, "Include insulation, installation, and maintenance costs"),
                ("Energy Savings", None, "Calculate annual energy savings vs insulation thickness"),
                ("Payback Period", None, "Find thickness that gives minimum owner cost"),
                ("Maintenance", None, "Account for replacement/repairs over service life"),
                ("Final Selection", None, "Select optimal thickness plus code minimum requirement")
            ],
            "inputs": ["thermal_conductivity_w_m_k", "surface_area_m2", "inside_temp_c", "outside_temp_c", "operating_hours_per_year"],
            "outputs": ["optimal_thickness_mm", "annual_energy_mwh", "total_owner_cost", "payback_years", "co2_savings_kg_per_year"]
        },
        {
            "id": "mechanical_noise_control",
            "title": "Mechanical System Noise Control",
            "description": "Design noise reduction for HVAC and equipment noise.",
            "domain": "mechanical",
            "steps": [
                ("Source Analysis", None, "Identify noise sources (fans, compressors, flow)"),
                ("Propagation", None, "Determine transmission paths and breakout walls"),
                ("Receptor", None, "Define target noise levels from code/design"),
                ("Attenuators", None, "Size silencers, duct liners, and enclosures"),
                ("Isolation", None, "Use vibration isolators to decouple from structure"),
                ("Verification", None, "Plan field noise testing and remedial measures")
            ],
            "inputs": ["source_sound_level_db", "source_frequency_hz", "distance_to_receiver_m", "target_level_db"],
            "outputs": ["sound_reduction_db", "attenuation_device_type", "lining_thickness_mm", "enclosure_cost"]
        },
        {
            "id": "mechanical_seismic_bracing",
            "title": "Seismic Bracing & Restraint Design",
            "description": "Design seismic restraint for mechanical equipment.",
            "domain": "mechanical",
            "steps": [
                ("Seismic Zone", None, "Determine seismic design category from location"),
                ("Acceleration", None, "Obtain design spectral acceleration"),
                ("Equipment Mass", None, "Locate center of gravity and mass distribution"),
                ("Restraint Force", None, "Calculate lateral and vertical restraint loads"),
                ("Attachment", None, "Specify bolting and bracing to structure"),
                ("Certification", None, "Verify brace adequacy and provide calculations")
            ],
            "inputs": ["equipment_mass_kg", "seismic_zone", "spectral_accel_g", "attachment_height_m", "damping_ratio"],
            "outputs": ["restraint_force_kn", "bolt_size_and_quantity", "brace_sizing_mm", "acceptability_check"]
        },
        {
            "id": "mechanical_blower_selection",
            "title": "Industrial Blower & Fan Selection",
            "description": "Select appropriate blower/fan for process air delivery.",
            "domain": "mechanical",
            "steps": [
                ("Airflow Requirement", "continuity_flow", "Determine operating point (CFM vs pressure)"),
                ("Pressure vs Flow", "darcy_weisbach", "Map system resistance curve"),
                ("Fan Curve", None, "Overlay fan performance curves"),
                ("Selection", "fan_power", "Choose fan at operating point with margin"),
                ("Power", None, "Calculate required motor power with VFD if applicable"),
                ("Sound Level", None, "Verify sound output acceptable for application")
            ],
            "inputs": ["required_cfm", "static_pressure_pa", "temperature_c", "humidity_pct", "motor_type"],
            "outputs": ["fan_model", "motor_power_kw", "noise_level_db", "operating_point", "cost"]
        },
    ],
    "civil": [
        {
            "id": "civil_building_frame_design",
            "title": "Building Structural Frame Design",
            "description": "Analyze and design complete building structure.",
            "domain": "civil",
            "steps": [
                ("Load Analysis", "axial_stress", "Gather dead, live, environmental loads"),
                ("Lateral Load Path", None, "Determine wind and seismic load distribution"),
                ("Member Selection", None, "Select beam/column sizes using code allowables"),
                ("Deflection Checks", "beam_deflection_ss_udl", "Verify deflections within L/240-L/360"),
                ("Connection Design", None, "Design bolted/welded connections"),
                ("Documentation", None, "Create construction drawings and specifications")
            ],
            "inputs": ["floor_area_m2", "num_stories", "live_load_kpa", "wind_speed_kmh", "seismic_zone"],
            "outputs": ["beam_size", "column_size", "moment_capacity_knm", "max_deflection_mm", "material_tonnes"]
        },
        {
            "id": "civil_foundation_design",
            "title": "Shallow Foundation Design",
            "description": "Design isolated and combined footings for building loads.",
            "domain": "civil",
            "steps": [
                ("Load Transfer", None, "Obtain column loads from structure above"),
                ("Soil Strength", "bearing_pressure", "Use site geotechnical report for bearing capacity"),
                ("Footing Sizing", "terzaghi_bearing_capacity", "Size footing for allowable bearing pressure"),
                ("Settling Analysis", "settlement_elastic", "Calculate immediate and consolidation settlement"),
                ("Rebar Design", "reinforcement_area", "Design bottom and top reinforcement"),
                ("Drainage", None, "Specify drainage and backfill materials")
            ],
            "inputs": ["column_load_kn", "building_weight_kn", "soil_bearing_capacity_kpa", "soil_angle_of_friction", "foundation_depth_m"],
            "outputs": ["footing_length_m", "footing_width_m", "footing_thickness_m", "settlement_mm", "rebar_sizes"]
        },
        {
            "id": "civil_slope_stability",
            "title": "Slope Stability Analysis",
            "description": "Analyze slope safety factors and design stabilization.",
            "domain": "civil",
            "steps": [
                ("Slope Geometry", None, "Survey slope profile and soil layers"),
                ("Soil Properties", None, "Obtain friction angle, cohesion, unit weight"),
                ("Critical Surface", None, "Find minimum factor of safety slope"),
                ("FOS Calculation", None, "Calculate FS using Bishop or Fellenius method"),
                ("Stabilization", "retaining_wall_active_pressure", "Design berms, drains, walls if FOS < target"),
                ("Monitoring", None, "Specify instrumentation for long-term monitoring")
            ],
            "inputs": ["slope_height_m", "slope_angle_degrees", "phi_degrees", "cohesion_kpa", "unit_weight_kn_m3"],
            "outputs": ["factor_of_safety", "critical_circle_depth_m", "stabilization_method", "cost_estimate"]
        },
        {
            "id": "civil_retaining_wall_geotechnical",
            "title": "Retaining Wall Design & Analysis",
            "description": "Design cantilever or gravity retaining walls with stability checks.",
            "domain": "civil",
            "steps": [
                ("Soil Pressure", "retaining_wall_active_pressure", "Calculate active and passive earth pressures"),
                ("Load Cases", None, "Analyze gravity, friction, bearing controls"),
                ("Wall Section", None, "Size concrete wall thickness and key"),
                ("Stability Checks", None, "Verify against sliding, overturning, bearing"),
                ("Drainage Design", None, "Design backfill drainage and weep holes"),
                ("Backfill & Curing", None, "Specify compaction and reinforcement protection")
            ],
            "inputs": ["wall_height_m", "soil_unit_weight_kn_m3", "phi_degrees", "cohesion_kpa", "truck_surcharge_kpa"],
            "outputs": ["wall_thickness_m", "key_depth_m", "fos_sliding", "fos_overturning", "fos_bearing", "rebar_schedule"]
        },
        {
            "id": "civil_beam_analysis",
            "title": "Beam Bending & Shear Analysis",
            "description": "Analyze simply supported or continuous beams.",
            "domain": "civil",
            "steps": [
                ("Loads", None, "Define dead, live, and environmental loads"),
                ("Shear Diagram", "beam_shear_stress", "Calculate and plot shear force along beam"),
                ("Moment Diagram", "beam_bending_stress", "Calculate and plot bending moment along beam"),
                ("Stress", "beam_bending_stress", "Compute maximum bending and shear stresses"),
                ("Deflection", "beam_deflection_ss_udl", "Calculate maximum mid-span deflection"),
                ("Design", None, "Select section that satisfies stress and deflection limits")
            ],
            "inputs": ["span_m", "distributed_load_kn_m", "point_load_kn", "material_fy_mpa"],
            "outputs": ["max_moment_knm", "max_shear_kn", "max_stress_mpa", "max_deflection_mm", "required_section"]
        },
        {
            "id": "civil_concrete_mix_design",
            "title": "Concrete Mix Design & Optimization",
            "description": "Design concrete mixes for strength, durability, and economy.",
            "domain": "civil",
            "steps": [
                ("Strength Requirement", None, "Define 28-day compressive strength target"),
                ("Water-Cement Ratio", None, "Use strength relationship to estimate w/c"),
                ("Slump", None, "Determine workability requirement from placement"),
                ("Durability Class", None, "Select exposure class and cement type"),
                ("Trial Mix", None, "Calculate volumes of cement, aggregate, water"),
                ("Optimization", None, "Adjust w/c and additives for site conditions")
            ],
            "inputs": ["target_fck_mpa", "exposure_class", "slump_mm", "cement_type", "agg_size_max_mm"],
            "outputs": ["cement_kg_per_m3", "water_kg_per_m3", "coarse_agg_kg_per_m3", "fine_agg_kg_per_m3", "admixtures"]
        },
        {
            "id": "civil_reinforcement_design",
            "title": "Reinforced Concrete Member Reinforcement Design",
            "description": "Design rebar placement and quantity for RC sections.",
            "domain": "civil",
            "steps": [
                ("Bending Moment", None, "Obtain design moment from structural analysis"),
                ("Section Properties", None, "Calculate moment of inertia and lever arm"),
                ("Steel Area", None, "Compute required steel area from moment and fy"),
                ("Bar Selection", None, "Choose bar size and spacing to meet area"),
                ("Detailing", None, "Apply ACI/code rules for lap length and spacing"),
                ("Shop Drawings", None, "Create reinforcement placement drawings")
            ],
            "inputs": ["design_moment_knm", "section_depth_mm", "concrete_fck_mpa", "steel_fy_mpa"],
            "outputs": ["steel_area_mm2", "bar_size_mm", "bar_spacing_mm", "lap_length_mm", "rebar_qty_per_m"]
        },
        {
            "id": "civil_seismic_design",
            "title": "Seismic Building Design per Code",
            "description": "Design building structure for seismic loads.",
            "domain": "civil",
            "steps": [
                ("Seismic Zone", None, "Obtain response spectra from site/code"),
                ("Building Period", None, "Estimate fundamental period using height/dimension"),
                ("Spectral Acceleration", None, "Read spectral acceleration at period"),
                ("Seismic Force", None, "Calculate base shear from spectral acceleration"),
                ("Force Distribution", None, "Distribute seismic force by height"),
                ("Moment Frames", None, "Design moment resisting frames with ductility")
            ],
            "inputs": ["building_height_m", "num_stories", "seismic_zone", "soil_class", "importance_factor"],
            "outputs": ["building_period_s", "spectral_accel_g", "base_shear_kn", "ductility_demand", "frame_moment_capacity_knm"]
        },
        {
            "id": "civil_excavation_volumetric",
            "title": "Excavation Volume Estimation",
            "description": "Calculate cut/fill volumes and earth balancing.",
            "domain": "civil",
            "steps": [
                ("Existing Levels", None, "Obtain existing ground surface elevation"),
                ("Design Levels", None, "Define design pad elevation and slopes"),
                ("Section Method", None, "Create cross-sections and measure areas"),
                ("Volumes", None, "Calculate cut and fill from section areas"),
                ("Balancing", None, "Determine if borrow or haul-away needed"),
                ("Equipment", None, "Estimate excavator type and timeline")
            ],
            "inputs": ["site_area_m2", "existing_avg_elev_m", "target_elev_m", "slope_ratio", "soil_cohesion_kpa"],
            "outputs": ["cut_volume_m3", "fill_volume_m3", "net_balance_m3", "excavator_hours", "truck_loads"]
        },
        {
            "id": "civil_pavement_thickness",
            "title": "Flexible Pavement Thickness Design",
            "description": "Design asphalt pavement layer thickness.",
            "domain": "civil",
            "steps": [
                ("Traffic", None, "Calculate design ESALs from daily traffic counts"),
                ("Subgrade", None, "Obtain California Bearing Ratio (CBR) from testing"),
                ("Reliability", None, "Select design reliability (e.g., 90%, 95%)"),
                ("AASHTO", None, "Use AASHTO method to compute structural number SN"),
                ("Layers", "mechanical_moment_of_inertia_rect", "Assign layer coefficients and compute thicknesses"),
                ("Materials", None, "Specify asphalt binder and aggregate requirements")
            ],
            "inputs": ["esal_millions", "cbr_subgrade_pct", "reliability_pct", "design_life_years"],
            "outputs": ["structural_number_sn", "asphalt_thickness_mm", "base_thickness_mm", "subbase_thickness_mm"]
        },
        {
            "id": "civil_stormwater_drainage",
            "title": "Stormwater Drainage System Design",
            "description": "Design complete stormwater collection and conveyance.",
            "domain": "civil",
            "steps": [
                ("Rainfall", None, "Determine design storm (e.g., 10-year, 100-year)"),
                ("Runoff", "manning_flow", "Calculate peak flow using rational method or SCS"),
                ("Inlet Design", None, "Size inlets and grates for carry-over conditions"),
                ("Pipe Sizing", "manning_flow", "Size pipes using Manning equation"),
                ("Energy", None, "Check head loss and outlet protection"),
                ("BMP", None, "Specify detention pond and water quality measures")
            ],
            "inputs": ["catchment_area_ha", "rainfall_intensity_mm_hr", "runoff_coefficient", "storm_duration_min"],
            "outputs": ["peak_flow_m3_s", "pipe_diameter_mm", "velocity_m_s", "detention_pond_volume_m3"]
        },
        {
            "id": "civil_ground_improvement",
            "title": "Ground Improvement Methods Design",
            "description": "Design ground treatment for weak or compressible soils.",
            "domain": "civil",
            "steps": [
                ("Soil Profile", None, "Characterize problematic layer depth and extent"),
                ("Improvement Goal", None, "Set strength or settlement improvement target"),
                ("Method Evaluation", None, "Compare options (grouting, piles, replacement)"),
                ("Design Calculation", "settlement_elastic", "Calculate improved soil properties"),
                ("Construction Method", None, "Specify equipment and quality control"),
                ("Testing", None, "Plan geotechnical monitoring and verification")
            ],
            "inputs": ["soil_type", "weak_layer_depth_m", "weak_layer_thickness_m", "target_settlement_mm"],
            "outputs": ["improvement_method", "material_volume_m3", "construction_cost", "construction_time_days"]
        },
        {
            "id": "civil_prestressed_beam",
            "title": "Prestressed Concrete Beam Design",
            "description": "Design prestressed beams with loss calculations.",
            "domain": "civil",
            "steps": [
                ("Loads & Geometry", None, "Establish beam span and loads"),
                ("Prestress Force", None, "Select initial prestressing force"),
                ("Losses", None, "Calculate immediate and time-dependent losses"),
                ("Stress Check", None, "Verify stresses at prestressing and service stages"),
                ("Strength Design", "beam_bending_stress", "Check ultimate code capacity"),
                ("Strand Pattern", None, "Design strand arrangement and development length")
            ],
            "inputs": ["span_m", "load_kn_m", "concrete_fck_mpa", "strand_size", "tension_pct_fpu"],
            "outputs": ["prestress_force_kn", "eccentricity_mm", "total_losses_kn", "final_stress_mpa", "required_strands"]
        },
    ]
}

# Helper function to ensure calculation_id exists
def ensure_calculation_exists(cur, calc_id):
    """Returns the ID of the calculation, or None if not found."""
    cur.execute("SELECT id FROM calculations WHERE calculation_id = ?", (calc_id,))
    row = cur.fetchone()
    return row[0] if row else None

def seed_workflows():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    try:
        for domain, workflows in WORKFLOW_DEFINITIONS.items():
            print(f"\nSeeding {domain} domain...")
            
            for wf in workflows:
                wf_id = wf['id']
                
                # Check if workflow already exists
                cur.execute("SELECT id FROM workflows WHERE workflow_id = ?", (wf_id,))
                if cur.fetchone():
                    print(f"  {wf_id} already exists, skipping")
                    continue
                
                # Insert workflow
                cur.execute("""
                    INSERT INTO workflows 
                    (workflow_id, title, description, domain, created_at, updated_at, is_active)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                """, (wf_id, wf['title'], wf['description'], domain, datetime.now(), datetime.now()))
                conn.commit()
                workflow_row = cur.lastrowid
                
                # Insert inputs
                for inp in wf['inputs']:
                    cur.execute("""
                        INSERT INTO workflow_inputs (workflow_id, name, type, required, data_type)
                        VALUES (?, ?, 'text', 1, 'number')
                    """, (workflow_row, inp))
                
                # Insert outputs
                for out in wf['outputs']:
                    cur.execute("""
                        INSERT INTO workflow_outputs (workflow_id, name, type, description)
                        VALUES (?, ?, 'number', NULL)
                    """, (workflow_row, out))
                
                # Insert steps
                conn.commit()
                for step_num, (step_name, calc_id, description) in enumerate(wf['steps'], 1):
                    cur.execute("""
                        INSERT INTO workflow_steps (workflow_id, step_number, name, description, calculation_id)
                        VALUES (?, ?, ?, ?, ?)
                    """, (workflow_row, step_num, step_name, description, calc_id))
                
                conn.commit()
                print(f"  ✓ {wf_id}")
        
        print(f"\n✓ Seeding complete!")
        cur.execute("SELECT domain, COUNT(*) FROM workflows GROUP BY domain")
        for domain, count in cur.fetchall():
            print(f"  {domain}: {count} workflows")
    
    finally:
        conn.close()

if __name__ == "__main__":
    seed_workflows()
