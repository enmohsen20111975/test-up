class MechanicalCalculators:
    @staticmethod
    def hvac_load(area: float, height: float, occupants: int, climate: str):
        """Calculate HVAC load based on area, height, occupants, and climate"""
        try:
            volume = area * height
            climate_factors = {
                'hot': {'sensible': 60, 'name': 'Hot & Humid'},
                'cold': {'sensible': 30, 'name': 'Cold'},
                'moderate': {'sensible': 45, 'name': 'Moderate'}
            }
            
            climate_data = climate_factors.get(climate, climate_factors['moderate'])
            envelope_load = volume * climate_data['sensible']
            occupant_load = occupants * 130
            total_heat_gain = envelope_load + occupant_load
            cooling_kw = total_heat_gain / 1000
            cooling_tr = cooling_kw / 3.517
            cooling_btu = cooling_kw * 3412
            
            results = {
                "room_volume": round(volume, 2),
                "climate_zone": climate_data['name'],
                "envelope_load": round(envelope_load / 1000, 2),
                "occupant_load": round(occupant_load / 1000, 2),
                "total_cooling_load": round(cooling_kw, 2),
                "cooling_capacity_tr": round(cooling_tr, 2),
                "cooling_capacity_btu": round(cooling_btu / 1000, 1),
                "recommended_ac_size": int(__import__('math').ceil(cooling_tr * 1.2))
            }
            
            compliance = "ASHRAE Fundamentals"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def pump_sizing(flow_rate: float, head: float, efficiency: float, speed: float = 1450):
        """Calculate pump sizing with efficiency and speed"""
        try:
            eff_decimal = efficiency / 100
            hydraulic_power = (1000 * 9.81 * flow_rate * head) / 3600000
            shaft_power = hydraulic_power / eff_decimal
            motor_power = shaft_power * 1.15
            recommended_motor = __import__('math').ceil(motor_power * 2) / 2
            
            omega = (2 * __import__('math').pi * speed) / 60
            torque = shaft_power / omega
            specific_speed = (speed * __import__('math').sqrt(flow_rate)) / __import__('math').pow(head, 0.75)
            
            if specific_speed < 20:
                pump_type = 'Centrifugal (Radial)'
            elif specific_speed < 80:
                pump_type = 'Mixed Flow'
            else:
                pump_type = 'Axial Flow'
            
            results = {
                "flow_rate": round(flow_rate, 2),
                "total_head": round(head, 2),
                "pump_efficiency": efficiency,
                "hydraulic_power": round(hydraulic_power, 2),
                "shaft_power": round(shaft_power, 2),
                "motor_power": round(motor_power, 2),
                "recommended_motor": recommended_motor,
                "torque": round(torque, 4),
                "speed": speed,
                "specific_speed": round(specific_speed, 1),
                "pump_type": pump_type
            }
            
            compliance = "ISO 9906:2012"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def pipe_sizing(flow_rate: float, velocity: float = 2, schedule: str = 'schedule40'):
        """Calculate pipe sizing"""
        try:
            flow_rate_m3s = flow_rate / 3600
            required_area = (flow_rate_m3s / velocity) * 1e6
            calculated_diameter = __import__('math').sqrt((4 * required_area) / __import__('math').pi)
            
            standard_sizes = [15, 20, 25, 32, 40, 50, 65, 80, 100, 125, 150, 200, 250, 300]
            selected_size = next((size for size in standard_sizes if size >= calculated_diameter), 300)
            
            actual_area = (__import__('math').pi * (selected_size / 1000) ** 2) / 4
            actual_velocity = flow_rate_m3s / actual_area
            
            results = {
                "calculated_diameter": round(calculated_diameter, 2),
                "standard_size": selected_size,
                "flow_rate": round(flow_rate, 2),
                "actual_velocity": round(actual_velocity, 2)
            }
            
            compliance = "ASME B36.10M"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def pipe_friction(flow_rate: float, pipe_size: float, pipe_length: float, temperature: float = 20, roughness: str = 'steel_new', schedule: str = 'schedule40'):
        """Calculate pipe friction using Darcy-Weisbach equation"""
        try:
            flow_rate_m3s = flow_rate / 3600
            g = 9.81
            diameter = pipe_size / 1000
            L = pipe_length
            
            area = (__import__('math').pi * diameter ** 2) / 4
            velocity = flow_rate_m3s / area
            
            nu = 1.004e-6 if temperature == 20 else 0.653e-6 if temperature == 40 else 1.004e-6
            rho = 1000
            Re = (velocity * diameter) / nu
            
            pipe_roughness = {
                'steel_new': 0.045,
                'steel_old': 0.2,
                'copper': 0.0015,
                'pvc': 0.0015,
                'cast_iron': 0.26
            }
            
            epsilon = pipe_roughness.get(roughness, 0.045)
            relative_roughness = epsilon / (pipe_size)
            
            if Re < 2300:
                f = 64 / Re
            else:
                f = __import__('math').pow(-1.8 * __import__('math').log10(__import__('math').pow(relative_roughness / 3.7, 1.1) + 6.9 / Re), -2)
                for i in range(3):
                    f = __import__('math').pow(-2 * __import__('math').log10(relative_roughness / 3.7 + 2.51 / (Re * __import__('math').sqrt(f))), -2)
            
            head_loss = f * (L / diameter) * (velocity ** 2 / (2 * g))
            pressure_drop = rho * g * head_loss / 1000
            
            results = {
                "flow_rate": round(flow_rate, 2),
                "calculated_diameter": pipe_size,
                "fluid_velocity": round(velocity, 3),
                "reynolds_number": round(Re, 0),
                "flow_regime": "Laminar" if Re < 2300 else "Transitional" if Re < 4000 else "Turbulent",
                "friction_factor": round(f, 4),
                "head_loss": round(head_loss, 3),
                "pressure_drop": round(pressure_drop, 2),
                "roughness_value": epsilon
            }
            
            compliance = "Darcy-Weisbach & Colebrook-White"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def duct_sizing(airflow: float, velocity: float = 10):
        """Calculate duct sizing for HVAC systems"""
        try:
            airflow_m3s = airflow / 3600
            area = airflow_m3s / velocity
            diameter = __import__('math').sqrt((4 * area) / __import__('math').pi) * 1000
            width = __import__('math').sqrt(2 * area) * 1000
            height = width / 2
            
            friction_factor = 0.02
            pressure_drop = friction_factor * (1.2 * velocity ** 2 / 2) * (100 / diameter)
            
            if velocity > 12:
                velocity_status = "High (noise risk)"
            elif velocity < 5:
                velocity_status = "Low (large duct)"
            else:
                velocity_status = "Optimal"
            
            results = {
                "airflow": round(airflow, 2),
                "design_velocity": velocity,
                "velocity_status": velocity_status,
                "circular_diameter": round(diameter, 0),
                "circular_pressure_drop": round(pressure_drop, 2),
                "rectangular_size": f"{round(width, 0)} × {round(height, 0)} mm",
                "recommendation": "Use circular duct" if diameter < 200 else "Either shape acceptable"
            }
            
            compliance = "ASHRAE 90.1"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def heat_transfer(area: float, delta_t: float, u_value: float = 1.5):
        """Calculate heat transfer and energy loss"""
        try:
            heat_loss = u_value * area * delta_t
            thermal_resistance = 1 / u_value
            
            annual_heating_degree_hours = 50000
            annual_energy_loss = (heat_loss * annual_heating_degree_hours) / (1000 * delta_t)
            heating_cost_per_kwh = 0.10
            annual_cost = annual_energy_loss * heating_cost_per_kwh
            
            if u_value < 0.3:
                insulation_rating = "Excellent"
            elif u_value < 0.6:
                insulation_rating = "Good"
            elif u_value < 1.2:
                insulation_rating = "Fair"
            else:
                insulation_rating = "Poor"
            
            recommended_u_value = 0.25
            potential_savings = area * delta_t * (u_value - recommended_u_value)
            
            results = {
                "surface_area": area,
                "temperature_diff": delta_t,
                "u_value": u_value,
                "thermal_resistance": round(thermal_resistance, 3),
                "insulation_rating": insulation_rating,
                "heat_loss": round(heat_loss, 2),
                "heat_loss_kw": round(heat_loss / 1000, 2),
                "annual_energy_loss": round(annual_energy_loss, 0),
                "annual_cost": round(annual_cost, 2),
                "potential_savings": round(potential_savings / 1000, 2) if potential_savings > 0 else 0
            }
            
            compliance = "ISO 6946 (Thermal Performance)"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def chiller_selection(cooling_load: float, inlet_temp: float, outlet_temp: float, chiller_type: str = 'airCooled'):
        """Select chiller based on cooling load"""
        try:
            chiller_specs = {
                'waterCooled': {'eer': 6.0, 'name': 'Water-Cooled Centrifugal', 'min_eer': 5.5},
                'airCooled': {'eer': 3.5, 'name': 'Air-Cooled Screw', 'min_eer': 2.8},
                'absorption': {'eer': 1.2, 'name': 'Absorption', 'min_eer': 0.6}
            }
            
            specs = chiller_specs.get(chiller_type, chiller_specs['airCooled'])
            eer = specs['eer']
            cop = eer / 3.412
            power_input = cooling_load / cop
            water_flow_rate = cooling_load / (4.18 * (inlet_temp - outlet_temp))
            tonnage = cooling_load / 3.517
            compliance_status = "Compliant" if eer >= specs['min_eer'] else "Non-compliant"
            
            annual_operating_hours = 4000
            electricity_rate = 0.12
            annual_energy_cost = power_input * annual_operating_hours * electricity_rate
            
            results = {
                "chiller_type": specs['name'],
                "cooling_capacity": round(cooling_load, 2),
                "tonnage": round(tonnage, 1),
                "water_flow_rate": round(water_flow_rate, 2),
                "temperature_range": round(inlet_temp - outlet_temp, 1),
                "eer": round(eer, 2),
                "cop": round(cop, 2),
                "power_input": round(power_input, 2),
                "compliance_status": compliance_status,
                "annual_energy_cost": round(annual_energy_cost, 0)
            }
            
            compliance = "ASHRAE 90.1-2019"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def cooling_tower_sizing(heat_rejection: float, wet_bulb: float, approach: float = 5, range: float = 5):
        """Calculate cooling tower sizing"""
        try:
            water_flow = heat_rejection / (4.18 * range)
            
            results = {
                "water_flow": round(water_flow, 2),
                "outlet_temp": round(wet_bulb + approach, 1)
            }
            
            compliance = "ASHRAE 90.1"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def fan_selection(airflow: float, pressure: float):
        """Select fan based on airflow and pressure"""
        try:
            efficiency = 0.65
            air_power = (airflow * pressure) / 3600
            shaft_power = air_power / efficiency
            motor_power = shaft_power * 1.15
            recommended_motor = __import__('math').ceil(motor_power * 2) / 2
            static_efficiency = efficiency * 100
            
            if pressure < 500:
                fan_type = 'Axial'
                specific_speed = 800
            elif pressure < 2000:
                fan_type = 'Centrifugal Backward Curved'
                specific_speed = 400
            else:
                fan_type = 'Centrifugal Radial'
                specific_speed = 200
            
            rpm = 1450
            sound_power = 50 + 10 * __import__('math').log10(airflow * pressure / 1000)
            
            results = {
                "airflow": round(airflow, 2),
                "static_pressure": pressure,
                "fan_type": fan_type,
                "air_power": round(air_power, 2),
                "shaft_power": round(shaft_power, 2),
                "motor_power": round(motor_power, 2),
                "recommended_motor": recommended_motor,
                "static_efficiency": round(static_efficiency, 1),
                "estimated_rpm": rpm,
                "sound_power_level": round(sound_power, 1)
            }
            
            compliance = "ISO 5801 (Fan Performance)"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def compressor_sizing(compressed_air_demand: float, system_pressure: float, air_type: str = 'screw', altitude: float = 0):
        """Calculate compressor sizing"""
        try:
            demand_cfm = compressed_air_demand * 35.315
            pressure_bar = system_pressure / 100000
            
            compressor_data = {
                'screw': {'specific_power': 6.5, 'efficiency': 0.85},
                'centrifugal': {'specific_power': 5.5, 'efficiency': 0.82},
                'reciprocating': {'specific_power': 7.2, 'efficiency': 0.78}
            }
            
            comp_type = compressor_data.get(air_type, compressor_data['screw'])
            base_power = (demand_cfm / 100) * comp_type['specific_power']
            altitude_corr = 1 - (altitude / 300) * 0.02
            required_power = (base_power / comp_type['efficiency']) * altitude_corr
            motor_size = int(__import__('math').ceil(required_power * 1.1 / 5) * 5)
            
            results = {
                "air_demand": round(compressed_air_demand, 2),
                "system_pressure": round(system_pressure, 0),
                "compressor_type": air_type.capitalize() + ' compressor',
                "base_power": round(base_power, 2),
                "altitude_adjustment": round(altitude_corr * 100, 1),
                "required_power": round(required_power, 2),
                "motor_size": motor_size
            }
            
            compliance = "ISO 1217"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def psychrometrics(dry_bulb_temp: float, relative_humidity: float, altitude: float = 0):
        """Calculate psychrometric properties"""
        try:
            Tdb = dry_bulb_temp
            RH = relative_humidity / 100
            P = 101.325 * __import__('math').pow(1 - 0.0065 * altitude / 288.15, 5.2559)
            
            Pws = 0.61121 * __import__('math').exp((18.678 - Tdb / 234.5) * (Tdb / (257.14 + Tdb)))
            Pw = RH * Pws
            W = 0.622 * Pw / (P - Pw)
            
            alpha = __import__('math').log(Pw / 0.61121)
            Tdp = (257.14 * alpha) / (18.678 - alpha)
            
            Twb = Tdb * __import__('math').atan(0.151977 * __import__('math').pow(RH * 100 + 8.313659, 0.5)) + \
                  __import__('math').atan(Tdb + RH * 100) - __import__('math').atan(RH * 100 - 1.676331) + \
                  0.00391838 * __import__('math').pow(RH * 100, 1.5) * __import__('math').atan(0.023101 * RH * 100) - 4.686035
            
            h = 1.006 * Tdb + W * (2501 + 1.86 * Tdb)
            v = (0.287 * (Tdb + 273.15) * (1 + 1.6078 * W)) / P
            density = 1 / v
            
            Ws = 0.622 * Pws / (P - Pws)
            degree_of_saturation = (W / Ws) * 100
            
            results = {
                "dry_bulb_temp": round(Tdb, 1),
                "relative_humidity": round(RH * 100, 1),
                "altitude": round(altitude, 0),
                "atmospheric_pressure": round(P, 2),
                "wet_bulb_temp": round(Twb, 1),
                "dew_point_temp": round(Tdp, 1),
                "humidity_ratio": round(W * 1000, 2),
                "specific_enthalpy": round(h, 2),
                "specific_volume": round(v, 3),
                "air_density": round(density, 3),
                "degree_of_saturation": round(degree_of_saturation, 1),
                "vapor_pressure": round(Pw, 2)
            }
            
            compliance = "ASHRAE Fundamentals"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def stress_strain_analysis(force: float, area: float, length: float, material: str = 'Steel', load_type: str = 'tensile', safety_factor: float = 2.0):
        """Analyze stress and strain in materials"""
        try:
            materials = {
                'Steel': {'E': 200, 'yield': 250, 'ultimate': 400, 'poisson': 0.3, 'name': 'Structural Steel (ASTM A36)'},
                'Aluminum': {'E': 70, 'yield': 95, 'ultimate': 110, 'poisson': 0.33, 'name': 'Aluminum 6061-T6'},
                'Stainless': {'E': 193, 'yield': 207, 'ultimate': 586, 'poisson': 0.29, 'name': 'Stainless 304'},
                'Concrete': {'E': 30, 'yield': 4, 'ultimate': 4.5, 'poisson': 0.2, 'name': 'Concrete (30 MPa)'},
                'Timber': {'E': 12, 'yield': 40, 'ultimate': 50, 'poisson': 0.35, 'name': 'Douglas Fir'}
            }
            
            mat = materials.get(material, materials['Steel'])
            stress = force / area
            strain = stress / (mat['E'] * 1000)
            delta = strain * length
            allowable_stress = mat['yield'] / safety_factor
            utilization_ratio = stress / allowable_stress
            safety_status = "SAFE" if utilization_ratio <= 1.0 else "OVERSTRESSED"
            
            lateral_strain = -mat['poisson'] * strain
            ultimate_load = mat['ultimate'] * area
            yield_load = mat['yield'] * area
            
            results = {
                "material": mat['name'],
                "load_type": load_type.capitalize() + ' Loading',
                "applied_force": round(force / 1000, 2),
                "cross_section": area,
                "length": length,
                "stress": round(stress, 2),
                "strain": round(strain, 6),
                "elongation": round(delta, 3),
                "modulus_of_elasticity": mat['E'],
                "poissons_ratio": mat['poisson'],
                "lateral_strain": round(lateral_strain, 6),
                "yield_strength": mat['yield'],
                "ultimate_strength": mat['ultimate'],
                "safety_factor": safety_factor,
                "allowable_stress": round(allowable_stress, 2),
                "utilization_ratio": round(utilization_ratio * 100, 1),
                "safety_status": safety_status,
                "yield_load": round(yield_load / 1000, 2),
                "ultimate_load": round(ultimate_load / 1000, 2)
            }
            
            compliance = "ASME Section VIII/AISC 360"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def bearing_selection(load: float, speed: float, life: float = 20000, reliability: float = 90, application_type: str = 'radial'):
        """Select bearing based on load and speed"""
        try:
            application_factors = {'smooth': 1.0, 'lightShock': 1.2, 'moderateShock': 1.5, 'heavyShock': 2.0}
            Ka = application_factors.get('lightShock', 1.0)
            P = load * Ka
            
            reliability_factors = {90: 1.00, 95: 0.62, 96: 0.53, 97: 0.44, 98: 0.33, 99: 0.21}
            a1 = reliability_factors.get(int(reliability), 1.00)
            
            n = speed
            
            bearing_types = {
                'radial': {'p': 3, 'name': 'Deep Groove Ball Bearing', 'speed_limit': 15000},
                'angular': {'p': 3, 'name': 'Angular Contact Ball Bearing', 'speed_limit': 12000},
                'cylindrical': {'p': 10/3, 'name': 'Cylindrical Roller Bearing', 'speed_limit': 8000},
                'tapered': {'p': 10/3, 'name': 'Tapered Roller Bearing', 'speed_limit': 5000},
                'spherical': {'p': 10/3, 'name': 'Spherical Roller Bearing', 'speed_limit': 4000},
                'thrust': {'p': 3, 'name': 'Thrust Ball Bearing', 'speed_limit': 3000}
            }
            
            bearing = bearing_types.get(application_type, bearing_types['radial'])
            
            L10_revolutions = (life * 60 * n) / 1e6
            C = P * __import__('math').pow(L10_revolutions / a1, 1 / bearing['p'])
            
            if C < 5000:
                bore_diameter = 17
            elif C < 10000:
                bore_diameter = 25
            elif C < 20000:
                bore_diameter = 35
            elif C < 40000:
                bore_diameter = 50
            elif C < 60000:
                bore_diameter = 60
            elif C < 100000:
                bore_diameter = 80
            else:
                bore_diameter = 100
            
            dn = bore_diameter * n
            dn_limit = bearing['speed_limit'] * bore_diameter
            speed_ok = dn < dn_limit
            
            C0 = C * 0.5
            min_load = 0.01 * C0
            min_load_ok = load >= min_load
            
            results = {
                "bearing_type": bearing['name'],
                "applied_load": load,
                "operating_speed": speed,
                "design_life": life,
                "reliability": reliability,
                "application_factor": Ka,
                "equivalent_load": round(P, 0),
                "reliability_factor": a1,
                "life_factor": bearing['p'],
                "required_dynamic_rating": round(C / 1000, 1),
                "required_static_rating": round(C0 / 1000, 1),
                "estimated_bore_diameter": bore_diameter,
                "dn_value": round(dn / 1000, 0),
                "speed_limit": speed_ok,
                "min_load_requirement": round(min_load, 1),
                "min_load_check": min_load_ok
            }
            
            compliance = "ISO 281:2007"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
