class CivilCalculators:
    @staticmethod
    def concrete_volume(length: float, width: float, depth: float):
        """Calculate concrete volume with wastage"""
        try:
            volume_m3 = length * width * depth
            volume_with_wastage = volume_m3 * 1.1
            
            results = {
                "volume": round(volume_m3, 2),
                "volume_with_wastage": round(volume_with_wastage, 2)
            }
            
            compliance = "ACI 318"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def steel_weight(diameter: float, length: float, quantity: int):
        """Calculate steel weight"""
        try:
            weight_per_bar = (diameter ** 2) * length * 0.00617
            total_weight = weight_per_bar * quantity
            
            results = {
                "weight_per_bar": round(weight_per_bar, 2),
                "total_weight": round(total_weight, 2),
                "total_weight_ton": round(total_weight / 1000, 3)
            }
            
            compliance = "BS 4449"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def beam_load(uniform_load: float, length: float, beam_depth: float = 600, beam_width: float = 300, concrete_grade: float = 25, steel_grade: float = 415, standard: str = 'IS456'):
        """Calculate beam load and design parameters"""
        try:
            codes = {
                'IS456': {
                    'name': 'IS 456:2000',
                    'reference': 'Indian Standard for RCC',
                    'deflection_limit': 'L/250',
                    'cover_required': 25,
                    'min_steel': 0.85,
                    'max_steel': 4.0
                },
                'ACI318': {
                    'name': 'ACI 318-19',
                    'reference': 'American Concrete Institute',
                    'deflection_limit': 'L/240',
                    'cover_required': 40,
                    'min_steel': 0.60,
                    'max_steel': 4.0
                },
                'EC2': {
                    'name': 'Eurocode 2',
                    'reference': 'EN 1992-1-1:2004',
                    'deflection_limit': 'L/250',
                    'cover_required': 30,
                    'min_steel': 0.26,
                    'max_steel': 4.0
                },
                'BS8110': {
                    'name': 'BS 8110-1:1997',
                    'reference': 'British Standard for Structural Concrete',
                    'deflection_limit': 'L/250',
                    'cover_required': 25,
                    'min_steel': 0.13,
                    'max_steel': 4.0
                }
            }
            
            code_data = codes.get(standard, codes['IS456'])
            reaction = (uniform_load * length) / 2
            max_moment = (uniform_load * length ** 2) / 8
            max_shear = (uniform_load * length) / 2
            
            fck = concrete_grade
            fy = steel_grade
            Es = 200000
            Ec = 5000 * __import__('math').sqrt(fck)
            modulus_ratio = Es / Ec
            
            effective_cover = code_data['cover_required'] + 10
            effective_depth = beam_depth - effective_cover
            moment_of_inertia = (beam_width * beam_depth ** 3) / 12
            
            deflection_limit_factor = 240 if code_data['deflection_limit'] == 'L/240' else 250
            permissible_deflection = (length * 1000) / deflection_limit_factor
            
            Mu = max_moment * 1.5 * 1e6
            Ru = Mu / (beam_width * effective_depth ** 2)
            percent_steel = (50 * fck / fy) * (1 - __import__('math').sqrt(1 - (4.6 * Ru / fck)))
            Ast = (percent_steel * beam_width * effective_depth) / 100
            
            min_steel = (code_data['min_steel'] / 100) * beam_width * effective_depth
            max_steel = (code_data['max_steel'] / 100) * beam_width * effective_depth
            required_steel = max(Ast, min_steel)
            steel_ok = required_steel <= max_steel
            
            bar_dia = 20
            bar_area = __import__('math').pi * (bar_dia / 2) ** 2
            num_bars = int(__import__('math').ceil(required_steel / bar_area))
            provided_steel = num_bars * bar_area
            actual_percent = (provided_steel / (beam_width * effective_depth)) * 100
            
            Vu = max_shear * 1.5
            tauV = (Vu * 1000) / (beam_width * effective_depth)
            
            if standard == 'IS456':
                beta = 0.8 * fck / (6.89 * actual_percent)
                tauC = 0.85 * __import__('math').sqrt(0.8 * fck) * (__import__('math').sqrt(1 + 5 * beta) - 1) / 6
            elif standard == 'ACI318':
                tauC = 0.17 * __import__('math').sqrt(fck)
            else:
                tauC = 0.12 * __import__('math').sqrt(fck)
            
            needs_shear_reinforcement = tauV > tauC
            stirrup_details = 'None - concrete shear capacity sufficient'
            stirrup_spacing = 'Not required'
            
            if needs_shear_reinforcement:
                Asv = 2 * __import__('math').pi * (8 / 2) ** 2
                spacing_calc = __import__('math').floor((0.87 * fy * Asv * effective_depth) / ((tauV - tauC) * beam_width))
                max_spacing = min(0.75 * effective_depth, 300)
                stirrup_spacing = min(spacing_calc, max_spacing)
                stirrup_details = f'2-legged 8mm ø @ {stirrup_spacing} mm c/c'
            
            results = {
                "design_code": code_data['name'] + '-' + code_data['reference'],
                "reactions": round(reaction, 2),
                "max_moment": round(max_moment, 2),
                "max_shear": round(max_shear, 2),
                "effective_depth": effective_depth,
                "cover_provided": code_data['cover_required'],
                "concrete_grade": f"M{concrete_grade}",
                "steel_grade": f"Fe {steel_grade}",
                "required_steel": round(required_steel, 0),
                "min_steel_required": round(min_steel, 0),
                "max_steel_allowed": round(max_steel, 0),
                "reinforcement": f"{num_bars} bars of {bar_dia}mm ø",
                "actual_steel_provided": round(provided_steel, 0),
                "steel_percentage": round(actual_percent, 2),
                "steel_compliance": steel_ok,
                "shear_stress": round(tauV, 3),
                "concrete_shear_capacity": round(tauC, 3),
                "stirrups": stirrup_details,
                "beam_size": f"{beam_width} × {beam_depth} mm"
            }
            
            compliance = code_data['name']
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def foundation_area(load: float, bearing_capacity: float):
        """Calculate foundation area"""
        try:
            required_area = load / bearing_capacity
            side = __import__('math').sqrt(required_area)
            circular_diameter = 2 * __import__('math').sqrt(required_area / __import__('math').pi)
            
            results = {
                "required_area": round(required_area, 2),
                "square_foundation": f"{side:.2f}×{side:.2f}m",
                "circular_diameter": round(circular_diameter, 2)
            }
            
            compliance = "IS 1904"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def column_design(axial_load: float, unsupported_length: float = 3000, concrete_grade: float = 25, steel_grade: float = 415, end_condition: str = 'bothFixed', design_code: str = 'IS456'):
        """Calculate column design parameters"""
        try:
            codes = {
                'IS456': {
                    'alpha': 0.4,
                    'gamma': 0.67,
                    'min_steel': 0.008,
                    'max_steel': 0.04,
                    'slenderness_limit': 12
                },
                'ACI318': {
                    'alpha': 0.55,
                    'gamma': 0.52,
                    'min_steel': 0.01,
                    'max_steel': 0.08,
                    'slenderness_limit': 22
                },
                'Eurocode': {
                    'alpha': 0.35,
                    'gamma': 0.8,
                    'min_steel': 0.002,
                    'max_steel': 0.04,
                    'slenderness_limit': 15
                }
            }
            
            code = codes.get(design_code, codes['IS456'])
            Pu = axial_load * 1.5
            
            effective_length_factors = {
                'bothFixed': 0.65,
                'oneFixed': 0.80,
                'bothPinned': 1.0,
                'cantilever': 2.0
            }
            
            k = effective_length_factors.get(end_condition, 1.0)
            effective_length = unsupported_length * k
            
            steel_ratio = 0.015
            required_area = (Pu * 1000) / (code['alpha'] * concrete_grade + code['gamma'] * steel_grade * steel_ratio)
            column_size = int(__import__('math').ceil(__import__('math').sqrt(required_area) / 50) * 50)
            
            slenderness_ratio = effective_length / column_size
            is_short_column = slenderness_ratio <= code['slenderness_limit']
            
            actual_area = column_size * column_size
            steel_area = max(code['min_steel'] * actual_area, steel_ratio * actual_area)
            
            bar_dia = 16 if column_size <= 300 else 20
            bar_area = __import__('math').pi * (bar_dia / 2) ** 2
            num_bars = int(__import__('math').ceil(steel_area / bar_area))
            num_bars = max(4, num_bars)
            
            tie_spacing = min(column_size, 16 * bar_dia, 300)
            tie_dia = max(6, bar_dia / 4)
            
            provided_capacity = code['alpha'] * concrete_grade * (actual_area - steel_area) + code['gamma'] * steel_grade * steel_area
            
            results = {
                "design_standard": design_code,
                "column_size": f"{column_size} × {column_size} mm",
                "effective_length": effective_length,
                "slenderness_ratio": round(slenderness_ratio, 2),
                "column_type": "Short Column" if is_short_column else "Slender Column",
                "reinforcement": f"{num_bars} bars of {bar_dia}mm ø",
                "steel_provided": round(num_bars * bar_area, 0),
                "steel_percentage": round((steel_area / actual_area) * 100, 2),
                "ties": f"{tie_dia}mm ø @ {tie_spacing}mm c/c",
                "design_capacity": round(provided_capacity / 1000, 2)
            }
            
            compliance = design_code
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def earthwork_volume(length: float, width: float, depth1: float, depth2: float):
        """Calculate earthwork volume with swelling factor"""
        try:
            area1 = length * depth1
            area2 = length * depth2
            volume = ((area1 + area2) / 2) * width
            volume_with_swelling = volume * 1.25
            
            results = {
                "volume": round(volume, 2),
                "volume_with_swelling": round(volume_with_swelling, 2)
            }
            
            compliance = "IS 1200"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def retaining_wall_pressure(height: float, soil_density: float = 18, friction_angle: float = 30):
        """Calculate retaining wall earth pressure"""
        try:
            phi = friction_angle * __import__('math').pi / 180
            Ka = (1 - __import__('math').sin(phi)) / (1 + __import__('math').sin(phi))
            pressure = Ka * soil_density * height
            total_force = 0.5 * pressure * height
            
            results = {
                "ka": round(Ka, 3),
                "pressure_at_base": round(pressure, 2),
                "total_force": round(total_force, 2)
            }
            
            compliance = "IS 1905"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def seismic_load(building_weight: float, zone: int, soil_type: str = 'medium', importance: float = 1.0):
        """Calculate seismic base shear"""
        try:
            zone_factors = {1: 0.10, 2: 0.16, 3: 0.24, 4: 0.36, 5: 0.40}
            Z = zone_factors.get(zone, 0.24)
            R = 5
            
            soil_factors = {'soft': 1.5, 'medium': 1.0, 'hard': 0.8}
            Sa = soil_factors.get(soil_type, 1.0)
            
            base_shear = (Z * importance * Sa / R) * building_weight
            
            results = {
                "base_shear": round(base_shear, 2),
                "seismic_zone": f"Zone {zone}",
                "zone_factor": Z,
                "soil_type": soil_type.capitalize(),
                "importance_factor": importance
            }
            
            compliance = "IS 1893:2016"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def wind_load(building_height: float, building_width: float, wind_speed: float, terrain_category: int = 2):
        """Calculate wind load on buildings"""
        try:
            terrain_factors = [1.0, 0.91, 0.88, 0.85]
            k2 = terrain_factors[terrain_category - 1] if 1 <= terrain_category <= 4 else 0.91
            
            Vz = wind_speed * k2
            pz = 0.6 * Vz ** 2
            area = building_height * building_width
            wind_force = pz * area * 1.2
            moment = wind_force * (building_height / 2)
            
            results = {
                "design_pressure": round(pz, 2),
                "wind_force": round(wind_force, 2),
                "overturn_moment": round(moment / 1000, 2),
                "design_wind_speed": round(Vz, 2),
                "terrain_category": f"Category {terrain_category}"
            }
            
            compliance = "IS 875(Part 3)"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def pile_foundation(load: float, soil_capacity: float, pile_diameter: float = 0.5, pile_length: float = 10):
        """Calculate pile foundation requirements"""
        try:
            pile_area = __import__('math').pi * (pile_diameter / 2) ** 2
            end_bearing = soil_capacity * pile_area * 9
            perimeter = __import__('math').pi * pile_diameter
            skin_friction = perimeter * pile_length * soil_capacity * 0.5
            total_capacity = (end_bearing + skin_friction) / 2.5
            num_piles = int(__import__('math').ceil(load / total_capacity))
            spacing = pile_diameter * 3
            
            results = {
                "pile_capacity": round(total_capacity, 2),
                "end_bearing": round(end_bearing, 2),
                "skin_friction": round(skin_friction, 2),
                "number_of_piles": num_piles,
                "pile_spacing": round(spacing, 2),
                "pile_diameter": round(pile_diameter * 1000, 0),
                "pile_length": pile_length
            }
            
            compliance = "IS 2911"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def bar_bending_schedule(member_type: str, quantity: int, bar_diameter: float, length: float):
        """Calculate bar bending schedule"""
        try:
            hook_length = bar_diameter * 10
            bend_deduction = bar_diameter * 2
            cutting_length = length
            hooks = 0
            bends = 0
            
            if member_type == 'stirrup':
                hooks = 2
                bends = 4
                cutting_length = length + (hooks * hook_length) - (bends * bend_deduction)
            elif member_type == 'column':
                hooks = 2
                cutting_length = length + (hooks * hook_length)
            
            total_length = cutting_length * quantity
            weight = (bar_diameter ** 2) * total_length * 0.00617 / 1000
            
            results = {
                "member_type": member_type.capitalize(),
                "bar_diameter": bar_diameter,
                "quantity": quantity,
                "cutting_length": round(cutting_length / 1000, 3),
                "total_length": round(total_length / 1000, 2),
                "weight": round(weight, 2)
            }
            
            compliance = "IS 2502"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def cantilever_beam(point_load: float, load_distance: float):
        """Calculate cantilever beam parameters"""
        try:
            max_moment = point_load * load_distance
            max_shear = point_load
            deflection = (point_load * load_distance ** 3) / (3 * 200 * 0.001)
            
            results = {
                "max_moment": round(max_moment, 2),
                "max_shear": round(max_shear, 2),
                "deflection": round(deflection, 2)
            }
            
            compliance = "IS 456"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def deflection_check(span: float, actual_deflection: float, member_type: str = 'beam'):
        """Check deflection compliance"""
        try:
            limits = {
                'beam': span / 250,
                'cantilever': span / 180,
                'slab': span / 350
            }
            
            permissible_deflection = limits.get(member_type, span / 250) * 1000
            ratio = actual_deflection / permissible_deflection
            status = "OK" if ratio <= 1.0 else "FAIL"
            
            results = {
                "span": span,
                "actual_deflection": round(actual_deflection, 2),
                "permissible_deflection": round(permissible_deflection, 2),
                "ratio": round(ratio, 2),
                "status": status
            }
            
            compliance = "IS 456"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def soil_bearing_capacity(cohesion: float, phi: float, gamma: float, depth: float, width: float, shape: str = 'strip'):
        """Calculate soil bearing capacity using Terzaghi's formula"""
        try:
            rad_phi = phi * __import__('math').pi / 180
            nq = (__import__('math').tan(__import__('math').pi / 4 + rad_phi / 2)) ** 2 * __import__('math').exp(__import__('math').pi * __import__('math').tan(rad_phi))
            
            if phi == 0:
                nc = 5.14
            else:
                nc = (nq - 1) / __import__('math').tan(rad_phi)
            
            ngamma = 2 * (nq + 1) * __import__('math').tan(rad_phi)
            
            sc = 1
            sq = 1
            sgamma = 1
            
            if shape == 'square':
                sc = 1.3
                sgamma = 0.8
            elif shape == 'circular':
                sc = 1.3
                sgamma = 0.6
            
            qult = sc * cohesion * nc + sq * depth * gamma * nq + sgamma * 0.5 * gamma * width * ngamma
            qsafe = qult / 3
            
            results = {
                "ultimate_capacity": round(qult, 2),
                "safe_bearing_capacity": round(qsafe, 2),
                "bearing_factors": {
                    "nc": round(nc, 2),
                    "nq": round(nq, 2),
                    "ngamma": round(ngamma, 2)
                }
            }
            
            compliance = "IS 6403"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
    
    @staticmethod
    def thermal_expansion(length: float, temp_diff: float, material: str = 'steel', constrained: str = 'no'):
        """Calculate thermal expansion and stress"""
        try:
            alpha = 12e-6
            modulus = 30
            
            if material == 'steel':
                alpha = 11.7e-6
                modulus = 200
            elif material == 'aluminum':
                alpha = 23e-6
                modulus = 70
            elif material == 'pvc':
                alpha = 54e-6
                modulus = 3
            
            deltaL = alpha * length * temp_diff
            stress = 0
            
            if constrained == 'yes':
                stress = alpha * temp_diff * modulus * 1000
            
            results = {
                "expansion": round(deltaL * 1000, 2),
                "induced_stress": round(stress, 1) if stress > 0 else "N/A",
                "thermal_strain": round(alpha * temp_diff, 6)
            }
            
            compliance = "IS 800"
            return {"results": results, "compliance": compliance, "success": True}
        except Exception as e:
            return {"error": str(e), "success": False}
