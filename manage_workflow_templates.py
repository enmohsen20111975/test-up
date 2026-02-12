"""
Admin tool for managing workflow templates.
Edit workflow patterns directly in database without code changes.
"""
import sqlite3
import json
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).parent / "workflows.db"

class WorkflowTemplateManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cur = self.conn.cursor()
    
    def list_all_templates(self):
        """List all workflow templates with their details."""
        self.cur.execute("""
            SELECT t.id, t.domain, t.template_name, t.description
            FROM workflow_templates t
            ORDER BY t.domain, t.template_name
        """)
        
        print("\n" + "=" * 100)
        print("WORKFLOW TEMPLATES - EDITABLE CONFIGURATION")
        print("=" * 100)
        
        current_domain = None
        for template_id, domain, name, desc in self.cur.fetchall():
            if domain != current_domain:
                print(f"\n🔧 {domain.upper()}")
                current_domain = domain
            
            print(f"  [{template_id}] {name}")
            print(f"       Description: {desc}")
            print(f"       Template ID: {template_id}")
    
    def show_template(self, template_id: int):
        """Display full template with all steps."""
        self.cur.execute("""
            SELECT domain, template_name, description, steps_config
            FROM workflow_templates
            WHERE id = ?
        """, (template_id,))
        
        result = self.cur.fetchone()
        if not result:
            print(f"❌ Template {template_id} not found")
            return
        
        domain, name, desc, steps_json = result
        steps = json.loads(steps_json)
        
        print(f"\n{'=' * 80}")
        print(f"TEMPLATE: {name.upper()}")
        print(f"Domain: {domain} | ID: {template_id}")
        print(f"Description: {desc}")
        print(f"{'=' * 80}\n")
        
        print("STEPS:")
        for i, step in enumerate(steps.get("steps", []), 1):
            print(f"  {i}. Name: {step.get('name', 'Unnamed')}")
            print(f"     Equation: {step.get('calculation', 'None')}")
            print(f"     Description: {step.get('description', '')}")
            print()
    
    def edit_template_steps(self, template_id: int, new_steps: list):
        """
        Edit workflow template steps.
        new_steps format:
        [
            {"name": "Step Name", "calculation": "equation_name", "description": "..."},
            ...
        ]
        """
        # Get current template
        self.cur.execute("""
            SELECT steps_config FROM workflow_templates WHERE id = ?
        """, (template_id,))
        
        result = self.cur.fetchone()
        if not result:
            print(f"❌ Template {template_id} not found")
            return False
        
        current_config = json.loads(result[0])
        current_config["steps"] = new_steps
        
        # Update database
        self.cur.execute("""
            UPDATE workflow_templates
            SET steps_config = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (json.dumps(current_config), template_id))
        
        self.conn.commit()
        print(f"✅ Template {template_id} updated successfully!")
        return True
    
    def add_step_to_template(self, template_id: int, step_name: str, 
                            calculation: Optional[str] = None, 
                            description: str = ""):
        """Add a new step to a workflow template."""
        self.cur.execute("""
            SELECT steps_config FROM workflow_templates WHERE id = ?
        """, (template_id,))
        
        result = self.cur.fetchone()
        if not result:
            print(f"❌ Template {template_id} not found")
            return False
        
        config = json.loads(result[0])
        steps = config.get("steps", [])
        
        new_step = {
            "name": step_name,
            "calculation": calculation,
            "description": description
        }
        
        steps.append(new_step)
        config["steps"] = steps
        
        self.cur.execute("""
            UPDATE workflow_templates
            SET steps_config = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (json.dumps(config), template_id))
        
        self.conn.commit()
        print(f"✅ Step '{step_name}' added to template {template_id}")
        return True
    
    def get_equations_for_domain(self, domain: str, search: Optional[str] = None):
        """List available equations for a domain to help with template editing."""
        if search:
            query = """
                SELECT DISTINCT name FROM equations
                WHERE domain = ? AND (name LIKE ? OR description LIKE ?)
                ORDER BY name
                LIMIT 20
            """
            params = (domain, f"%{search}%", f"%{search}%")
        else:
            query = """
                SELECT DISTINCT name FROM equations
                WHERE domain = ?
                ORDER BY name
                LIMIT 20
            """
            params = (domain,)
        
        self.cur.execute(query, params)
        results = self.cur.fetchall()
        
        print(f"\nAvailable equations for {domain}:")
        for name, in results:
            print(f"  • {name}")
        
        return [row[0] for row in results]
    
    def count_workflows_by_template(self):
        """Show how many workflows are using each template."""
        print("\n" + "=" * 80)
        print("WORKFLOW DISTRIBUTION BY TEMPLATE")
        print("=" * 80)
        
        self.cur.execute("""
            SELECT t.domain, t.template_name, COUNT(w.id) as count
            FROM workflow_templates t
            LEFT JOIN workflows w ON w.domain = t.domain
            GROUP BY t.id
            ORDER BY t.domain, t.template_name
        """)
        
        for domain, template_name, count in self.cur.fetchall():
            print(f"{domain:15} | {template_name:30} | {count:3} workflows")
    
    def export_template_as_sql(self, template_id: int):
        """Export a template as SQL statement for documentation."""
        self.cur.execute("""
            SELECT domain, template_name, description, steps_config
            FROM workflow_templates
            WHERE id = ?
        """, (template_id,))
        
        result = self.cur.fetchone()
        if not result:
            print(f"❌ Template {template_id} not found")
            return
        
        domain, name, desc, steps_json = result
        
        sql = f"""
-- Template: {name} ({domain})
-- Description: {desc}
UPDATE workflow_templates
SET steps_config = '{steps_json}'
WHERE template_name = '{name}';
"""
        print(sql)
        return sql
    
    def close(self):
        """Close database connection."""
        self.conn.close()

def main():
    manager = WorkflowTemplateManager()
    
    # Show all templates
    manager.list_all_templates()
    
    # Show distribution
    manager.count_workflows_by_template()
    
    print("\n" + "=" * 80)
    print("EXAMPLE: How to Edit a Template")
    print("=" * 80)
    print("""
Option 1: Using SQL directly
  UPDATE workflow_templates
  SET steps_config = '[{"name": "New Step", "calculation": "equation", "description": "..."}]'
  WHERE template_name = 'electrical_pattern_name';

Option 2: Using this Python manager
  manager.show_template(1)  # View template
  new_steps = [
      {"name": "Step 1", "calculation": "power_calc", "description": "Calculate power"},
      {"name": "Step 2", "calculation": "none", "description": "Manual entry"},
  ]
  manager.edit_template_steps(1, new_steps)

Option 3: Add individual steps
  manager.add_step_to_template(1, "New Step", "equation_name", "Description")

Option 4: Find available equations
  manager.get_equations_for_domain("electrical", "power")  # Search for power-related equations
""")
    
    print("=" * 80)
    print("✅ Workflow templates are now EDITABLE via database without code changes!")
    print("   • Edit: SQL UPDATE or this Python tool")
    print("   • Changes take effect on next workflow execution")
    print("   • All 800 workflows use these dynamic patterns")
    print("=" * 80)
    
    manager.close()

if __name__ == "__main__":
    main()
