"""
Calculation Pipeline Migration
Migrates existing fixed data from Python files to the new database schema.
Converts workflow patterns into calculation pipeline definitions.
"""

import json
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow_database import workflow_engine, WorkflowBase, get_workflow_db
from calculation_pipeline.models import (
    EngineeringStandard,
    StandardCoefficient,
    CalculationPipeline,
    CalculationStep,
    CalculationDependency,
    CalculationValidation
)


def create_engineering_standards(db):
    """Create engineering standards records"""
    standards = [
        {
            "standard_code": "IEC_60364_5_52",
            "name": "IEC 60364-5-52: Low-voltage electrical installations",
            "description": "Selection and erection of electrical equipment - Wiring systems",
            "standard_type": "cable_sizing",
            "domain": "electrical"
        },
        {
            "standard_code": "NEC_2023",
            "name": "National Electrical Code 2023",
            "description": "United States electrical installation standards",
            "standard_type": "all",
            "domain": "electrical"
        },
        {
            "standard_code": "IEEE_1584",
            "name": "IEEE 1584: Arc Flash Calculations",
            "description": "Guide for performing arc-flash hazard calculations",
            "standard_type": "arc_flash",
            "domain": "electrical"
        },
        {
            "standard_code": "ASHRAE_90.1",
            "name": "ASHRAE 90.1: Energy Standard for Buildings",
            "description": "Energy efficiency standards for buildings",
            "standard_type": "hvac",
            "domain": "mechanical"
        },
        {
            "standard_code": "AISC_360",
            "name": "AISC 360: Steel Construction Manual",
            "description": "Specification for structural steel buildings",
            "standard_type": "structural",
            "domain": "civil"
        },
        {
            "standard_code": "ACI_318",
            "name": "ACI 318: Building Code Requirements for Structural Concrete",
            "description": "Concrete design standard",
            "standard_type": "structural",
            "domain": "civil"
        }
    ]
    
    for std_data in standards:
        existing = db.query(EngineeringStandard).filter(
            EngineeringStandard.standard_code == std_data["standard_code"]
        ).first()
        
        if not existing:
            standard = EngineeringStandard(**std_data)
            db.add(standard)
    
    db.commit()
    print(f"Created {len(standards)} engineering standards")


def create_standard_coefficients(db):
    """Create standard coefficient lookup tables"""
    # Temperature derating factors for cables (IEC 60364-5-52)
    temperature_derating = {
        "25": 1.0,
        "30": 0.95,
        "35": 0.9,
        "40": 0.87,
        "45": 0.82,
        "50": 0.76,
        "55": 0.71,
        "60": 0.65,
        "65": 0.60,
        "70": 0.55
    }
    
    # Cable grouping factors
    grouping_factors = {
        "2": 0.8,
        "3": 0.7,
        "4": 0.65,
        "5": 0.6,
        "6": 0.57,
        "7": 0.54,
        "8": 0.52,
        "9": 0.5,
        "10": 0.48
    }
    
    coefficients = [
        {
            "coefficient_name": "temperature_derating",
            "coefficient_type": "derating",
            "data_source": "table",
            "coefficient_table": temperature_derating,
            "standard_code": "IEC_60364_5_52"
        },
        {
            "coefficient_name": "grouping_factor",
            "coefficient_type": "grouping",
            "data_source": "table",
            "coefficient_table": grouping_factors,
            "standard_code": "IEC_60364_5_52"
        }
    ]
    
    for coeff_data in coefficients:
        standard = db.query(EngineeringStandard).filter(
            EngineeringStandard.standard_code == coeff_data["standard_code"]
        ).first()
        
        if standard:
            existing = db.query(StandardCoefficient).filter(
                StandardCoefficient.standard_id == standard.id,
                StandardCoefficient.coefficient_name == coeff_data["coefficient_name"]
            ).first()
            
            if not existing:
                coeff = StandardCoefficient(
                    standard_id=standard.id,
                    coefficient_name=coeff_data["coefficient_name"],
                    coefficient_type=coeff_data["coefficient_type"],
                    data_source=coeff_data["data_source"],
                    coefficient_table=coeff_data["coefficient_table"]
                )
                db.add(coeff)
    
    db.commit()
    print(f"Created {len(coefficients)} standard coefficients")


def load_existing_workflow_data():
    """Load existing workflow data from Python files"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
    
    # Load create_workflow_config.py
    config_path = os.path.join(project_root, "backend", "create_workflow_config.py")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config_content = f.read()
    
    # Extract DEFAULT_WORKFLOW_PATTERNS
    import ast
    tree = ast.parse(config_content)
    
    default_patterns = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "DEFAULT_WORKFLOW_PATTERNS":
                    try:
                        default_patterns = ast.literal_eval(node.value)
                    except:
                        pass
                    break
    
    return default_patterns


def migrate_workflows_to_pipelines(db, workflow_patterns):
    """Migrate existing workflow patterns to calculation pipelines"""
    if not workflow_patterns:
        print("No workflow patterns to migrate")
        return
    
    pipelines_created = 0
    steps_created = 0
    dependencies_created = 0
    
    # Get default standards
    electrical_standard = db.query(EngineeringStandard).filter(
        EngineeringStandard.standard_code == "IEC_60364_5_52"
    ).first()
    
    mechanical_standard = db.query(EngineeringStandard).filter(
        EngineeringStandard.standard_code == "ASHRAE_90.1"
    ).first()
    
    civil_standard = db.query(EngineeringStandard).filter(
        EngineeringStandard.standard_code == "AISC_360"
    ).first()
    
    domain_standards = {
        "electrical": electrical_standard,
        "mechanical": mechanical_standard,
        "civil": civil_standard
    }
    
    # Process each domain
    for domain, patterns in workflow_patterns.items():
        standard = domain_standards.get(domain)
        
        for pattern_name, pattern_data in patterns.items():
            # Create pipeline
            pipeline_id = f"{domain}_{pattern_name}"
            existing = db.query(CalculationPipeline).filter(
                CalculationPipeline.pipeline_id == pipeline_id
            ).first()
            
            if not existing:
                pipeline = CalculationPipeline(
                    pipeline_id=pipeline_id,
                    name=pattern_name.replace('_', ' ').capitalize(),
                    description=pattern_data["description"],
                    domain=domain,
                    standard_id=standard.id if standard else None
                )
                db.add(pipeline)
                db.commit()
                db.refresh(pipeline)
                
                pipelines_created += 1
                
                # Create steps
                steps = pattern_data["steps"]
                
                for step_number, step in enumerate(steps, 1):
                    step_name = step[0]
                    calc_name = step[1]
                    description = step[2]
                    
                    # Create step
                    step_obj = CalculationStep(
                        pipeline_id=pipeline.id,
                        step_id=f"{pipeline_id}_step_{step_number}",
                        step_number=step_number,
                        name=step_name,
                        description=description,
                        standard_id=standard.id if standard else None,
                        calculation_type="formula" if calc_name else "custom",
                        input_config={},
                        output_config={}
                    )
                    db.add(step_obj)
                    steps_created += 1
                
                db.commit()
                
                # Create step dependencies (sequential)
                pipeline_steps = db.query(CalculationStep).filter(
                    CalculationStep.pipeline_id == pipeline.id
                ).order_by(CalculationStep.step_number).all()
                
                for i in range(1, len(pipeline_steps)):
                    dep = CalculationDependency(
                        pipeline_id=pipeline.id,
                        step_id=pipeline_steps[i].id,
                        depends_on_step_id=pipeline_steps[i-1].id,
                        input_mapping={}
                    )
                    db.add(dep)
                    dependencies_created += 1
                
                db.commit()
                
                print(f"Created pipeline: {pipeline.name} ({pipeline_id}) with {len(pipeline_steps)} steps")
    
    print(f"\nMigration complete:")
    print(f"  - {pipelines_created} pipelines created")
    print(f"  - {steps_created} steps created")
    print(f"  - {dependencies_created} dependencies created")


def create_initial_pipelines(db):
    """Create initial set of calculation pipelines"""
    # Load existing workflow data
    workflow_patterns = load_existing_workflow_data()
    
    if workflow_patterns:
        migrate_workflows_to_pipelines(db, workflow_patterns)
    
    # Create additional pipelines not in existing patterns
    additional_pipelines = [
        {
            "pipeline_id": "electrical_cable_sizing",
            "name": "Electrical Cable Sizing",
            "description": "Comprehensive cable sizing calculation pipeline",
            "domain": "electrical",
            "standard_code": "IEC_60364_5_52"
        },
        {
            "pipeline_id": "mechanical_hvac_load",
            "name": "HVAC Load Calculation",
            "description": "Complete HVAC load calculation pipeline",
            "domain": "mechanical",
            "standard_code": "ASHRAE_90.1"
        },
        {
            "pipeline_id": "civil_structural_analysis",
            "name": "Structural Analysis",
            "description": "Structural analysis and design pipeline",
            "domain": "civil",
            "standard_code": "AISC_360"
        }
    ]
    
    for pipeline_data in additional_pipelines:
        existing = db.query(CalculationPipeline).filter(
            CalculationPipeline.pipeline_id == pipeline_data["pipeline_id"]
        ).first()
        
        if not existing:
            standard = db.query(EngineeringStandard).filter(
                EngineeringStandard.standard_code == pipeline_data["standard_code"]
            ).first()
            
            pipeline = CalculationPipeline(
                pipeline_id=pipeline_data["pipeline_id"],
                name=pipeline_data["name"],
                description=pipeline_data["description"],
                domain=pipeline_data["domain"],
                standard_id=standard.id if standard else None
            )
            db.add(pipeline)
    
    db.commit()
    print(f"\nCreated {len(additional_pipelines)} additional pipelines")


def main():
    """Main migration function"""
    print("=" * 60)
    print("Calculation Pipeline Migration")
    print("=" * 60)
    
    # Create all tables
    print("\nCreating database tables...")
    try:
        from calculation_pipeline.models import WorkflowBase
        WorkflowBase.metadata.create_all(bind=workflow_engine)
        print("Tables created successfully")
    except Exception as e:
        print(f"Error creating tables: {e}")
        return
    
    # Get database session
    db = next(get_workflow_db())
    
    try:
        print("\nCreating engineering standards...")
        create_engineering_standards(db)
        
        print("\nCreating standard coefficients...")
        create_standard_coefficients(db)
        
        print("\nCreating initial pipelines...")
        create_initial_pipelines(db)
        
        print("\n" + "=" * 60)
        print("Migration completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nError during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
