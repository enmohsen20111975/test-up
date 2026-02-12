from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from workflow_database import get_workflow_db
from auth.router import get_current_user
from auth.models import User
from calculators.services.electrical import ElectricalCalculators
from calculators.services.mechanical import MechanicalCalculators
from calculators.services.civil import CivilCalculators
from workflow_models import Equation, EquationCategory, EquationInput, EquationOutput
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

router = APIRouter(prefix="/calculators", tags=["calculators"])

class CalculationRequest(BaseModel):
    inputs: Dict[str, Any]

@router.get("/")
async def get_all_calculations(db: Session = Depends(get_workflow_db)):
    """Get all equations grouped by domain"""
    # Get all equations with their categories
    equations = db.query(Equation).all()
    
    # Group by domain
    result = {}
    for eq in equations:
        if eq.domain not in result:
            result[eq.domain] = []
        
        result[eq.domain].append({
            "id": eq.equation_id,
            "name": eq.name,
            "description": eq.description,
            "equation": eq.equation,
            "category": eq.category.name if eq.category else None,
            "difficulty": eq.difficulty_level
        })
    
    return result

@router.get("/{domain}")
async def get_calculators_by_domain(domain: str, db: Session = Depends(get_workflow_db)):
    """Get equations for a specific domain with category hierarchy"""
    domain = domain.lower()
    if domain not in ["electrical", "mechanical", "civil"]:
        raise HTTPException(status_code=404, detail="Discipline not found")
    
    # Load equations from workflow database
    equations = db.query(Equation).filter_by(domain=domain).all()
    
    # Categorize equations into subcategories for better organization
    categories = {
        "electrical": {
            "3phase": [],
            "cable": [],
            "transformer": [],
            "voltage_drop": [],
            "short_circuit": [],
            "power_factor": [],
            "motor": [],
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
            "heat_transfer": [],
            "compressor": [],
            "psychrometrics": [],
            "other": []
        },
        "civil": {
            "beam": [],
            "column": [],
            "foundation": [],
            "retaining_wall": [],
            "earthworks": [],
            "concrete": [],
            "steel": [],
            "other": []
        }
    }
    
    # Categorize equations
    for eq in equations:
        calc_data = {
            "id": eq.equation_id,
            "name": eq.name,
            "description": eq.description,
            "equation": eq.equation,
            "category": eq.category.name if eq.category else None,
            "difficulty": eq.difficulty_level
        }
        
        calc_name = eq.name.lower()
        category_assigned = False
        
        for subcategory in categories[domain]:
            if subcategory in calc_name:
                categories[domain][subcategory].append(calc_data)
                category_assigned = True
                break
        
        if not category_assigned:
            categories[domain]["other"].append(calc_data)
    
    # Remove empty subcategories
    categories[domain] = {k: v for k, v in categories[domain].items() if v}
    
    return {"domain": domain, "categories": categories[domain]}

@router.get("/equation/{equation_id}")
async def get_equation_details(equation_id: str, db: Session = Depends(get_workflow_db)):
    """Get detailed information about a specific equation including inputs and outputs"""
    equation = db.query(Equation).filter_by(equation_id=equation_id).first()
    
    if not equation:
        raise HTTPException(status_code=404, detail="Equation not found")
    
    # Get inputs
    inputs = db.query(EquationInput).filter_by(equation_id=equation.id).order_by(EquationInput.input_order).all()
    
    # Get outputs
    outputs = db.query(EquationOutput).filter_by(equation_id=equation.id).order_by(EquationOutput.output_order).all()
    
    return {
        "id": equation.equation_id,
        "name": equation.name,
        "description": equation.description,
        "equation": equation.equation,
        "equation_latex": equation.equation_latex,
        "domain": equation.domain,
        "category": equation.category.name if equation.category else None,
        "difficulty": equation.difficulty_level,
        "tags": equation.tags,
        "inputs": [
            {
                "name": inp.name,
                "symbol": inp.symbol,
                "description": inp.description,
                "data_type": inp.data_type,
                "unit": inp.unit,
                "unit_category": inp.unit_category,
                "required": inp.required,
                "default_value": inp.default_value,
                "min_value": inp.min_value,
                "max_value": inp.max_value,
                "placeholder": inp.placeholder,
                "help_text": inp.help_text
            }
            for inp in inputs
        ],
        "outputs": [
            {
                "name": out.name,
                "symbol": out.symbol,
                "description": out.description,
                "data_type": out.data_type,
                "unit": out.unit,
                "unit_category": out.unit_category,
                "precision": out.precision
            }
            for out in outputs
        ]
    }


@router.post("/{type}/calculate")
async def calculate(
    type: str,
    request: CalculationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        if type.startswith("electrical_"):
            method_name = type.replace("electrical_", "")
            if hasattr(ElectricalCalculators, method_name):
                method = getattr(ElectricalCalculators, method_name)
                result = method(**request.inputs)
                return result
        elif type.startswith("mechanical_"):
            method_name = type.replace("mechanical_", "")
            if hasattr(MechanicalCalculators, method_name):
                method = getattr(MechanicalCalculators, method_name)
                result = method(**request.inputs)
                return result
        elif type.startswith("civil_"):
            method_name = type.replace("civil_", "")
            if hasattr(CivilCalculators, method_name):
                method = getattr(CivilCalculators, method_name)
                result = method(**request.inputs)
                return result
        
        raise HTTPException(status_code=404, detail="Calculator type not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))