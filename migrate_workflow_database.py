"""
Migration Script for Workflow Database
This script:
1. Creates all tables in the workflow database
2. Populates equations from calculations.json
3. Creates appropriate categories
4. Maps inputs, outputs, and units correctly
"""

import json
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow_database import workflow_engine, WorkflowBase, get_workflow_db
from workflow_models import (
    Equation, EquationCategory, EquationInput, EquationOutput, 
    EquationUnit, EquationExample,
    Workflow, WorkflowCategory, WorkflowInput, WorkflowOutput, WorkflowStep
)


def load_calculations():
    """Load calculations from calculations.json"""
    calculations_file = Path(__file__).parent.parent / "calculations.json"
    with open(calculations_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('calculations', [])


def load_workflows():
    """Load workflows from workflows.json"""
    workflows_file = Path(__file__).parent.parent / "workflows.json"
    with open(workflows_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('workflows', [])


def get_or_create_category(db, domain, subcategory=None):
    """Get or create an equation category"""
    # Try to find existing category
    query = db.query(EquationCategory).filter_by(domain=domain)
    if subcategory:
        query = query.filter_by(subcategory=subcategory)
    
    category = query.first()
    
    if not category:
        # Create new category
        name = f"{domain.capitalize()}"
        if subcategory:
            name = f"{subcategory}"
        
        category = EquationCategory(
            name=name,
            domain=domain,
            subcategory=subcategory,
            description=f"Equations for {name}",
            display_order=0
        )
        db.add(category)
        db.commit()
        db.refresh(category)
    
    return category


def migrate_equations():
    """Migrate equations from calculations.json to workflow database"""
    print("Starting equation migration...")
    
    # Create all tables
    print("Creating database tables...")
    WorkflowBase.metadata.create_all(bind=workflow_engine)
    print("Tables created successfully!")
    
    # Load calculations
    calculations = load_calculations()
    print(f"Loaded {len(calculations)} calculations from calculations.json")
    
    # Get database session
    db = next(get_workflow_db())
    
    try:
        # Track statistics
        equations_created = 0
        inputs_created = 0
        outputs_created = 0
        categories_created = {}
        
        for calc in calculations:
            # Get or create category
            category = get_or_create_category(db, calc.get('domain', 'general'))
            if calc.get('domain') not in categories_created:
                categories_created[calc['domain']] = 0
            categories_created[calc['domain']] += 1
            
            # Create equation
            equation = Equation(
                equation_id=calc.get('id', ''),
                name=calc.get('name', ''),
                equation=calc.get('equation', ''),
                domain=calc.get('domain', 'general'),
                category_id=category.id,
                difficulty_level='intermediate',
                is_active=True
            )
            db.add(equation)
            db.commit()
            db.refresh(equation)
            equations_created += 1
            
            # Process variables
            variables = calc.get('variables', [])
            for var in variables:
                # Determine if input or output based on position
                # Usually, the last variable is the output
                is_output = (var == variables[-1])
                
                if is_output:
                    # Create output
                    output = EquationOutput(
                        equation_id=equation.id,
                        name=var.get('name', ''),
                        symbol=var.get('symbol', ''),
                        description=var.get('description', ''),
                        unit=var.get('unit', ''),
                        output_order=0,
                        precision=2
                    )
                    db.add(output)
                    outputs_created += 1
                else:
                    # Create input
                    input_param = EquationInput(
                        equation_id=equation.id,
                        name=var.get('name', ''),
                        symbol=var.get('symbol', ''),
                        description=var.get('description', ''),
                        unit=var.get('unit', ''),
                        required=True,
                        input_order=len([v for v in variables if v != variables[-1] and variables.index(v) < variables.index(var)])
                    )
                    db.add(input_param)
                    inputs_created += 1
            
            # Commit after each equation to avoid large transactions
            db.commit()
        
        print("\n" + "="*50)
        print("Migration completed successfully!")
        print("="*50)
        print(f"Equations created: {equations_created}")
        print(f"Inputs created: {inputs_created}")
        print(f"Outputs created: {outputs_created}")
        print(f"\nCategories by domain:")
        for domain, count in categories_created.items():
            print(f"  - {domain}: {count} equations")
        print("="*50)
        
    except Exception as e:
        print(f"Error during migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def get_or_create_workflow_category(db, domain, subcategory=None):
    """Get or create a workflow category"""
    query = db.query(WorkflowCategory).filter_by(domain=domain)
    if subcategory:
        query = query.filter_by(subcategory=subcategory)
    
    category = query.first()
    
    if not category:
        name = f"{domain.capitalize()}"
        if subcategory:
            name = f"{subcategory}"
        
        category = WorkflowCategory(
            name=name,
            domain=domain,
            subcategory=subcategory,
            description=f"Workflows for {name}",
            display_order=0
        )
        db.add(category)
        db.commit()
        db.refresh(category)
    
    return category


def migrate_workflows():
    """Migrate workflows from workflows.json to workflow database"""
    print("\nStarting workflow migration...")
    
    # Load workflows
    workflows = load_workflows()
    print(f"Loaded {len(workflows)} workflows from workflows.json")
    
    # Get database session
    db = next(get_workflow_db())
    
    try:
        # Track statistics
        workflows_created = 0
        inputs_created = 0
        outputs_created = 0
        steps_created = 0
        categories_created = {}
        
        for wf in workflows:
            # Get or create category
            category = get_or_create_workflow_category(db, wf.get('domain', 'general'))
            if wf.get('domain') not in categories_created:
                categories_created[wf['domain']] = 0
            categories_created[wf['domain']] += 1
            
            # Create workflow
            workflow = Workflow(
                workflow_id=wf.get('id', ''),
                title=wf.get('title', ''),
                description=wf.get('description', ''),
                domain=wf.get('domain', 'general'),
                category_id=category.id,
                difficulty_level='intermediate',
                is_active=True
            )
            db.add(workflow)
            db.commit()
            db.refresh(workflow)
            workflows_created += 1
            
            # Create inputs
            for idx, input_name in enumerate(wf.get('inputs', [])):
                wf_input = WorkflowInput(
                    workflow_id=workflow.id,
                    name=input_name,
                    type='text',
                    description=f"Input: {input_name}",
                    required=True,
                    input_order=idx
                )
                db.add(wf_input)
                inputs_created += 1
            
            # Create outputs
            for idx, output_name in enumerate(wf.get('outputs', [])):
                wf_output = WorkflowOutput(
                    workflow_id=workflow.id,
                    name=output_name,
                    type='text',
                    description=f"Output: {output_name}",
                    output_order=idx
                )
                db.add(wf_output)
                outputs_created += 1
            
            # Create steps
            for idx, step_name in enumerate(wf.get('steps', [])):
                step = WorkflowStep(
                    workflow_id=workflow.id,
                    step_number=idx + 1,
                    name=step_name,
                    description=f"Step: {step_name}",
                    step_type='calculation'
                )
                db.add(step)
                steps_created += 1
            
            # Commit after each workflow
            db.commit()
        
        print("\n" + "="*50)
        print("Workflow migration completed successfully!")
        print("="*50)
        print(f"Workflows created: {workflows_created}")
        print(f"Inputs created: {inputs_created}")
        print(f"Outputs created: {outputs_created}")
        print(f"Steps created: {steps_created}")
        print(f"\nWorkflows by domain:")
        for domain, count in categories_created.items():
            print(f"  - {domain}: {count} workflows")
        print("="*50)
        
    except Exception as e:
        print(f"Error during workflow migration: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def verify_migration():
    """Verify the migration by counting records"""
    print("\nVerifying migration...")
    db = next(get_workflow_db())
    
    try:
        equation_count = db.query(Equation).count()
        input_count = db.query(EquationInput).count()
        output_count = db.query(EquationOutput).count()
        category_count = db.query(EquationCategory).count()
        workflow_count = db.query(Workflow).count()
        workflow_input_count = db.query(WorkflowInput).count()
        workflow_output_count = db.query(WorkflowOutput).count()
        workflow_step_count = db.query(WorkflowStep).count()
        
        print("\n" + "="*50)
        print("EQUATIONS")
        print("="*50)
        print(f"Equations in database: {equation_count}")
        print(f"Inputs in database: {input_count}")
        print(f"Outputs in database: {output_count}")
        print(f"Categories in database: {category_count}")
        
        # Show sample equations
        print("\nSample equations:")
        for eq in db.query(Equation).limit(5).all():
            print(f"  - {eq.name} ({eq.equation_id})")
            print(f"    Domain: {eq.domain}")
            print(f"    Equation: {eq.equation}")
        
        print("\n" + "="*50)
        print("WORKFLOWS")
        print("="*50)
        print(f"Workflows in database: {workflow_count}")
        print(f"Workflow inputs in database: {workflow_input_count}")
        print(f"Workflow outputs in database: {workflow_output_count}")
        print(f"Workflow steps in database: {workflow_step_count}")
        
        # Show sample workflows
        print("\nSample workflows:")
        for wf in db.query(Workflow).limit(5).all():
            print(f"  - {wf.title} ({wf.workflow_id})")
            print(f"    Domain: {wf.domain}")
            print(f"    Description: {wf.description}")
            
    finally:
        db.close()


if __name__ == "__main__":
    print("EngiSuite Workflow Database Migration")
    print("="*50)
    
    # Run equation migration
    migrate_equations()
    
    # Run workflow migration
    migrate_workflows()
    
    # Verify migration
    verify_migration()
    
    print("\n" + "="*50)
    print("All migrations completed successfully!")
    print("="*50)
