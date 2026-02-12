from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from workflow_database import get_workflow_db
from workflow_models import Workflow, WorkflowCategory, WorkflowInput, WorkflowOutput, WorkflowStep
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/workflows", tags=["workflows"])

class WorkflowExecutionRequest(BaseModel):
    inputs: Dict[str, Any]

@router.get("/")
async def get_all_workflows(db: Session = Depends(get_workflow_db)):
    """Get all workflows grouped by domain"""
    # Get all workflows with their steps
    workflows = db.query(Workflow).all()
    
    # Group by domain
    result = {}
    for wf in workflows:
        if wf.domain not in result:
            result[wf.domain] = []
        
        # Get steps for this workflow
        steps = db.query(WorkflowStep).filter_by(workflow_id=wf.id).order_by(WorkflowStep.step_number).all()
        step_names = [step.name for step in steps]
        
        result[wf.domain].append({
            "id": wf.workflow_id,
            "title": wf.title,
            "description": wf.description,
            "category": wf.category.name if wf.category else None,
            "difficulty": wf.difficulty_level,
            "estimated_time": wf.estimated_time,
            "steps": step_names
        })
    
    return result

@router.get("/{domain}")
async def get_workflows_by_domain(domain: str, db: Session = Depends(get_workflow_db)):
    """Get workflows for a specific domain with category hierarchy"""
    domain = domain.lower()
    if domain not in ["electrical", "mechanical", "civil"]:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    # Load workflows from workflow database
    workflows = db.query(Workflow).filter_by(domain=domain).all()
    
    # Categorize workflows into subcategories for better organization
    categories = {
        "electrical": {
            "design": [],
            "analysis": [],
            "protection": [],
            "installation": [],
            "testing": [],
            "other": []
        },
        "mechanical": {
            "design": [],
            "analysis": [],
            "installation": [],
            "maintenance": [],
            "other": []
        },
        "civil": {
            "structural": [],
            "geotechnical": [],
            "construction": [],
            "earthworks": [],
            "other": []
        }
    }
    
    # Categorize workflows
    for wf in workflows:
        # Get steps for this workflow
        steps = db.query(WorkflowStep).filter_by(workflow_id=wf.id).order_by(WorkflowStep.step_number).all()
        step_names = [step.name for step in steps]
        
        wf_data = {
            "id": wf.workflow_id,
            "title": wf.title,
            "description": wf.description,
            "category": wf.category.name if wf.category else None,
            "difficulty": wf.difficulty_level,
            "estimated_time": wf.estimated_time,
            "steps": step_names
        }
        
        wf_name = wf.title.lower()
        category_assigned = False
        
        for subcategory in categories[domain]:
            if subcategory in wf_name:
                categories[domain][subcategory].append(wf_data)
                category_assigned = True
                break
        
        if not category_assigned:
            categories[domain]["other"].append(wf_data)
    
    # Remove empty subcategories
    categories[domain] = {k: v for k, v in categories[domain].items() if v}
    
    return {"domain": domain, "categories": categories[domain]}

@router.get("/{domain}/{subcategory}")
async def get_workflows_by_subcategory(domain: str, subcategory: str, db: Session = Depends(get_db)):
    """Get workflows for a specific domain and subcategory"""
    domain = domain.lower()
    if domain not in ["electrical", "mechanical", "civil"]:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    workflows = WorkflowService.get_workflows_by_domain(db, domain)
    if subcategory not in workflows:
        raise HTTPException(status_code=404, detail="Subcategory not found")
    
    return {"domain": domain, "subcategory": subcategory, "workflows": workflows[subcategory]}

@router.get("/{workflow_id}/details")
async def get_workflow_details(workflow_id: str, db: Session = Depends(get_workflow_db)):
    """Get workflow details including inputs, outputs, and steps."""
    workflow = db.query(Workflow).filter_by(workflow_id=workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Get inputs
    inputs = db.query(WorkflowInput).filter_by(workflow_id=workflow.id).order_by(WorkflowInput.input_order).all()
    
    # Get outputs
    outputs = db.query(WorkflowOutput).filter_by(workflow_id=workflow.id).order_by(WorkflowOutput.output_order).all()
    
    # Get steps
    steps = db.query(WorkflowStep).filter_by(workflow_id=workflow.id).order_by(WorkflowStep.step_number).all()
    
    return {
        "id": workflow.workflow_id,
        "title": workflow.title,
        "description": workflow.description,
        "domain": workflow.domain,
        "category": workflow.category.name if workflow.category else None,
        "difficulty": workflow.difficulty_level,
        "estimated_time": workflow.estimated_time,
        "tags": workflow.tags,
        "inputs": [
            {
                "name": inp.name,
                "type": inp.type,
                "description": inp.description,
                "required": inp.required,
                "default_value": inp.default_value,
                "placeholder": inp.placeholder,
                "help_text": inp.help_text,
                "options": inp.options
            }
            for inp in inputs
        ],
        "outputs": [
            {
                "name": out.name,
                "type": out.type,
                "description": out.description,
                "precision": out.precision
            }
            for out in outputs
        ],
        "steps": [
            {
                "step_number": step.step_number,
                "name": step.name,
                "description": step.description,
                "step_type": step.step_type,
                "equation": step.equation,
                "equation_id": step.equation_id,
                "help_text": step.help_text
            }
            for step in steps
        ]
    }

@router.post("/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, request: WorkflowExecutionRequest, db: Session = Depends(get_workflow_db)):
    """Execute a workflow with given inputs"""
    try:
        # Find the workflow
        workflow = db.query(Workflow).filter_by(workflow_id=workflow_id).first()
        if not workflow:
            raise HTTPException(status_code=404, detail="Workflow not found")
        
        # Simulate workflow execution
        result = WorkflowService.execute_workflow(workflow_id, request.inputs)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
