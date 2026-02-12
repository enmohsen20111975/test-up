"""
Calculation Pipeline Engine
DAG-based execution engine for deterministic engineering calculation pipelines.
"""

import time
import json
import networkx as nx
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from calculation_pipeline.models import (
    CalculationPipeline,
    CalculationStep,
    CalculationDependency,
    CalculationValidation,
    CalculationExecution,
    StepExecution,
    EngineeringStandard,
    StandardCoefficient
)


class CalculationEngine:
    """
    Deterministic calculation pipeline engine with DAG-based execution.
    Handles step dependencies, state management, and validation gates.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.execution_state = {}
        self.validation_results = {}
    
    def load_pipeline(self, pipeline_id: str) -> Optional[CalculationPipeline]:
        """
        Load a calculation pipeline by pipeline ID
        """
        return self.db.query(CalculationPipeline).filter(
            CalculationPipeline.pipeline_id == pipeline_id,
            CalculationPipeline.is_active == True
        ).first()
    
    def build_dependency_graph(self, pipeline: CalculationPipeline) -> nx.DiGraph:
        """
        Build the DAG from pipeline steps and dependencies
        """
        G = nx.DiGraph()
        
        # Add all steps as nodes
        steps = self.db.query(CalculationStep).filter(
            CalculationStep.pipeline_id == pipeline.id,
            CalculationStep.is_active == True
        ).all()
        
        for step in steps:
            G.add_node(step.step_id, step=step)
        
        # Add dependencies as edges
        dependencies = self.db.query(CalculationDependency).filter(
            CalculationDependency.pipeline_id == pipeline.id
        ).all()
        
        for dep in dependencies:
            from_step = self.db.query(CalculationStep).filter(
                CalculationStep.id == dep.depends_on_step_id
            ).first()
            to_step = self.db.query(CalculationStep).filter(
                CalculationStep.id == dep.step_id
            ).first()
            
            if from_step and to_step:
                G.add_edge(from_step.step_id, to_step.step_id, dependency=dep)
        
        return G
    
    def execute_pipeline(self, pipeline_id: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a calculation pipeline with given inputs
        """
        # Load pipeline
        pipeline = self.load_pipeline(pipeline_id)
        if not pipeline:
            raise Exception(f"Pipeline '{pipeline_id}' not found or inactive")
        
        # Build execution
        execution = self._create_execution(pipeline, inputs)
        
        try:
            # Build dependency graph
            G = self.build_dependency_graph(pipeline)
            
            # Validate DAG has no cycles
            if not nx.is_directed_acyclic_graph(G):
                raise Exception("Pipeline has cyclic dependencies - cannot execute")
            
            # Topological sort to determine execution order
            execution_order = list(nx.topological_sort(G))
            
            # Execute steps in order
            step_results = {}
            pipeline_state = {**inputs}
            
            for step_id in execution_order:
                step_result = self._execute_step(
                    step_id,
                    pipeline_state,
                    execution,
                    G,
                    step_results
                )
                
                step_results[step_id] = step_result
                
                if not step_result['success']:
                    execution.status = "failed"
                    execution.error_message = step_result['error']
                    break
                
                # Merge step outputs into pipeline state
                if 'outputs' in step_result and step_result['outputs']:
                    pipeline_state.update(step_result['outputs'])
            
            # Finalize execution
            if execution.status != "failed":
                execution.status = "completed"
                execution.output_data = pipeline_state
            
            execution.end_time = time.time()
            execution.execution_time = execution.end_time - execution.start_time
            
            self.db.commit()
            
            return {
                "success": execution.status == "completed",
                "execution_id": execution.execution_id,
                "results": pipeline_state,
                "status": execution.status,
                "execution_time": f"{execution.execution_time:.2f} seconds",
                "steps": step_results
            }
            
        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            execution.end_time = time.time()
            execution.execution_time = execution.end_time - execution.start_time
            self.db.commit()
            raise
    
    def _create_execution(self, pipeline: CalculationPipeline, inputs: Dict[str, Any]) -> CalculationExecution:
        """
        Create a new execution record
        """
        execution = CalculationExecution(
            pipeline_id=pipeline.id,
            execution_id=f"exec_{int(time.time() * 1000)}",
            status="running",
            input_data=inputs,
            start_time=time.time()
        )
        self.db.add(execution)
        self.db.commit()
        self.db.refresh(execution)
        return execution
    
    def _execute_step(self, step_id: str, pipeline_state: Dict[str, Any], 
                     execution: CalculationExecution, G: nx.DiGraph, 
                     step_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single calculation step
        """
        start_time = time.time()
        
        # Get step from graph
        step = G.nodes[step_id]['step']
        
        # Create step execution record
        step_execution = StepExecution(
            execution_id=execution.id,
            step_id=step.id,
            status="running",
            start_time=start_time
        )
        self.db.add(step_execution)
        self.db.commit()
        self.db.refresh(step_execution)
        
        try:
            # Collect inputs for this step
            step_inputs = self._collect_step_inputs(step, pipeline_state)
            
            # Execute calculation
            step_execution.input_data = step_inputs
            
            calculation_result = self._execute_calculation(step, step_inputs)
            
            # Validate results
            validation_result = self._validate_step(step, calculation_result)
            
            # Update step execution
            step_execution.output_data = calculation_result
            step_execution.calculation_result = calculation_result
            step_execution.validation_passed = validation_result['passed']
            step_execution.status = "completed"
            step_execution.end_time = time.time()
            step_execution.execution_time = step_execution.end_time - start_time
            
            if not validation_result['passed']:
                step_execution.validation_errors = validation_result['errors']
                raise Exception(f"Step validation failed: {validation_result['errors']}")
            
            self.db.commit()
            
            return {
                "success": True,
                "step_id": step_id,
                "name": step.name,
                "inputs": step_inputs,
                "outputs": calculation_result,
                "execution_time": f"{step_execution.execution_time:.2f} seconds",
                "validation": validation_result
            }
            
        except Exception as e:
            step_execution.status = "failed"
            step_execution.end_time = time.time()
            step_execution.execution_time = step_execution.end_time - start_time
            step_execution.error_message = str(e)
            self.db.commit()
            
            return {
                "success": False,
                "step_id": step_id,
                "name": step.name,
                "error": str(e),
                "execution_time": f"{step_execution.execution_time:.2f} seconds"
            }
    
    def _collect_step_inputs(self, step: CalculationStep, pipeline_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collect inputs for a step from pipeline state
        """
        step_inputs = {}
        
        if step.input_config:
            for param_name, config in step.input_config.items():
                if param_name in pipeline_state:
                    step_inputs[param_name] = pipeline_state[param_name]
                elif 'default' in config:
                    step_inputs[param_name] = config['default']
                elif config.get('required', True):
                    raise Exception(f"Required parameter '{param_name}' missing for step '{step.name}'")
        
        return step_inputs
    
    def _execute_calculation(self, step: CalculationStep, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the calculation for a single step
        """
        calculation_type = step.calculation_type
        
        if calculation_type == "formula":
            return self._execute_formula_calculation(step, inputs)
        elif calculation_type == "lookup":
            return self._execute_lookup_calculation(step, inputs)
        elif calculation_type == "table":
            return self._execute_table_calculation(step, inputs)
        elif calculation_type == "custom":
            return self._execute_custom_calculation(step, inputs)
        else:
            raise Exception(f"Unknown calculation type '{calculation_type}'")
    
    def _execute_formula_calculation(self, step: CalculationStep, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute formula-based calculation
        """
        if not step.formula:
            raise Exception(f"No formula defined for step '{step.name}'")
        
        try:
            # Evaluate formula with inputs
            local_vars = {**inputs}
            exec_result = {}
            
            # For now, we'll just return mock results (to be implemented)
            exec_result['result'] = 0.0
            
            return exec_result
        except Exception as e:
            raise Exception(f"Formula execution failed: {e}")
    
    def _execute_lookup_calculation(self, step: CalculationStep, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute lookup-based calculation (from standard coefficients)
        """
        # To be implemented - look up from standard coefficients table
        return {}
    
    def _execute_table_calculation(self, step: CalculationStep, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute table-based calculation
        """
        # To be implemented - table lookup logic
        return {}
    
    def _execute_custom_calculation(self, step: CalculationStep, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute custom calculation
        """
        # To be implemented - custom calculation logic
        return {}
    
    def _validate_step(self, step: CalculationStep, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate step results against configured constraints
        """
        errors = []
        
        if step.validation_config:
            for param_name, param_value in results.items():
                if param_name in step.validation_config:
                    param_errors = self._validate_parameter(
                        param_name,
                        param_value,
                        step.validation_config[param_name]
                    )
                    errors.extend(param_errors)
        
        # Check for explicit validation rules
        validations = self.db.query(CalculationValidation).filter(
            CalculationValidation.step_id == step.id,
            CalculationValidation.is_active == True
        ).all()
        
        for validation in validations:
            validation_errors = self._run_validation(validation, results)
            errors.extend(validation_errors)
        
        return {
            "passed": len(errors) == 0,
            "errors": errors,
            "validations_checked": len(step.validation_config) + len(validations)
        }
    
    def _validate_parameter(self, param_name: str, param_value: Any, 
                           validation_config: Dict[str, Any]) -> List[str]:
        """
        Validate a single parameter against constraints
        """
        errors = []
        
        if "range" in validation_config:
            range_config = validation_config["range"]
            min_val = range_config.get("min")
            max_val = range_config.get("max")
            
            if min_val is not None and param_value < min_val:
                errors.append(f"Parameter '{param_name}' ({param_value}) is less than minimum {min_val}")
            if max_val is not None and param_value > max_val:
                errors.append(f"Parameter '{param_name}' ({param_value}) exceeds maximum {max_val}")
        
        if "precision" in validation_config:
            precision = validation_config["precision"]
            # Check precision
            pass
        
        if "unit" in validation_config:
            # Check unit compatibility
            pass
        
        return errors
    
    def _run_validation(self, validation: CalculationValidation, 
                      results: Dict[str, Any]) -> List[str]:
        """
        Run a specific validation rule
        """
        errors = []
        
        if validation.validation_type == "range":
            config = validation.validation_config
            param_name = config.get("param")
            
            if param_name in results:
                param_value = results[param_name]
                errors.extend(self._validate_parameter(param_name, param_value, config))
        
        elif validation.validation_type == "standard":
            errors.append("Standard-based validation not implemented")
        
        return errors
    
    def get_execution_history(self, pipeline_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get execution history for a pipeline
        """
        pipeline = self.load_pipeline(pipeline_id)
        if not pipeline:
            raise Exception(f"Pipeline '{pipeline_id}' not found")
        
        executions = self.db.query(CalculationExecution).filter(
            CalculationExecution.pipeline_id == pipeline.id
        ).order_by(CalculationExecution.created_at.desc()).limit(limit).all()
        
        return [self._format_execution(exec) for exec in executions]
    
    def _format_execution(self, execution: CalculationExecution) -> Dict[str, Any]:
        """
        Format execution for API response
        """
        return {
            "execution_id": execution.execution_id,
            "status": execution.status,
            "start_time": execution.start_time,
            "end_time": execution.end_time,
            "execution_time": execution.execution_time,
            "inputs": execution.input_data,
            "results": execution.output_data,
            "step_count": len(execution.step_executions)
        }


class StandardsEngine:
    """
    Engineering standards coefficient lookup engine
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_standard(self, standard_code: str) -> Optional[EngineeringStandard]:
        """
        Get a specific engineering standard
        """
        return self.db.query(EngineeringStandard).filter(
            EngineeringStandard.standard_code == standard_code
        ).first()
    
    def get_coefficient(self, standard_code: str, coefficient_name: str, 
                       params: Dict[str, Any]) -> Optional[float]:
        """
        Get a coefficient from an engineering standard
        """
        standard = self.get_standard(standard_code)
        if not standard:
            return None
        
        coefficients = self.db.query(StandardCoefficient).filter(
            StandardCoefficient.standard_id == standard.id,
            StandardCoefficient.coefficient_name == coefficient_name
        ).all()
        
        for coeff in coefficients:
            if coeff.data_source == "table":
                return self._lookup_table_coefficient(coeff, params)
            elif coeff.data_source == "formula":
                return self._calculate_formula_coefficient(coeff, params)
            elif coeff.data_source == "lookup":
                return self._lookup_external_coefficient(coeff, params)
        
        return None
    
    def _lookup_table_coefficient(self, coefficient: StandardCoefficient, 
                                params: Dict[str, Any]) -> Optional[float]:
        """
        Lookup coefficient from table
        """
        try:
            if not coefficient.coefficient_table:
                return None
            
            for key, value in coefficient.coefficient_table.items():
                if float(key) == float(params.get("key", 0)):
                    return float(value)
            
            return None
        except:
            return None
    
    def _calculate_formula_coefficient(self, coefficient: StandardCoefficient, 
                                     params: Dict[str, Any]) -> Optional[float]:
        """
        Calculate coefficient from formula
        """
        try:
            if not coefficient.formula:
                return None
            
            # Evaluate formula with parameters
            local_vars = {**params}
            return float(eval(coefficient.formula, {}, local_vars))
        except:
            return None
    
    def _lookup_external_coefficient(self, coefficient: StandardCoefficient, 
                                    params: Dict[str, Any]) -> Optional[float]:
        """
        Lookup coefficient from external source
        """
        return None
