"""
Calculation Pipeline API Routes
FastAPI routes for the calculation pipeline system.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from workflow_database import get_workflow_db
from calculation_pipeline.engine import CalculationEngine, StandardsEngine
from calculation_pipeline.models import (
    CalculationPipeline,
    CalculationStep,
    CalculationExecution,
    StepExecution,
    EngineeringStandard,
    StandardCoefficient
)
from pydantic import BaseModel
from typing import Dict, Any, List, Optional


router = APIRouter(prefix="/calculation-pipelines", tags=["calculation-pipelines"])


# Request/Response Models
class PipelineExecutionRequest(BaseModel):
    """Request model for pipeline execution"""
    inputs: Dict[str, Any]


class PipelineExecutionResponse(BaseModel):
    """Response model for pipeline execution"""
    success: bool
    execution_id: str
    results: Dict[str, Any]
    status: str
    execution_time: str
    steps: List[Dict[str, Any]]


class PipelineListResponse(BaseModel):
    """Response model for pipeline list"""
    id: str
    name: str
    description: str
    domain: str
    standard: Optional[str]
    step_count: int


class PipelineDetailsResponse(BaseModel):
    """Response model for pipeline details"""
    id: str
    name: str
    description: str
    domain: str
    standard: Optional[Dict[str, Any]]
    steps: List[Dict[str, Any]]
    dependencies: List[Dict[str, Any]]


class ExecutionHistoryResponse(BaseModel):
    """Response model for execution history"""
    execution_id: str
    status: str
    start_time: str
    end_time: str
    execution_time: float
    step_count: int


# Helper functions
def format_pipeline_list(db: Session, pipeline: CalculationPipeline) -> Dict[str, Any]:
    """Format pipeline for list response"""
    standard_name = None
    if pipeline.standard:
        standard_name = pipeline.standard.name
    
    step_count = db.query(CalculationStep).filter(
        CalculationStep.pipeline_id == pipeline.id,
        CalculationStep.is_active == True
    ).count()
    
    return {
        "id": pipeline.pipeline_id,
        "name": pipeline.name,
        "description": pipeline.description,
        "domain": pipeline.domain,
        "standard": standard_name,
        "step_count": step_count
    }


def format_pipeline_details(db: Session, pipeline: CalculationPipeline) -> Dict[str, Any]:
    """Format pipeline for details response"""
    standard_info = None
    if pipeline.standard:
        standard_info = {
            "code": pipeline.standard.standard_code,
            "name": pipeline.standard.name
        }
    
    # Get steps
    steps = db.query(CalculationStep).filter(
        CalculationStep.pipeline_id == pipeline.id,
        CalculationStep.is_active == True
    ).order_by(CalculationStep.step_number).all()
    
    step_list = []
    for step in steps:
        step_list.append({
            "id": step.step_id,
            "step_number": step.step_number,
            "name": step.name,
            "description": step.description,
            "calculation_type": step.calculation_type,
            "formula": step.formula,
            "input_config": step.input_config,
            "output_config": step.output_config,
            "validation_config": step.validation_config
        })
    
    # Get dependencies
    dependencies = db.query(CalculationDependency).filter(
        CalculationDependency.pipeline_id == pipeline.id
    ).all()
    
    dependency_list = []
    for dep in dependencies:
        from_step = db.query(CalculationStep).filter(
            CalculationStep.id == dep.depends_on_step_id
        ).first()
        to_step = db.query(CalculationStep).filter(
            CalculationStep.id == dep.step_id
        ).first()
        
        dependency_list.append({
            "step_id": to_step.step_id if to_step else None,
            "depends_on_step_id": from_step.step_id if from_step else None,
            "input_mapping": dep.input_mapping
        })
    
    return {
        "id": pipeline.pipeline_id,
        "name": pipeline.name,
        "description": pipeline.description,
        "domain": pipeline.domain,
        "standard": standard_info,
        "steps": step_list,
        "dependencies": dependency_list
    }


# API Routes

@router.get("/")
async def get_all_pipelines(
    domain: Optional[str] = None,
    db: Session = Depends(get_workflow_db)
):
    """Get all calculation pipelines"""
    query = db.query(CalculationPipeline).filter(CalculationPipeline.is_active == True)
    
    if domain:
        query = query.filter(CalculationPipeline.domain == domain)
    
    pipelines = query.all()
    
    return {
        "pipelines": [format_pipeline_list(db, pipeline) for pipeline in pipelines]
    }


@router.get("/domains")
async def get_available_domains(db: Session = Depends(get_workflow_db)):
    """Get available domains for calculation pipelines"""
    domains = db.query(CalculationPipeline.domain).distinct().all()
    return {
        "domains": [domain[0] for domain in domains]
    }


@router.get("/standards")
async def get_engineering_standards(
    domain: Optional[str] = None,
    db: Session = Depends(get_workflow_db)
):
    """Get available engineering standards"""
    query = db.query(EngineeringStandard).filter(EngineeringStandard.is_active == True)
    
    if domain:
        query = query.filter(EngineeringStandard.domain == domain)
    
    standards = query.all()
    
    return {
        "standards": [{
            "code": std.standard_code,
            "name": std.name,
            "type": std.standard_type,
            "domain": std.domain
        } for std in standards]
    }


@router.get("/{pipeline_id}")
async def get_pipeline_details(
    pipeline_id: str,
    db: Session = Depends(get_workflow_db)
):
    """Get details of a specific calculation pipeline"""
    pipeline = db.query(CalculationPipeline).filter(
        CalculationPipeline.pipeline_id == pipeline_id,
        CalculationPipeline.is_active == True
    ).first()
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    return format_pipeline_details(db, pipeline)


@router.get("/{pipeline_id}/steps")
async def get_pipeline_steps(
    pipeline_id: str,
    db: Session = Depends(get_workflow_db)
):
    """Get steps of a specific calculation pipeline"""
    pipeline = db.query(CalculationPipeline).filter(
        CalculationPipeline.pipeline_id == pipeline_id,
        CalculationPipeline.is_active == True
    ).first()
    
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    steps = db.query(CalculationStep).filter(
        CalculationStep.pipeline_id == pipeline.id,
        CalculationStep.is_active == True
    ).order_by(CalculationStep.step_number).all()
    
    return {
        "steps": [{
            "id": step.step_id,
            "step_number": step.step_number,
            "name": step.name,
            "description": step.description,
            "calculation_type": step.calculation_type,
            "formula": step.formula,
            "input_config": step.input_config,
            "output_config": step.output_config,
            "validation_config": step.validation_config
        } for step in steps]
    }


@router.post("/{pipeline_id}/execute")
async def execute_pipeline(
    pipeline_id: str,
    request: PipelineExecutionRequest,
    db: Session = Depends(get_workflow_db)
):
    """Execute a calculation pipeline"""
    try:
        engine = CalculationEngine(db)
        result = engine.execute_pipeline(pipeline_id, request.inputs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pipeline_id}/execution-history")
async def get_pipeline_execution_history(
    pipeline_id: str,
    limit: int = 20,
    db: Session = Depends(get_workflow_db)
):
    """Get execution history of a pipeline"""
    try:
        engine = CalculationEngine(db)
        history = engine.get_execution_history(pipeline_id, limit)
        
        return {
            "execution_history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/executions/{execution_id}")
async def get_execution_details(
    execution_id: str,
    db: Session = Depends(get_workflow_db)
):
    """Get details of a specific execution"""
    execution = db.query(CalculationExecution).filter(
        CalculationExecution.execution_id == execution_id
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    
    # Get step executions
    step_executions = db.query(StepExecution).filter(
        StepExecution.execution_id == execution.id
    ).all()
    
    return {
        "execution_id": execution.execution_id,
        "status": execution.status,
        "start_time": execution.start_time,
        "end_time": execution.end_time,
        "execution_time": execution.execution_time,
        "inputs": execution.input_data,
        "results": execution.output_data,
        "step_count": len(step_executions),
        "steps": [{
            "step_id": step_execution.step.step_id,
            "name": step_execution.step.name,
            "status": step_execution.status,
            "input_data": step_execution.input_data,
            "output_data": step_execution.output_data,
            "execution_time": step_execution.execution_time,
            "validation_passed": step_execution.validation_passed,
            "validation_errors": step_execution.validation_errors
        } for step_execution in step_executions]
    }


@router.get("/standards/{standard_code}/coefficients")
async def get_standard_coefficients(
    standard_code: str,
    db: Session = Depends(get_workflow_db)
):
    """Get coefficients for a specific standard"""
    standard = db.query(EngineeringStandard).filter(
        EngineeringStandard.standard_code == standard_code
    ).first()
    
    if not standard:
        raise HTTPException(status_code=404, detail="Standard not found")
    
    coefficients = db.query(StandardCoefficient).filter(
        StandardCoefficient.standard_id == standard.id
    ).all()
    
    return {
        "standard": {
            "code": standard.standard_code,
            "name": standard.name
        },
        "coefficients": [{
            "name": coeff.coefficient_name,
            "type": coeff.coefficient_type,
            "data_source": coeff.data_source,
            "table": coeff.coefficient_table,
            "formula": coeff.formula
        } for coeff in coefficients]
    }


@router.get("/standards/{standard_code}/coefficients/{coefficient_name}")
async def get_standard_coefficient(
    standard_code: str,
    coefficient_name: str,
    params: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_workflow_db)
):
    """Get a specific coefficient from a standard"""
    try:
        engine = StandardsEngine(db)
        coefficient = engine.get_coefficient(standard_code, coefficient_name, params or {})
        
        if coefficient is None:
            raise HTTPException(status_code=404, detail="Coefficient not found")
        
        return {
            "standard_code": standard_code,
            "coefficient_name": coefficient_name,
            "value": coefficient,
            "parameters": params
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_pipeline_statistics(db: Session = Depends(get_workflow_db)):
    """Get system-wide pipeline statistics"""
    total_pipelines = db.query(CalculationPipeline).filter(
        CalculationPipeline.is_active == True
    ).count()
    
    total_steps = db.query(CalculationStep).filter(
        CalculationStep.is_active == True
    ).count()
    
    total_executions = db.query(CalculationExecution).count()
    
    completed_executions = db.query(CalculationExecution).filter(
        CalculationExecution.status == "completed"
    ).count()
    
    failed_executions = db.query(CalculationExecution).filter(
        CalculationExecution.status == "failed"
    ).count()
    
    domain_counts = db.query(
        CalculationPipeline.domain,
        db.func.count(CalculationPipeline.id)
    ).filter(CalculationPipeline.is_active == True).group_by(CalculationPipeline.domain).all()
    
    return {
        "total_pipelines": total_pipelines,
        "total_steps": total_steps,
        "total_executions": total_executions,
        "completed_executions": completed_executions,
        "failed_executions": failed_executions,
        "pipelines_by_domain": {domain: count for domain, count in domain_counts}
    }
