import json
import os
from sqlalchemy.orm import Session
from calculators.models import Calculation, CalculationVariable, CalculationCategory

class CalculationService:
    @staticmethod
    def load_calculations_from_json(db: Session):
        """Load calculations from shared/data/calculations.json and populate the database"""
        # Check if we already have calculations
        if db.query(Calculation).count() > 0:
            return
        
        # Load calculations from JSON file
        # Check if we're running from the correct directory
        current_dir = os.path.dirname(__file__)
        project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
        json_path = os.path.join(project_root, "..", "shared", "data", "calculations.json")
        
        # Verify the file exists
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"Calculations file not found at: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Create categories and subcategories
        categories = {}
        for calc in data['calculations']:
            domain = calc['domain']
            # Create domain category
            if domain not in categories:
                category = CalculationCategory(
                    name=domain.capitalize(),
                    domain=domain,
                    subcategory=None
                )
                db.add(category)
                db.commit()
                db.refresh(category)
                categories[domain] = category
        
        # Create calculations and variables
        for calc in data['calculations']:
            calculation = Calculation(
                calculation_id=calc['id'],
                name=calc['name'],
                equation=calc['equation'],
                domain=calc['domain'],
                category_id=categories[calc['domain']].id
            )
            db.add(calculation)
            db.commit()
            db.refresh(calculation)
            
            # Create variables
            for var in calc['variables']:
                variable = CalculationVariable(
                    calculation_id=calculation.id,
                    name=var['name'],
                    symbol=var['symbol'],
                    unit=var.get('unit'),
                    description=var.get('description')
                )
                db.add(variable)
        
        db.commit()
    
    @staticmethod
    def get_all_calculations(db: Session):
        """Get all calculations grouped by domain and subcategory"""
        calculations = db.query(Calculation).all()
        result = {
            "electrical": [],
            "mechanical": [],
            "civil": []
        }
        
        for calc in calculations:
            result[calc.domain].append({
                "id": calc.calculation_id,
                "name": calc.name,
                "equation": calc.equation,
                "variables": [{
                    "name": v.name,
                    "symbol": v.symbol,
                    "unit": v.unit,
                    "description": v.description
                } for v in calc.variables]
            })
        
        return result
    
    @staticmethod
    def get_calculations_by_domain(db: Session, domain: str):
        """Get calculations for a specific domain"""
        calculations = db.query(Calculation).filter(Calculation.domain == domain.lower()).all()
        return [{
            "id": calc.calculation_id,
            "name": calc.name,
            "equation": calc.equation,
            "variables": [{
                "name": v.name,
                "symbol": v.symbol,
                "unit": v.unit,
                "description": v.description
            } for v in calc.variables]
        } for calc in calculations]
