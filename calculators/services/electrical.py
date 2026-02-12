class ElectricalCalculators:
    @staticmethod
    def load_calculation(connected_load: float, demand_factor: float = 0.8, diversity_factor: float = 0.85, system_type: str = '3phase', voltage: float = 400, power_factor: float = 0.85):
        """Calculate electrical load with demand and diversity factors"""
        try:
            pf = power_factor
            demand_load = connected_load * demand_factor
            diversified_load = demand_load * diversity_factor
            
            if system_type == '3phase':
                design_current = (diversified_load * 1000) / (3 ** 0.5 * voltage * pf)
            else:
                design_current = (diversified_load * 1000) / (voltage * pf)
                
            apparent_power = diversified_load / pf
            active_power = diversified_load
            
            results = {
                "connected_load": round(connected_load, 2),
                "demand_factor": round(demand_factor, 2),
                "diversity_factor": round(diversity_factor, 2),
                "system_type": system_type,
                "voltage": round(voltage, 0),
                "power_factor": round(pf, 2),
                "diversified_load": round(diversified_load, 2),
                "apparent_power": round(apparent_power, 2),
                "design_current": round(design_current, 2)
            }
            
            compliance = "IEC 60364/NEC 220"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def cable_sizing(design_current: float, length: float, voltage_system: float = 400, standard: str = 'IEC', circuit_type: str = 'power', install_method: str = 'conduit', material: str = 'copper', ambient_temp: float = 40, grouping_factor: float = 1.0):
        """Calculate cable sizing with derating factors"""
        try:
            code_data = {
                'IEC': {'name': 'IEC 60364-5-52', 'ref': 'Current-carrying capacities'},
                'NEC': {'name': 'NEC 310', 'ref': 'Conductors for General Wiring'},
                'BS7671': {'name': 'BS 7671', 'ref': 'Wiring Regulations'},
                'AS3000': {'name': 'AS/NZS 3000', 'ref': 'Wiring Rules'}
            }
            
            code = code_data.get(standard, code_data['IEC'])
            max_vdrop = 3 if circuit_type == 'lighting' else 5
            
            install_derating = {'conduit': 0.8, 'cableTray': 0.85, 'directBuried': 0.9, 'openAir': 1.0, 'trunking': 0.75}
            install_factor = install_derating.get(install_method, 0.8)
            
            temp_derating = 0.91 if ambient_temp > 40 else 0.82 if ambient_temp > 50 else 1.0
            combined_derating = install_factor * temp_derating * grouping_factor
            required_ampacity = design_current / combined_derating
            
            cable_table = [
                {'mm2': 1.5, 'xlpe': 15, 'pvc': 13},
                {'mm2': 2.5, 'xlpe': 20, 'pvc': 17},
                {'mm2': 4, 'xlpe': 27, 'pvc': 23},
                {'mm2': 6, 'xlpe': 35, 'pvc': 30},
                {'mm2': 10, 'xlpe': 48, 'pvc': 40},
                {'mm2': 16, 'xlpe': 64, 'pvc': 53},
                {'mm2': 25, 'xlpe': 85, 'pvc': 70},
                {'mm2': 35, 'xlpe': 105, 'pvc': 88},
                {'mm2': 50, 'xlpe': 130, 'pvc': 110},
                {'mm2': 70, 'xlpe': 165, 'pvc': 140},
                {'mm2': 95, 'xlpe': 200, 'pvc': 170},
                {'mm2': 120, 'xlpe': 230, 'pvc': 195},
                {'mm2': 150, 'xlpe': 260, 'pvc': 220},
                {'mm2': 185, 'xlpe': 300, 'pvc': 250},
                {'mm2': 240, 'xlpe': 350, 'pvc': 300},
                {'mm2': 300, 'xlpe': 400, 'pvc': 340},
                {'mm2': 400, 'xlpe': 470, 'pvc': 400}
            ]
            
            suitable_cable = next((cable for cable in cable_table if cable['xlpe'] >= required_ampacity), None)
            if not suitable_cable:
                return {"error": "Current too high. Consider parallel cables or larger system.", "success": False}
            
            resistivity = 0.0172 if material == 'copper' else 0.0282
            material_name = 'Cu' if material == 'copper' else 'Al'
            resistance = (resistivity * length) / suitable_cable['mm2']
            reactance = 0.08 * length / 1000
            impedance = (resistance ** 2 + reactance ** 2) ** 0.5
            voltage_drop = 3 ** 0.5 * design_current * impedance
            voltage_drop_percent = (voltage_drop / voltage_system) * 100
            compliant = voltage_drop_percent <= max_vdrop
            power_loss = 3 * design_current ** 2 * resistance
            num_cores = '4C' if voltage_system > 100 else '3C'
            
            results = {
                "cable_size": suitable_cable['mm2'],
                "cable_config": f"{num_cores}× {suitable_cable['mm2']}mm² {material_name}XLPE",
                "ampacity": suitable_cable['xlpe'],
                "required_ampacity": round(required_ampacity, 2),
                "design_current": round(design_current, 2),
                "voltage_drop": round(voltage_drop, 2),
                "voltage_drop_percent": round(voltage_drop_percent, 2),
                "max_allowed_drop": max_vdrop,
                "compliance": compliant,
                "power_loss": round(power_loss, 2),
                "derating_factors": {
                    "installation": round(install_factor * 100, 0),
                    "temperature": round(temp_derating * 100, 0),
                    "grouping": round(grouping_factor * 100, 0),
                    "combined": round(combined_derating * 100, 0)
                }
            }
            
            return {"results": results, "compliance": code['name'] + '-' + code['ref'], "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def breaker_selection(design_current: float, fault_current: float, breaker_type: str = 'MCB', curve_type: str = 'C', standard: str = 'IEC'):
        """Select circuit breaker based on load and fault current"""
        try:
            code_data = {
                'IEC': {'name': 'IEC 60947-2', 'ref': 'Circuit-breakers'},
                'NEMA': {'name': 'NEMA AB1', 'ref': 'Molded Case Circuit Breakers'}
            }
            
            code = code_data.get(standard, code_data['IEC'])
            standard_ratings = [6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100, 125, 160, 200, 250, 320, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3200, 4000, 5000, 6300]
            
            continuous_load = design_current * 1.25
            selected_in = next((rating for rating in standard_ratings if rating >= continuous_load), standard_ratings[-1])
            in_check = selected_in >= design_current
            
            required_icu = fault_current * 1.2
            standard_icu = [3, 6, 10, 15, 25, 35, 50, 65, 80, 100, 150]
            selected_icu = next((icu for icu in standard_icu if icu >= required_icu), standard_icu[-1])
            icu_check = selected_icu >= fault_current
            
            curve_data = {
                'B': {'name': 'Curve B', 'trip_point': '3-5x In', 'application': 'Residential, lighting'},
                'C': {'name': 'Curve C', 'trip_point': '5-10x In', 'application': 'General purpose, commercial'},
                'D': {'name': 'Curve D', 'trip_point': '10-20x In', 'application': 'Motor, inductive loads'},
                'K': {'name': 'Curve K', 'trip_point': '10-14x In', 'application': 'Motor protection'},
                'Z': {'name': 'Curve Z', 'trip_point': '2-3x In', 'application': 'Electronic equipment'}
            }
            
            curve = curve_data.get(curve_type, curve_data['C'])
            
            breaker_types = {
                'MCB': {'name': 'MCB (Miniature Circuit Breaker)', 'max_in': 125, 'max_icu': 25, 'poles': '1P/2P/3P/4P'},
                'MCCB': {'name': 'MCCB (Molded Case Circuit Breaker)', 'max_in': 1600, 'max_icu': 100, 'poles': '3P/4P'},
                'ACB': {'name': 'ACB (Air Circuit Breaker)', 'max_in': 6300, 'max_icu': 150, 'poles': '3P/4P'},
                'VCB': {'name': 'VCB (Vacuum Circuit Breaker)', 'max_in': 4000, 'max_icu': 63, 'poles': '3P'}
            }
            
            breaker_spec = breaker_types.get(breaker_type, breaker_types['MCB'])
            type_appropriate = selected_in <= breaker_spec['max_in']
            utilization = (design_current / selected_in) * 100
            
            trip_range = curve['trip_point'].split('-')
            instant_trip_min = selected_in * float(trip_range[0])
            instant_trip_max = selected_in * float(trip_range[1])
            
            results = {
                "breaker_type": breaker_spec['name'],
                "breaker_rating": selected_in,
                "breaking_capacity": selected_icu,
                "trip_curve": curve['name'],
                "trip_point": curve['trip_point'],
                "application": curve['application'],
                "poles": breaker_spec['poles'],
                "in_check": in_check,
                "icu_check": icu_check,
                "type_check": type_appropriate,
                "utilization": round(utilization, 1),
                "instant_trip_min": round(instant_trip_min, 0),
                "instant_trip_max": round(instant_trip_max, 0)
            }
            
            return {"results": results, "compliance": code['name'] + '-' + code['ref'], "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def transformer_sizing(total_load: float, growth_factor: float = 1.25, efficiency: float = 0.98, standard: str = 'IEC', cooling_type: str = 'ONAN'):
        """Calculate transformer sizing with growth and efficiency factors"""
        try:
            code_data = {
                'IEC': {'name': 'IEC 60076', 'ref': 'IEC 60076-1:2011-Power Transformers'},
                'IEEE': {'name': 'IEEE C57.12.00', 'ref': 'IEEE C57.12.00-2015-General Requirements'}
            }
            
            code = code_data.get(standard, code_data['IEC'])
            diversity_factor = 0.8
            diversified_load = total_load * diversity_factor
            future_load = diversified_load * growth_factor
            required_kva = future_load / efficiency
            
            standard_sizes = [15, 25, 30, 50, 75, 100, 150, 200, 250, 300, 400, 500, 630, 750, 1000, 1250, 1500, 1600, 2000, 2500, 3150, 4000, 5000]
            selected_size = next((size for size in standard_sizes if size >= required_kva), standard_sizes[-1])
            
            actual_loading = (total_load / selected_size) * 100
            future_loading = (future_load / selected_size) * 100
            optimal_loading = 50 <= future_loading <= 80
            
            no_load_loss = selected_size * 0.002
            load_loss = selected_size * 0.01 * (actual_loading / 100) ** 2
            total_loss = no_load_loss + load_loss
            output_power = total_load
            input_power = output_power + total_loss
            actual_efficiency = (output_power / input_power) * 100
            
            cooling_data = {
                'ONAN': {'name': 'Oil Natural Air Natural', 'temp_rise': 60},
                'ONAF': {'name': 'Oil Natural Air Forced', 'temp_rise': 65},
                'OFAF': {'name': 'Oil Forced Air Forced', 'temp_rise': 65},
                'OFWF': {'name': 'Oil Forced Water Forced', 'temp_rise': 55}
            }
            
            cooling = cooling_data.get(cooling_type, cooling_data['ONAN'])
            impedance_percent = 4 if selected_size <= 1000 else 6 if selected_size <= 2500 else 8
            fault_current = (selected_size * 1000) / (3 ** 0.5 * 400 * (impedance_percent / 100))
            
            results = {
                "total_connected_load": round(total_load, 2),
                "diversified_load": round(diversified_load, 2),
                "future_load": round(future_load, 2),
                "required_kva": round(required_kva, 2),
                "standard_size": selected_size,
                "current_loading": round(actual_loading, 1),
                "future_loading": round(future_loading, 1),
                "optimal_loading": optimal_loading,
                "no_load_loss": round(no_load_loss, 2),
                "load_loss": round(load_loss, 2),
                "total_loss": round(total_loss, 2),
                "efficiency": round(actual_efficiency, 2),
                "cooling_type": cooling['name'],
                "temp_rise": cooling['temp_rise'],
                "impedance": impedance_percent,
                "fault_current": round(fault_current / 1000, 2)
            }
            
            return {"results": results, "compliance": code['name'], "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def power_factor_correction(active_power: float, current_pf: float, target_pf: float = 0.95, voltage: float = 400, standard: str = 'IEC'):
        """Calculate power factor correction requirements"""
        try:
            current_angle = __import__('math').acos(current_pf)
            target_angle = __import__('math').acos(target_pf)
            
            current_reactive_power = active_power * __import__('math').tan(current_angle)
            target_reactive_power = active_power * __import__('math').tan(target_angle)
            required_kvar = current_reactive_power - target_reactive_power
            
            current_kva = active_power / current_pf
            target_kva = active_power / target_pf
            kva_reduction = current_kva - target_kva
            
            current_before = (current_kva * 1000) / (3 ** 0.5 * voltage)
            current_after = (target_kva * 1000) / (3 ** 0.5 * voltage)
            current_reduction = current_before - current_after
            current_reduction_percent = (current_reduction / current_before) * 100
            
            line_resistance = 0.1
            power_loss_before = 3 * current_before ** 2 * line_resistance
            power_loss_after = 3 * current_after ** 2 * line_resistance
            power_loss_saving = power_loss_before - power_loss_after
            
            standard_capacitor_sizes = [5, 10, 15, 20, 25, 30, 40, 50, 60, 75, 100, 125, 150, 200, 250, 300]
            selected_capacitor_size = next((size for size in standard_capacitor_sizes if size >= abs(required_kvar)), 300)
            
            monthly_saving_kwh = power_loss_saving * 720
            cost_per_kwh = 0.15
            monthly_saving = monthly_saving_kwh * cost_per_kwh
            
            results = {
                "active_power": round(active_power, 2),
                "current_pf": round(current_pf, 3),
                "target_pf": round(target_pf, 3),
                "required_kvar": round(abs(required_kvar), 2),
                "selected_capacitor_size": selected_capacitor_size,
                "current_reactive_power": round(current_reactive_power, 2),
                "target_reactive_power": round(target_reactive_power, 2),
                "current_kva": round(current_kva, 2),
                "target_kva": round(target_kva, 2),
                "kva_reduction": round(kva_reduction, 2),
                "current_before": round(current_before, 2),
                "current_after": round(current_after, 2),
                "current_reduction": round(current_reduction, 2),
                "current_reduction_percent": round(current_reduction_percent, 1),
                "power_loss_saving": round(power_loss_saving, 2),
                "monthly_saving": round(monthly_saving, 2)
            }
            
            code = "IEC 61921" if standard == 'IEC' else "IEEE 1459"
            return {"results": results, "compliance": code, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def generator_sizing(running_load: float, starting_load: float, altitude: float = 0, temperature: float = 25, fuel_type: str = 'diesel'):
        """Calculate generator sizing with environmental derating"""
        try:
            starting_multiplier = 3.0
            starting_kva = starting_load * starting_multiplier
            total_kva = running_load + starting_kva
            
            altitude_derating_factor = 1.0
            if altitude > 1000:
                excess_altitude = altitude - 1000
                altitude_derating_factor = 1 - (excess_altitude / 500 * 0.04)
            
            temperature_derating_factor = 1.0
            if temperature > 25:
                temperature_derating_factor = 1 - ((temperature - 25) / 10 * 0.01)
            
            combined_derating_factor = altitude_derating_factor * temperature_derating_factor
            required_kva = total_kva / combined_derating_factor
            
            standard_sizes = [10, 15, 20, 30, 45, 60, 75, 80, 100, 125, 150, 175, 200, 250, 300, 350, 400, 500, 625, 750, 1000, 1250, 1500, 2000]
            selected_size = next((size for size in standard_sizes if size >= required_kva), 2000)
            
            loading_percent = (total_kva / (selected_size * combined_derating_factor)) * 100
            loading_status = "Good" if loading_percent < 70 else "Adequate" if loading_percent < 85 else "Overloaded"
            
            fuel_consumption_factors = {'diesel': 0.22, 'gas': 0.35, 'hfo': 0.25}
            fuel_factor = fuel_consumption_factors.get(fuel_type, 0.22)
            estimated_fuel_consumption = (running_load * 0.8) * fuel_factor
            
            typical_tank_size = selected_size * 0.6
            runtime = typical_tank_size / estimated_fuel_consumption
            
            sound_power_level = 95 + 10 * __import__('math').log10(selected_size / 100)
            sound_pressure_at_7m = sound_power_level - 17
            sound_compliance = "Residential compliant" if sound_pressure_at_7m < 75 else "May require enclosure"
            
            alternator_type = "2-pole (3000/3600 RPM)" if selected_size < 100 else "4-pole (1500/1800 RPM)"
            voltage_regulation = "±1% (Automatic Voltage Regulator)"
            
            if selected_size <= 30:
                starting_method = "Electric start (12V battery)"
            elif selected_size <= 200:
                starting_method = "Electric start (24V battery)"
            else:
                starting_method = "Electric start (24V/48V battery bank)"
            
            results = {
                "running_load": round(running_load, 2),
                "starting_load": round(starting_load, 2),
                "starting_method": "DOL (3× multiplier)",
                "total_load_requirement": round(total_kva, 2),
                "altitude": round(altitude, 0),
                "altitude_derating": round(altitude_derating_factor * 100, 1),
                "ambient_temperature": round(temperature, 0),
                "temperature_derating": round(temperature_derating_factor * 100, 1),
                "combined_derating": round(combined_derating_factor * 100, 1),
                "required_gen_kva": round(required_kva, 2),
                "recommended_size": selected_size,
                "generator_type": fuel_type.upper() + " Generator Set",
                "alternator_spec": alternator_type,
                "voltage_regulation": voltage_regulation,
                "starting_system": starting_method,
                "actual_loading": round(loading_percent, 1),
                "loading_status": loading_status,
                "fuel_consumption": round(estimated_fuel_consumption, 2),
                "typical_tank_size": round(typical_tank_size, 0),
                "estimated_runtime": round(runtime, 1),
                "sound_power_level": round(sound_power_level, 1),
                "sound_pressure_at_7m": round(sound_pressure_at_7m, 1),
                "sound_compliance": sound_compliance
            }
            
            return {"results": results, "compliance": "ISO 8528-1:2018/NFPA 110:2019", "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def short_circuit(voltage: float, transformer_kva: float, impedance: float, standard: str = 'IEC'):
        """Calculate short circuit current"""
        try:
            code_data = {
                'IEC': {'name': 'IEC 60909', 'ref': 'IEC 60909-0:2016'},
                'IEEE': {'name': 'IEEE 1584', 'ref': 'IEEE 1584-2018'}
            }
            
            code = code_data.get(standard, code_data['IEC'])
            base_kva = transformer_kva
            z_percent = impedance / 100
            fault_current = (base_kva * 1000) / (3 ** 0.5 * voltage * z_percent)
            pscc = fault_current / 1000
            breaking_capacity = pscc * 1.5
            
            if breaking_capacity <= 6:
                device_type = 'MCB (Miniature Circuit Breaker)'
                icn = int(__import__('math').ceil(breaking_capacity / 3) * 3)
            elif breaking_capacity <= 50:
                device_type = 'MCCB (Molded Case Circuit Breaker)'
                icn = int(__import__('math').ceil(breaking_capacity / 10) * 10)
            elif breaking_capacity <= 100:
                device_type = 'ACB (Air Circuit Breaker)'
                icn = int(__import__('math').ceil(breaking_capacity / 20) * 20)
            else:
                device_type = 'VCB (Vacuum Circuit Breaker)'
                icn = int(__import__('math').ceil(breaking_capacity / 25) * 25)
            
            clearing_time = 0.02
            let_through_energy = (pscc * 1000) ** 2 * clearing_time
            
            results = {
                "fault_current": round(fault_current, 2),
                "pscc_ka": round(pscc, 2),
                "breaking_capacity": round(breaking_capacity, 2),
                "device_type": device_type,
                "recommended_icn": icn,
                "let_through_energy": round(let_through_energy / 1e6, 2)
            }
            
            return {"results": results, "compliance": code['name'] + '-' + code['ref'], "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def voltage_drop(current: float, length: float, cross_section: float, voltage: float = 400, material: str = 'copper', standard: str = 'IEC', circuit_type: str = 'power', system_type: str = '3phase'):
        """Calculate voltage drop with detailed parameters"""
        try:
            resistivity = 0.0172 if material == 'copper' else 0.0282
            material_name = 'Cu' if material == 'copper' else 'Al'
            
            codes = {
                'IEC': {'name': 'IEC 60364-5-52', 'power': 5, 'lighting': 3, 'feeder': 5, 'branch': 3},
                'NEC': {'name': 'NEC 210.19(A)', 'power': 5, 'lighting': 3, 'feeder': 5, 'branch': 3},
                'BS7671': {'name': 'BS 7671', 'power': 5, 'lighting': 3, 'feeder': 5, 'branch': 3},
                'AS3000': {'name': 'AS/NZS 3000', 'power': 5, 'lighting': 3, 'feeder': 5, 'branch': 3}
            }
            
            code_data = codes.get(standard, codes['IEC'])
            max_vdrop_percent = code_data['lighting'] if circuit_type == 'lighting' else code_data['power']
            
            resistance = (resistivity * length) / cross_section
            reactance = 0.08 * (length / 1000)
            impedance = (resistance ** 2 + reactance ** 2) ** 0.5
            
            if system_type == '3phase':
                v_drop = 3 ** 0.5 * current * impedance
            elif system_type == '1phase':
                v_drop = 2 * current * impedance
            else:
                v_drop = 3 ** 0.5 * current * impedance
            
            v_drop_percent = (v_drop / voltage) * 100
            compliant = v_drop_percent <= max_vdrop_percent
            
            power_loss = 3 * current ** 2 * resistance if system_type == '3phase' else 2 * current ** 2 * resistance
            
            cable_table = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240]
            next_size = None
            for i in range(len(cable_table)):
                if cable_table[i] > cross_section:
                    next_size = cable_table[i]
                    break
            
            recommendation = "Voltage drop acceptable with good safety margin"
            if not compliant:
                if next_size:
                    recommendation = f"Increase cable size to {next_size} mm² or reduce run length"
                else:
                    recommendation = "Use larger cable or reduce length"
            else:
                margin = max_vdrop_percent - v_drop_percent
                if margin <= 1:
                    recommendation = "Voltage drop acceptable but close to limit"
            
            results = {
                "voltage_drop": round(v_drop, 2),
                "voltage_drop_percent": round(v_drop_percent, 2),
                "max_allowed_percent": max_vdrop_percent,
                "resistance": round(resistance, 4),
                "impedance": round(impedance, 4),
                "reactance": round(reactance, 4),
                "power_loss": round(power_loss, 2),
                "compliant": compliant,
                "recommendation": recommendation
            }
            
            return {"results": results, "compliance": code_data['name'], "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def earthing_conductor(fault_current: float, fault_time: float = 1):
        """Calculate earthing conductor size"""
        try:
            k_factor = 143
            min_area = (fault_current * __import__('math').sqrt(fault_time)) / k_factor
            standard_sizes = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300]
            selected_size = next((size for size in standard_sizes if size >= min_area), 300)
            
            results = {
                "minimum_conductor_area": round(min_area, 2),
                "recommended_conductor": selected_size,
                "current_density": round(fault_current / selected_size, 2),
                "k_factor": k_factor
            }
            
            return {"results": results, "compliance": "IEC 60364-5-54/BS 7671", "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def busbar_sizing(current: float, busbars_per_phase: int = 1, material: str = 'copper'):
        """Calculate busbar sizing"""
        try:
            material_data = {
                'copper': {'current_density': 1.2, 'name': 'Copper', 'conductivity': '100% IACS', 'temp_rise': '35°C', 'standard': 'IEC 61439'},
                'aluminum': {'current_density': 0.8, 'name': 'Aluminum', 'conductivity': '61% IACS', 'temp_rise': '35°C', 'standard': 'IEC 61439'}
            }
            
            mat_data = material_data.get(material, material_data['copper'])
            current_per_bar = current / busbars_per_phase
            min_area = current_per_bar / mat_data['current_density']
            
            standard_sizes = [
                {'w': 20, 't': 3, 'area': 60},
                {'w': 25, 't': 3, 'area': 75},
                {'w': 25, 't': 5, 'area': 125},
                {'w': 30, 't': 5, 'area': 150},
                {'w': 40, 't': 5, 'area': 200},
                {'w': 50, 't': 5, 'area': 250},
                {'w': 60, 't': 5, 'area': 300},
                {'w': 60, 't': 10, 'area': 600},
                {'w': 80, 't': 10, 'area': 800},
                {'w': 100, 't': 10, 'area': 1000}
            ]
            
            selected_size = next((size for size in standard_sizes if size['area'] >= min_area), standard_sizes[-1])
            actual_current_density = current_per_bar / selected_size['area']
            temp_rise = (actual_current_density / mat_data['current_density']) * 35
            safety_margin = selected_size['area'] / min_area
            
            results = {
                "current_per_bar": round(current_per_bar, 2),
                "minimum_area": round(min_area, 2),
                "recommended_size": f"{selected_size['w']} x {selected_size['t']} mm",
                "actual_area": selected_size['area'],
                "actual_current_density": round(actual_current_density, 2),
                "design_current_density": mat_data['current_density'],
                "estimated_temp_rise": round(temp_rise, 1),
                "safety_margin": round(safety_margin, 2),
                "material": mat_data['name']
            }
            
            return {"results": results, "compliance": mat_data['standard'], "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
