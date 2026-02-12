import json
import os
import re
from sqlalchemy.orm import Session
from workflow_models import Workflow, WorkflowCategory, WorkflowInput, WorkflowOutput, WorkflowStep, Equation, EquationInput, EquationOutput

class WorkflowService:
    @staticmethod
    def load_workflows_from_json(db: Session):
        """Load workflows from shared/data/workflows.json and populate the database"""
        # Check if we already have workflows
        if db.query(Workflow).count() > 0:
            return
        
        # Load workflows from JSON file
        # Calculate the correct path to shared/data/workflows.json
        import sys
        import os
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Go up 3 directories: backend/workflows/services -> backend -> /
        project_root = os.path.abspath(os.path.join(current_dir, "..", "..", ".."))
        json_path = os.path.join(project_root, "shared", "data", "workflows.json")
        
        # Verify the file exists
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Workflows file not found at: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create categories and subcategories
        categories = {}
        for workflow in data['workflows']:
            domain = workflow['domain']
            # Create domain category
            if domain not in categories:
                category = WorkflowCategory(
                    name=domain.capitalize(),
                    domain=domain,
                    subcategory=None
                )
                db.add(category)
                db.commit()
                db.refresh(category)
                categories[domain] = category
        
        # Create workflows
        for workflow_data in data['workflows']:
            workflow = Workflow(
                workflow_id=workflow_data['id'],
                title=workflow_data['title'],
                description=workflow_data.get('description'),
                domain=workflow_data['domain'],
                category_id=categories[workflow_data['domain']].id
            )
            db.add(workflow)
            db.commit()
            db.refresh(workflow)
            
            # Create inputs
            for input_name in workflow_data.get('inputs', []):
                input_obj = WorkflowInput(
                    workflow_id=workflow.id,
                    name=input_name
                )
                db.add(input_obj)
            
            # Create outputs
            for output_name in workflow_data.get('outputs', []):
                output_obj = WorkflowOutput(
                    workflow_id=workflow.id,
                    name=output_name
                )
                db.add(output_obj)
            
            # Create steps
            for step_number, step_name in enumerate(workflow_data.get('steps', []), 1):
                step_obj = WorkflowStep(
                    workflow_id=workflow.id,
                    step_number=step_number,
                    name=step_name
                )
                db.add(step_obj)
        
        db.commit()
    
    @staticmethod
    def get_all_workflows(db: Session):
        """Get all workflows grouped by domain and subcategory"""
        workflows = db.query(Workflow).all()
        result = {
            "electrical": [],
            "mechanical": [],
            "civil": []
        }
        
        for workflow in workflows:
            result[workflow.domain].append({
                "id": workflow.workflow_id,
                "title": workflow.title,
                "description": workflow.description,
                "inputs": [input.name for input in workflow.inputs],
                "outputs": [output.name for output in workflow.outputs],
                "steps": [step.name for step in workflow.steps]
            })
        
        return result
    
    @staticmethod
    def execute_workflow(workflow_id: str, inputs: Dict[str, Any]):
        """Execute a workflow with given inputs"""
        import time
        time.sleep(1)  # Simulate processing time
        
        domain = workflow_id.split('_')[0]
        results = {}
        
        # Normalize workflow_id for matching (remove version suffix like _1)
        normalized_id = re.sub(r"_\d+$", "", workflow_id) if re.search(r"\d$", workflow_id) else workflow_id
        
        # Simulate workflow execution based on workflow type
        if domain == 'civil':
            if normalized_id == 'civil_earthworks' or workflow_id == 'civil_earthworks_volume':
                results['cut_volume'] = 1250
                results['fill_volume'] = 1180
                results['net_balance'] = -70
                results['compliance'] = 'Quantity survey completed successfully'
            elif normalized_id == 'civil_rebar_takeoff' or workflow_id == 'civil_rebar_takeoff':
                results['bar_count'] = 245
                results['bar_length'] = 490
                results['total_weight'] = 1250
                results['compliance'] = 'Rebar quantities calculated'
            elif normalized_id == 'civil_slab_design' or workflow_id == 'civil_slab_design':
                results['slab_thickness'] = 150
                results['reinforcement_area'] = 0.35
                results['deflection_ratio'] = 0.003
                results['compliance'] = 'Deflection within limits (L/250)'
            elif normalized_id == 'civil_column_design' or workflow_id == 'civil_column_design':
                results['rebar_ratio'] = 0.018
                results['bar_layout'] = '12-D16'
                results['utilization'] = 0.92
                results['compliance'] = 'Column section adequate'
            elif normalized_id == 'civil_footing_sizing' or workflow_id == 'civil_footing_sizing':
                results['footing_area'] = 4.5
                results['thickness'] = 600
                results['soil_pressure'] = 145
                results['compliance'] = 'Bearing pressure within limits'
            elif normalized_id == 'civil_retaining_wall' or workflow_id == 'civil_retaining_wall':
                results['safety_factors'] = {'sliding': 1.8, 'overturning': 2.2, 'bearing': 3.1}
                results['base_pressure'] = 135
                results['stability_ok'] = True
                results['compliance'] = 'All stability checks passed'
            elif normalized_id == 'civil_pavement_design' or workflow_id == 'civil_pavement_design':
                results['layer_thicknesses'] = {'surface': 50, 'base': 150, 'subbase': 200}
                results['design_life'] = 20
                results['compliance'] = 'Pavement structure designed for 20-year life'
            elif normalized_id == 'civil_concrete_mix' or workflow_id == 'civil_concrete_mix':
                results['cement_qty'] = 350
                results['water_qty'] = 185
                results['aggregate_qty'] = 1865
                results['compliance'] = 'Mix proportioning completed'
            elif normalized_id == 'civil_drainage_design':
                results['peak_flow'] = 125
                results['pipe_size'] = '300mm'
                results['culvert_size'] = '1200mm'
                results['compliance'] = 'Drainage system sized for 10-year storm'
            elif normalized_id == 'civil_survey_control':
                results['adjusted_coords'] = {'x': 1234.56, 'y': 7890.12}
                results['closure_error'] = 0.015
                results['compliance'] = 'Survey control established within limits'
        
        elif domain == 'electrical':
            if normalized_id == 'electrical_load_calc' or workflow_id == 'electrical_load_calc':
                results['connected_load'] = 125
                results['demand_load'] = 85
                results['service_size'] = 125
                results['compliance'] = 'Demand load calculated using IEC 60364'
            elif normalized_id == 'electrical_panel_schedule' or workflow_id == 'electrical_panel_schedule':
                results['phase_balance'] = 95
                results['panel_loads'] = {'phaseA': 45, 'phaseB': 42, 'phaseC': 43}
                results['compliance'] = 'Panel balanced within 5%'
            elif normalized_id == 'electrical_cable_sizing' or workflow_id == 'electrical_cable_sizing':
                results['cable_size'] = 35
                results['voltage_drop'] = 2.8
                results['ampacity_ok'] = True
                results['compliance'] = 'Cable size selected per IEC 60228'
            elif normalized_id == 'electrical_short_circuit' or workflow_id == 'electrical_short_circuit':
                results['fault_current'] = 12.5
                results['interrupting_rating'] = 25
                results['compliance'] = 'Equipment rating sufficient'
            elif normalized_id == 'electrical_lighting_layout' or workflow_id == 'electrical_lighting_layout':
                results['fixture_count'] = 12
                results['spacing'] = 4.5
                results['compliance'] = 'Lighting levels meet EN 12464'
            elif normalized_id == 'electrical_grounding' or workflow_id == 'electrical_grounding':
                results['ground_conductor_size'] = 50
                results['estimated_resistance'] = 0.8
                results['compliance'] = 'Ground resistance within 1Ω limit'
            elif normalized_id == 'electrical_transformer_sizing' or workflow_id == 'electrical_transformer_sizing':
                results['transformer_kva'] = 160
                results['loading_pct'] = 75
                results['compliance'] = 'Transformer sizing complete'
            elif normalized_id == 'electrical_solar_pv' or workflow_id == 'electrical_solar_pv':
                results['pv_kwp'] = 15
                results['inverter_kw'] = 12
                results['compliance'] = 'PV system sized for daily consumption'
            elif normalized_id == 'electrical_motor_starting':
                results['starting_current'] = 350
                results['voltage_dip'] = 8.5
                results['compliance'] = 'Motor starting analysis completed'
            elif normalized_id == 'electrical_harmonics':
                results['thd'] = 12.5
                results['filter_size'] = 150
                results['compliance'] = 'Harmonic distortion within limits'
        
        elif domain == 'mechanical':
            if normalized_id == 'mechanical_hvac_load' or workflow_id == 'mechanical_hvac_load':
                results['cooling_load'] = 125
                results['heating_load'] = 85
                results['compliance'] = 'Load calculation per ASHRAE'
            elif normalized_id == 'mechanical_duct_sizing' or workflow_id == 'mechanical_duct_sizing':
                results['duct_dimensions'] = '300x200'
                results['pressure_drop'] = 8.5
                results['compliance'] = 'Pressure drop within limits'
            elif normalized_id == 'mechanical_pump_sizing' or workflow_id == 'mechanical_pump_sizing':
                results['pump_power'] = 15
                results['pump_model'] = 'P-125'
                results['compliance'] = 'Pump selected per manufacturer data'
            elif normalized_id == 'mechanical_pipe_sizing' or workflow_id == 'mechanical_pipe_sizing':
                results['pipe_diameter'] = 100
                results['pressure_drop'] = 6.5
                results['compliance'] = 'Pipe size determined by velocity'
            elif normalized_id == 'mechanical_pressure_drop' or workflow_id == 'mechanical_pressure_drop':
                results['pressure_drop_total'] = 45
                results['compliance'] = 'System pressure losses calculated'
            elif normalized_id == 'mechanical_chiller_selection' or workflow_id == 'mechanical_chiller_selection':
                results['chiller_tons'] = 45
                results['chiller_model'] = 'C-45'
                results['compliance'] = 'Chiller capacity selected'
            elif normalized_id == 'mechanical_boiler_sizing' or workflow_id == 'mechanical_boiler_sizing':
                results['boiler_capacity'] = 100
                results['boiler_model'] = 'B-100'
                results['compliance'] = 'Boiler capacity determined'
        
        return {
            'success': True,
            'results': results,
            'compliance': results.get('compliance', 'Workflow executed successfully'),
            'workflow_id': workflow_id,
            'execution_time': '1.0 seconds'
        }

    @staticmethod
    def get_workflow_details(db: Session, workflow_id: str):
        """Return workflow details with step equations and calculation variables."""
        workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
        if not workflow:
            return None

        steps = sorted(workflow.steps, key=lambda step: step.step_number or 0)
        step_payload = []

        for step in steps:
            equation_obj = None
            if step.equation_id:
                equation_obj = db.query(Equation).filter(Equation.equation_id == step.equation_id).first()

            equation = step.equation or (equation_obj.equation if equation_obj else None)
            variables = []
            calculation_name = equation_obj.name if equation_obj else None

            if equation_obj:
                eq_vars = db.query(EquationInput).filter(EquationInput.equation_id == equation_obj.id).all()
                for var in eq_vars:
                    variables.append({
                        "name": var.name,
                        "symbol": var.symbol,
                        "unit": var.unit,
                        "description": var.description,
                        "data_type": var.data_type,
                        "default_value": var.default_value,
                        "min_value": var.min_value,
                        "max_value": var.max_value,
                        "validation_regex": var.validation_regex,
                        "required": var.required,
                        "input_order": var.input_order
                    })

            step_payload.append({
                "step_number": step.step_number,
                "name": step.name,
                "description": step.description,
                "equation": equation,
                "equation_id": step.equation_id,
                "calculation_name": calculation_name,
                "variables": variables
            })

        input_payload = []
        for input_item in workflow.inputs:
            input_payload.append({
                "name": input_item.name,
                "type": input_item.type,
                "description": input_item.description,
                "required": bool(input_item.required),
                "data_type": input_item.data_type,
                "default_value": input_item.default_value,
                "validation_pattern": input_item.validation_pattern,
                "unit": input_item.unit,
                "display_order": input_item.display_order
            })

        output_payload = []
        for output_item in workflow.outputs:
            output_payload.append({
                "name": output_item.name,
                "type": output_item.type,
                "description": output_item.description
            })

        return {
            "id": workflow.workflow_id,
            "title": workflow.title,
            "description": workflow.description,
            "domain": workflow.domain,
            "inputs": input_payload,
            "outputs": output_payload,
            "steps": step_payload
        }
    
    @staticmethod
    def get_workflows_by_domain(db: Session, domain: str):
        """Get workflows for a specific domain with category hierarchy"""
        domain = domain.lower()
        if domain not in ["electrical", "mechanical", "civil"]:
            return []
        
        workflows = db.query(Workflow).filter(Workflow.domain == domain).all()
        
        # Categorize workflows into subcategories
        categories = {
            "electrical": {
                "load_calculation": [],
                "cable_sizing": [],
                "transformer": [],
                "lighting": [],
                "earthing": [],
                "other": []
            },
            "mechanical": {
                "hvac": [],
                "pump": [],
                "pipe": [],
                "duct": [],
                "chiller": [],
                "other": []
            },
            "civil": {
                "beam": [],
                "column": [],
                "foundation": [],
                "retaining_wall": [],
                "earthworks": [],
                "other": []
            }
        }
        
        for workflow in workflows:
            workflow_title = workflow.title.lower()
            category_assigned = False
            
            for subcategory in categories[domain]:
                if subcategory in workflow_title:
                    categories[domain][subcategory].append({
                        "id": workflow.workflow_id,
                        "title": workflow.title,
                        "description": workflow.description,
                        "inputs": [input.name for input in workflow.inputs],
                        "outputs": [output.name for output in workflow.outputs],
                        "steps": [step.name for step in workflow.steps]
                    })
                    category_assigned = True
                    break
            
            if not category_assigned:
                categories[domain]["other"].append({
                    "id": workflow.workflow_id,
                    "title": workflow.title,
                    "description": workflow.description,
                    "inputs": [input.name for input in workflow.inputs],
                    "outputs": [output.name for output in workflow.outputs],
                    "steps": [step.name for step in workflow.steps]
                })
        
        # Remove empty subcategories
        categories[domain] = {k: v for k, v in categories[domain].items() if v}
        
        return categories[domain]
