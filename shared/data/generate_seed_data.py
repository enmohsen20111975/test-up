import json
import math
from datetime import datetime, timezone

DOMAINS = ["civil", "electrical", "mechanical"]

WORKFLOW_TOPICS = {
    "civil": [
        {
            "id": "earthworks",
            "title": "Earthworks Quantity",
            "description": "Estimate cut and fill volumes for site grading.",
            "inputs": ["surface_data", "design_levels", "bulking_factor", "shrink_factor"],
            "outputs": ["cut_volume", "fill_volume", "net_balance"],
            "steps": ["import_surface", "define_design_levels", "compute_cut_fill", "apply_factors", "summarize_balance"],
        },
        {
            "id": "rebar_takeoff",
            "title": "Rebar Takeoff",
            "description": "Quantify reinforcing steel for RC members.",
            "inputs": ["member_geometry", "bar_sizes", "spacing", "laps"],
            "outputs": ["bar_count", "bar_length", "total_weight"],
            "steps": ["select_members", "assign_bars", "compute_lengths", "apply_laps", "aggregate_weight"],
        },
        {
            "id": "slab_design",
            "title": "Slab Design",
            "description": "Check slab thickness and reinforcement.",
            "inputs": ["span", "loads", "concrete_grade", "steel_grade"],
            "outputs": ["slab_thickness", "reinforcement_area", "deflection_ratio"],
            "steps": ["compute_loads", "select_thickness", "check_deflection", "design_rebar"],
        },
        {
            "id": "column_design",
            "title": "Column Design",
            "description": "Design RC column for axial and bending actions.",
            "inputs": ["axial_load", "moment", "section_dims", "material_strengths"],
            "outputs": ["rebar_ratio", "bar_layout", "utilization"],
            "steps": ["select_section", "check_interaction", "size_rebar", "verify_details"],
        },
        {
            "id": "footing_sizing",
            "title": "Footing Sizing",
            "description": "Size isolated footing for bearing and punching.",
            "inputs": ["column_load", "soil_bearing", "depth_limits"],
            "outputs": ["footing_area", "thickness", "soil_pressure"],
            "steps": ["compute_area", "check_bearing", "check_punching", "design_rebar"],
        },
        {
            "id": "retaining_wall",
            "title": "Retaining Wall Stability",
            "description": "Check sliding, overturning, and bearing stability.",
            "inputs": ["wall_geometry", "soil_properties", "surcharge", "water_table"],
            "outputs": ["safety_factors", "base_pressure", "stability_ok"],
            "steps": ["compute_earth_pressure", "check_sliding", "check_overturning", "check_bearing"],
        },
        {
            "id": "pavement_design",
            "title": "Pavement Design",
            "description": "Determine pavement layer thicknesses.",
            "inputs": ["traffic_esal", "subgrade_cbr", "material_coeffs"],
            "outputs": ["layer_thicknesses", "design_life"],
            "steps": ["compute_structural_number", "select_layers", "verify_life"],
        },
        {
            "id": "concrete_mix",
            "title": "Concrete Mix Estimation",
            "description": "Estimate concrete mix proportions.",
            "inputs": ["target_strength", "slump", "aggregate_sizes", "cement_type"],
            "outputs": ["cement_qty", "water_qty", "aggregate_qty"],
            "steps": ["select_w_c_ratio", "estimate_water", "compute_cement", "compute_aggregates"],
        },
        {
            "id": "drainage_design",
            "title": "Drainage Design",
            "description": "Size stormwater network and culverts.",
            "inputs": ["catchment_area", "rainfall_intensity", "runoff_coeff"],
            "outputs": ["peak_flow", "pipe_size", "culvert_size"],
            "steps": ["compute_peak_flow", "select_pipes", "check_capacity"],
        },
        {
            "id": "survey_control",
            "title": "Survey Control",
            "description": "Set up survey control network and closures.",
            "inputs": ["station_coords", "angles", "distances"],
            "outputs": ["adjusted_coords", "closure_error"],
            "steps": ["compute_traverse", "adjust_closure", "report_control"],
        },
    ],
    "electrical": [
        {
            "id": "load_calc",
            "title": "Electrical Load Calculation",
            "description": "Calculate connected and demand loads.",
            "inputs": ["load_schedule", "demand_factors", "diversity_factors"],
            "outputs": ["connected_load", "demand_load", "service_size"],
            "steps": ["sum_connected", "apply_demand", "apply_diversity", "select_service"],
        },
        {
            "id": "panel_schedule",
            "title": "Panel Schedule",
            "description": "Build panel schedules with phase balancing.",
            "inputs": ["circuits", "phase_config", "breaker_sizes"],
            "outputs": ["phase_balance", "panel_loads"],
            "steps": ["assign_circuits", "balance_phases", "check_breakers"],
        },
        {
            "id": "cable_sizing",
            "title": "Cable Sizing",
            "description": "Select cable size for ampacity and voltage drop.",
            "inputs": ["load_current", "length", "installation_method", "ambient_temp"],
            "outputs": ["cable_size", "voltage_drop", "ampacity_ok"],
            "steps": ["compute_current", "select_cable", "check_drop", "apply_corrections"],
        },
        {
            "id": "short_circuit",
            "title": "Short Circuit Calculation",
            "description": "Estimate fault current at buses.",
            "inputs": ["source_impedance", "transformer_data", "cable_impedance"],
            "outputs": ["fault_current", "interrupting_rating"],
            "steps": ["build_impedance", "compute_fault", "select_breaker"],
        },
        {
            "id": "lighting_layout",
            "title": "Lighting Layout",
            "description": "Determine fixture count and spacing.",
            "inputs": ["area", "target_lux", "fixture_lumens", "utilization_factor"],
            "outputs": ["fixture_count", "spacing"],
            "steps": ["compute_total_lumens", "select_fixtures", "layout_spacing"],
        },
        {
            "id": "grounding",
            "title": "Grounding and Earthing",
            "description": "Size grounding conductors and check resistance.",
            "inputs": ["fault_current", "soil_resistivity", "electrode_type"],
            "outputs": ["ground_conductor_size", "estimated_resistance"],
            "steps": ["size_conductor", "estimate_resistance", "verify_limits"],
        },
        {
            "id": "transformer_sizing",
            "title": "Transformer Sizing",
            "description": "Select transformer rating and loading.",
            "inputs": ["demand_load", "voltage_level", "power_factor"],
            "outputs": ["transformer_kva", "loading_pct"],
            "steps": ["compute_kva", "select_standard", "check_loading"],
        },
        {
            "id": "solar_pv",
            "title": "Solar PV Sizing",
            "description": "Estimate PV and inverter size.",
            "inputs": ["energy_demand", "solar_irradiance", "system_losses"],
            "outputs": ["pv_kwp", "inverter_kw"],
            "steps": ["compute_daily_kwh", "select_pv_size", "select_inverter"],
        },
        {
            "id": "motor_starting",
            "title": "Motor Starting",
            "description": "Check starting current and voltage dip.",
            "inputs": ["motor_kw", "starting_method", "source_impedance"],
            "outputs": ["starting_current", "voltage_dip"],
            "steps": ["estimate_start_current", "compute_dip", "verify_limits"],
        },
        {
            "id": "harmonics",
            "title": "Harmonics Assessment",
            "description": "Estimate harmonic distortion and filter needs.",
            "inputs": ["load_profile", "nonlinear_loads", "system_impedance"],
            "outputs": ["thd", "filter_size"],
            "steps": ["estimate_thd", "check_limits", "size_filter"],
        },
    ],
    "mechanical": [
        {
            "id": "hvac_load",
            "title": "HVAC Load Calculation",
            "description": "Estimate cooling and heating loads.",
            "inputs": ["zone_area", "occupancy", "envelope_data", "weather_data"],
            "outputs": ["cooling_load", "heating_load"],
            "steps": ["compute_sensible", "compute_latent", "sum_loads"],
        },
        {
            "id": "duct_sizing",
            "title": "Duct Sizing",
            "description": "Size ducts for airflow and pressure limits.",
            "inputs": ["airflow", "velocity_limit", "duct_material"],
            "outputs": ["duct_dimensions", "pressure_drop"],
            "steps": ["select_velocity", "compute_area", "pick_dimensions", "check_pressure"],
        },
        {
            "id": "pump_sizing",
            "title": "Pump Sizing",
            "description": "Select pump based on flow and head.",
            "inputs": ["flow_rate", "total_head", "efficiency"],
            "outputs": ["pump_power", "pump_model"],
            "steps": ["compute_head", "compute_power", "select_pump"],
        },
        {
            "id": "pipe_sizing",
            "title": "Pipe Sizing",
            "description": "Size pipes for flow and pressure constraints.",
            "inputs": ["flow_rate", "velocity_limit", "fluid_properties"],
            "outputs": ["pipe_diameter", "pressure_drop"],
            "steps": ["select_velocity", "compute_diameter", "check_pressure"],
        },
        {
            "id": "pressure_drop",
            "title": "Pressure Drop",
            "description": "Calculate system pressure losses.",
            "inputs": ["pipe_lengths", "fittings", "flow_rate", "fluid_properties"],
            "outputs": ["pressure_drop_total"],
            "steps": ["compute_major_losses", "compute_minor_losses", "sum_losses"],
        },
        {
            "id": "chiller_selection",
            "title": "Chiller Selection",
            "description": "Select chiller capacity for cooling load.",
            "inputs": ["cooling_load", "delta_t", "efficiency"],
            "outputs": ["chiller_tons", "chiller_model"],
            "steps": ["compute_tons", "select_standard", "check_loading"],
        },
        {
            "id": "boiler_sizing",
            "title": "Boiler Sizing",
            "description": "Size boiler capacity for heating load.",
            "inputs": ["heating_load", "efficiency", "fuel_type"],
            "outputs": ["boiler_capacity", "boiler_model"],
            "steps": ["compute_capacity", "select_standard", "check_efficiency"],
        },
        {
            "id": "compressor_selection",
            "title": "Compressor Selection",
            "description": "Estimate compressor power and sizing.",
            "inputs": ["flow_rate", "pressure_ratio", "gas_properties"],
            "outputs": ["compressor_power", "compressor_model"],
            "steps": ["estimate_power", "select_compressor", "check_efficiency"],
        },
        {
            "id": "heat_exchanger",
            "title": "Heat Exchanger",
            "description": "Estimate heat exchanger area.",
            "inputs": ["heat_duty", "lmtd", "overall_u"],
            "outputs": ["exchanger_area"],
            "steps": ["compute_lmtd", "compute_area", "select_exchanger"],
        },
        {
            "id": "air_compressor",
            "title": "Compressed Air Sizing",
            "description": "Size air compressor and receiver.",
            "inputs": ["air_demand", "pressure", "duty_cycle"],
            "outputs": ["compressor_kw", "receiver_volume"],
            "steps": ["compute_flow", "size_receiver", "select_unit"],
        },
    ],
}

CALC_TEMPLATES = [
    {
        "domain": "civil",
        "name": "Bending stress",
        "equation": "sigma = M * c / I",
        "variables": [
            {"name": "bending_moment", "symbol": "M", "unit": "N*m", "description": "Applied bending moment"},
            {"name": "distance_to_extreme_fiber", "symbol": "c", "unit": "m", "description": "Distance from neutral axis"},
            {"name": "second_moment_of_area", "symbol": "I", "unit": "m^4", "description": "Section second moment"},
            {"name": "bending_stress", "symbol": "sigma", "unit": "Pa", "description": "Extreme fiber stress"},
        ],
    },
    {
        "domain": "civil",
        "name": "Deflection for simply supported beam (UDL)",
        "equation": "delta_max = 5 * w * L^4 / (384 * E * I)",
        "variables": [
            {"name": "uniform_load", "symbol": "w", "unit": "N/m", "description": "Uniformly distributed load"},
            {"name": "span", "symbol": "L", "unit": "m", "description": "Span length"},
            {"name": "elastic_modulus", "symbol": "E", "unit": "Pa", "description": "Elastic modulus"},
            {"name": "second_moment_of_area", "symbol": "I", "unit": "m^4", "description": "Section second moment"},
            {"name": "deflection", "symbol": "delta_max", "unit": "m", "description": "Maximum deflection"},
        ],
    },
    {
        "domain": "civil",
        "name": "Axial stress",
        "equation": "sigma = P / A",
        "variables": [
            {"name": "axial_load", "symbol": "P", "unit": "N", "description": "Axial load"},
            {"name": "area", "symbol": "A", "unit": "m^2", "description": "Cross-sectional area"},
            {"name": "axial_stress", "symbol": "sigma", "unit": "Pa", "description": "Axial stress"},
        ],
    },
    {
        "domain": "civil",
        "name": "Bearing pressure",
        "equation": "q = P / A",
        "variables": [
            {"name": "load", "symbol": "P", "unit": "N", "description": "Applied load"},
            {"name": "area", "symbol": "A", "unit": "m^2", "description": "Footing area"},
            {"name": "bearing_pressure", "symbol": "q", "unit": "Pa", "description": "Average pressure"},
        ],
    },
    {
        "domain": "civil",
        "name": "Manning equation",
        "equation": "Q = (1 / n) * A * R^(2/3) * S^(1/2)",
        "variables": [
            {"name": "flow_rate", "symbol": "Q", "unit": "m^3/s", "description": "Discharge"},
            {"name": "roughness", "symbol": "n", "unit": "-", "description": "Manning roughness"},
            {"name": "area", "symbol": "A", "unit": "m^2", "description": "Flow area"},
            {"name": "hydraulic_radius", "symbol": "R", "unit": "m", "description": "Hydraulic radius"},
            {"name": "slope", "symbol": "S", "unit": "-", "description": "Energy slope"},
        ],
    },
    {
        "domain": "electrical",
        "name": "Ohm's law",
        "equation": "V = I * R",
        "variables": [
            {"name": "voltage", "symbol": "V", "unit": "V", "description": "Voltage"},
            {"name": "current", "symbol": "I", "unit": "A", "description": "Current"},
            {"name": "resistance", "symbol": "R", "unit": "ohm", "description": "Resistance"},
        ],
    },
    {
        "domain": "electrical",
        "name": "Electric power (DC)",
        "equation": "P = V * I",
        "variables": [
            {"name": "power", "symbol": "P", "unit": "W", "description": "Power"},
            {"name": "voltage", "symbol": "V", "unit": "V", "description": "Voltage"},
            {"name": "current", "symbol": "I", "unit": "A", "description": "Current"},
        ],
    },
    {
        "domain": "electrical",
        "name": "Three-phase power",
        "equation": "P = sqrt(3) * V_line * I_line * pf",
        "variables": [
            {"name": "power", "symbol": "P", "unit": "W", "description": "Power"},
            {"name": "line_voltage", "symbol": "V_line", "unit": "V", "description": "Line voltage"},
            {"name": "line_current", "symbol": "I_line", "unit": "A", "description": "Line current"},
            {"name": "power_factor", "symbol": "pf", "unit": "-", "description": "Power factor"},
        ],
    },
    {
        "domain": "electrical",
        "name": "Voltage drop (3-phase)",
        "equation": "Vd = sqrt(3) * I * (R * cos_phi + X * sin_phi) * L",
        "variables": [
            {"name": "voltage_drop", "symbol": "Vd", "unit": "V", "description": "Voltage drop"},
            {"name": "current", "symbol": "I", "unit": "A", "description": "Line current"},
            {"name": "resistance_per_length", "symbol": "R", "unit": "ohm/m", "description": "Resistance per length"},
            {"name": "reactance_per_length", "symbol": "X", "unit": "ohm/m", "description": "Reactance per length"},
            {"name": "line_length", "symbol": "L", "unit": "m", "description": "Line length"},
            {"name": "power_factor_angle", "symbol": "phi", "unit": "rad", "description": "Power factor angle"},
        ],
    },
    {
        "domain": "electrical",
        "name": "Ground rod resistance",
        "equation": "Rg = (rho / (2 * pi * L)) * (ln(4 * L / d) - 1)",
        "variables": [
            {"name": "soil_resistivity", "symbol": "rho", "unit": "ohm*m", "description": "Soil resistivity"},
            {"name": "rod_length", "symbol": "L", "unit": "m", "description": "Rod length"},
            {"name": "rod_diameter", "symbol": "d", "unit": "m", "description": "Rod diameter"},
            {"name": "ground_resistance", "symbol": "Rg", "unit": "ohm", "description": "Grounding resistance"},
        ],
    },
    {
        "domain": "mechanical",
        "name": "Reynolds number",
        "equation": "Re = (rho * v * D) / mu",
        "variables": [
            {"name": "reynolds_number", "symbol": "Re", "unit": "-", "description": "Flow regime indicator"},
            {"name": "density", "symbol": "rho", "unit": "kg/m^3", "description": "Fluid density"},
            {"name": "velocity", "symbol": "v", "unit": "m/s", "description": "Flow velocity"},
            {"name": "diameter", "symbol": "D", "unit": "m", "description": "Hydraulic diameter"},
            {"name": "dynamic_viscosity", "symbol": "mu", "unit": "Pa*s", "description": "Dynamic viscosity"},
        ],
    },
    {
        "domain": "mechanical",
        "name": "Darcy-Weisbach head loss",
        "equation": "hf = f * (L/D) * (v^2 / (2 * g))",
        "variables": [
            {"name": "head_loss", "symbol": "hf", "unit": "m", "description": "Head loss"},
            {"name": "friction_factor", "symbol": "f", "unit": "-", "description": "Friction factor"},
            {"name": "length", "symbol": "L", "unit": "m", "description": "Pipe length"},
            {"name": "diameter", "symbol": "D", "unit": "m", "description": "Pipe diameter"},
            {"name": "velocity", "symbol": "v", "unit": "m/s", "description": "Flow velocity"},
            {"name": "gravity", "symbol": "g", "unit": "m/s^2", "description": "Gravity"},
        ],
    },
    {
        "domain": "mechanical",
        "name": "Pump power",
        "equation": "P = (rho * g * Q * H) / eta",
        "variables": [
            {"name": "power", "symbol": "P", "unit": "W", "description": "Pump power"},
            {"name": "density", "symbol": "rho", "unit": "kg/m^3", "description": "Fluid density"},
            {"name": "gravity", "symbol": "g", "unit": "m/s^2", "description": "Gravity"},
            {"name": "flow_rate", "symbol": "Q", "unit": "m^3/s", "description": "Flow rate"},
            {"name": "head", "symbol": "H", "unit": "m", "description": "Total head"},
            {"name": "efficiency", "symbol": "eta", "unit": "-", "description": "Pump efficiency"},
        ],
    },
    {
        "domain": "mechanical",
        "name": "Heat transfer by conduction",
        "equation": "Q = k * A * (T1 - T2) / L",
        "variables": [
            {"name": "heat_flow", "symbol": "Q", "unit": "W", "description": "Heat flow"},
            {"name": "thermal_conductivity", "symbol": "k", "unit": "W/m*K", "description": "Thermal conductivity"},
            {"name": "area", "symbol": "A", "unit": "m^2", "description": "Area"},
            {"name": "temperature_hot", "symbol": "T1", "unit": "K", "description": "Hot side temperature"},
            {"name": "temperature_cold", "symbol": "T2", "unit": "K", "description": "Cold side temperature"},
            {"name": "thickness", "symbol": "L", "unit": "m", "description": "Thickness"},
        ],
    },
    {
        "domain": "mechanical",
        "name": "Continuity equation",
        "equation": "Q = A * v",
        "variables": [
            {"name": "flow_rate", "symbol": "Q", "unit": "m^3/s", "description": "Flow rate"},
            {"name": "area", "symbol": "A", "unit": "m^2", "description": "Flow area"},
            {"name": "velocity", "symbol": "v", "unit": "m/s", "description": "Flow velocity"},
        ],
    },
]

EXAMPLE_TEMPLATES = {
    "civil": [
        {
            "id": "beam_deflection",
            "title": "Simply supported beam deflection",
            "scenario": "A simply supported beam carries a uniform load.",
            "units": {"w": "N/m", "L": "m", "E": "Pa", "I": "m^4", "delta_max": "m"},
            "compute": lambda v: 5 * v["w"] * v["L"] ** 4 / (384 * v["E"] * v["I"]),
            "inputs": lambda s: {"w": 9000 + s * 120, "L": 5 + 0.1 * s, "E": 25e9, "I": 0.00028 + 1e-6 * s},
            "output_key": "delta_max",
        },
        {
            "id": "bearing_pressure",
            "title": "Footing bearing pressure",
            "scenario": "A column load is supported by a square footing.",
            "units": {"P": "N", "A": "m^2", "q": "Pa"},
            "compute": lambda v: v["P"] / v["A"],
            "inputs": lambda s: {"P": 1.2e6 + s * 15000, "A": 6 + 0.05 * s},
            "output_key": "q",
        },
        {
            "id": "manning_flow",
            "title": "Open channel flow",
            "scenario": "A trapezoidal channel conveys stormwater.",
            "units": {"n": "-", "A": "m^2", "R": "m", "S": "-", "Q": "m^3/s"},
            "compute": lambda v: (1 / v["n"]) * v["A"] * (v["R"] ** (2 / 3)) * (v["S"] ** 0.5),
            "inputs": lambda s: {"n": 0.015, "A": 3.8 + 0.03 * s, "R": 0.7 + 0.005 * s, "S": 0.001},
            "output_key": "Q",
        },
        {
            "id": "axial_stress",
            "title": "Axial stress",
            "scenario": "A column carries axial load only.",
            "units": {"P": "N", "A": "m^2", "sigma": "Pa"},
            "compute": lambda v: v["P"] / v["A"],
            "inputs": lambda s: {"P": 1.0e6 + s * 12000, "A": 0.3 + 0.002 * s},
            "output_key": "sigma",
        },
        {
            "id": "retaining_wall",
            "title": "Retaining wall active pressure",
            "scenario": "A retaining wall with dry backfill.",
            "units": {"Ka": "-", "gamma": "N/m^3", "H": "m", "Pa": "N/m"},
            "compute": lambda v: 0.5 * v["Ka"] * v["gamma"] * v["H"] ** 2,
            "inputs": lambda s: {"Ka": 0.33, "gamma": 18000, "H": 4 + 0.05 * s},
            "output_key": "Pa",
        },
    ],
    "electrical": [
        {
            "id": "ohms_law",
            "title": "Ohm's law",
            "scenario": "A resistive load on a DC circuit.",
            "units": {"I": "A", "R": "ohm", "V": "V"},
            "compute": lambda v: v["I"] * v["R"],
            "inputs": lambda s: {"I": 8 + 0.2 * s, "R": 12 + 0.1 * s},
            "output_key": "V",
        },
        {
            "id": "power_dc",
            "title": "Electric power (DC)",
            "scenario": "DC load power calculation.",
            "units": {"V": "V", "I": "A", "P": "W"},
            "compute": lambda v: v["V"] * v["I"],
            "inputs": lambda s: {"V": 120 + s, "I": 10 + 0.1 * s},
            "output_key": "P",
        },
        {
            "id": "power_3ph",
            "title": "Three-phase power",
            "scenario": "Three-phase feeder with given power factor.",
            "units": {"V_line": "V", "I_line": "A", "pf": "-", "P": "W"},
            "compute": lambda v: math.sqrt(3) * v["V_line"] * v["I_line"] * v["pf"],
            "inputs": lambda s: {"V_line": 400, "I_line": 50 + s, "pf": 0.85},
            "output_key": "P",
        },
        {
            "id": "voltage_drop_3ph",
            "title": "Three-phase voltage drop",
            "scenario": "Feeder voltage drop for a balanced load.",
            "units": {"I": "A", "R": "ohm/m", "X": "ohm/m", "L": "m", "phi": "rad", "Vd": "V"},
            "compute": lambda v: math.sqrt(3) * v["I"] * (v["R"] * math.cos(v["phi"]) + v["X"] * math.sin(v["phi"])) * v["L"],
            "inputs": lambda s: {"I": 80 + s, "R": 0.0003, "X": 0.00008, "L": 40 + s, "phi": 0.5},
            "output_key": "Vd",
        },
        {
            "id": "ground_rod",
            "title": "Ground rod resistance",
            "scenario": "Single rod in uniform soil.",
            "units": {"rho": "ohm*m", "L": "m", "d": "m", "Rg": "ohm"},
            "compute": lambda v: (v["rho"] / (2 * math.pi * v["L"])) * (math.log(4 * v["L"] / v["d"]) - 1),
            "inputs": lambda s: {"rho": 80 + s, "L": 3 + 0.02 * s, "d": 0.016},
            "output_key": "Rg",
        },
    ],
    "mechanical": [
        {
            "id": "reynolds",
            "title": "Reynolds number",
            "scenario": "Flow in a circular pipe.",
            "units": {"rho": "kg/m^3", "v": "m/s", "D": "m", "mu": "Pa*s", "Re": "-"},
            "compute": lambda v: (v["rho"] * v["v"] * v["D"]) / v["mu"],
            "inputs": lambda s: {"rho": 998, "v": 1.2 + 0.02 * s, "D": 0.04 + 0.0005 * s, "mu": 0.001},
            "output_key": "Re",
        },
        {
            "id": "darcy_weisbach",
            "title": "Darcy-Weisbach head loss",
            "scenario": "Head loss in a straight pipe.",
            "units": {"f": "-", "L": "m", "D": "m", "v": "m/s", "g": "m/s^2", "hf": "m"},
            "compute": lambda v: v["f"] * (v["L"] / v["D"]) * (v["v"] ** 2 / (2 * v["g"])),
            "inputs": lambda s: {"f": 0.02, "L": 80 + s, "D": 0.15, "v": 1.8, "g": 9.81},
            "output_key": "hf",
        },
        {
            "id": "pump_power",
            "title": "Pump power",
            "scenario": "Pump against a given head.",
            "units": {"rho": "kg/m^3", "g": "m/s^2", "Q": "m^3/s", "H": "m", "eta": "-", "P": "W"},
            "compute": lambda v: (v["rho"] * v["g"] * v["Q"] * v["H"]) / v["eta"],
            "inputs": lambda s: {"rho": 1000, "g": 9.81, "Q": 0.04 + 0.0005 * s, "H": 20 + 0.2 * s, "eta": 0.72},
            "output_key": "P",
        },
        {
            "id": "heat_conduction",
            "title": "Heat transfer by conduction",
            "scenario": "Heat loss through a wall.",
            "units": {"k": "W/m*K", "A": "m^2", "T1": "K", "T2": "K", "L": "m", "Q": "W"},
            "compute": lambda v: v["k"] * v["A"] * (v["T1"] - v["T2"]) / v["L"],
            "inputs": lambda s: {"k": 1.1, "A": 10 + 0.1 * s, "T1": 303, "T2": 283, "L": 0.2},
            "output_key": "Q",
        },
        {
            "id": "continuity",
            "title": "Continuity equation",
            "scenario": "Flow rate from area and velocity.",
            "units": {"A": "m^2", "v": "m/s", "Q": "m^3/s"},
            "compute": lambda v: v["A"] * v["v"],
            "inputs": lambda s: {"A": 0.25 + 0.002 * s, "v": 2.5 + 0.02 * s},
            "output_key": "Q",
        },
    ],
}


def build_workflows(target_count):
    workflows = []
    variant = 1
    while len(workflows) < target_count:
        for domain in DOMAINS:
            for topic in WORKFLOW_TOPICS[domain]:
                entry = {
                    "id": f"{domain}_{topic['id']}_{variant}",
                    "domain": domain,
                    "title": f"{topic['title']} v{variant}",
                    "description": f"{topic['description']} Variant {variant}.",
                    "inputs": topic["inputs"],
                    "outputs": topic["outputs"],
                    "steps": topic["steps"],
                }
                workflows.append(entry)
                if len(workflows) >= target_count:
                    return workflows
        variant += 1
    return workflows


def build_calculations(target_count):
    calculations = []
    idx = 1
    while len(calculations) < target_count:
        for base in CALC_TEMPLATES:
            entry = {
                "id": f"{base['domain']}_{base['name'].lower().replace(' ', '_').replace('(', '').replace(')', '').replace("'", '')}_{idx}",
                "domain": base["domain"],
                "name": f"{base['name']} case {idx}",
                "equation": base["equation"],
                "variables": base["variables"],
            }
            calculations.append(entry)
            if len(calculations) >= target_count:
                return calculations
        idx += 1
    return calculations


def build_examples(target_count):
    examples = []
    per_domain = target_count // len(DOMAINS)
    for domain in DOMAINS:
        templates = EXAMPLE_TEMPLATES[domain]
        for i in range(per_domain):
            template = templates[i % len(templates)]
            step = i % 40
            inputs = template["inputs"](step)
            output_value = template["compute"](inputs)
            outputs = {template["output_key"]: round(output_value, 4) if isinstance(output_value, float) else output_value}
            entry = {
                "id": f"{domain}_{template['id']}_{i + 1}",
                "domain": domain,
                "title": f"{template['title']} #{i + 1}",
                "scenario": f"{template['scenario']} Example {i + 1}.",
                "inputs": inputs,
                "outputs": outputs,
                "units": template["units"],
            }
            examples.append(entry)

    while len(examples) < target_count:
        examples.append(examples[len(examples) % len(examples)].copy())
    return examples[:target_count]


def main():
    workflows = build_workflows(800)
    calculations = build_calculations(2000)
    examples = build_examples(1200)

    metadata = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "version": "1.2",
    }

    with open("workflows.json", "w", encoding="utf-8") as f:
        json.dump({**metadata, "domains": DOMAINS, "workflows": workflows}, f, indent=2, ensure_ascii=True)

    with open("calculations.json", "w", encoding="utf-8") as f:
        json.dump({**metadata, "calculations": calculations}, f, indent=2, ensure_ascii=True)

    with open("examples.json", "w", encoding="utf-8") as f:
        json.dump({**metadata, "examples": examples}, f, indent=2, ensure_ascii=True)


if __name__ == "__main__":
    main()
