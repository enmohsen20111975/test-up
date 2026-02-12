"""
Dynamic workflow transformation - reads patterns from database configuration.
Allows easy editing of workflow patterns without code changes.
"""
import sqlite3
from pathlib import Path
import json

DB_PATH = Path(__file__).parent / "workflows.db"

def find_calculation_by_name(cur, calc_name, domain):
    """Find calculation ID by partial name match across 2000 equations."""
    if not calc_name:
        return None, None
    
    query = """
        SELECT id, equation FROM equations
        WHERE (name LIKE ? OR name LIKE ? OR description LIKE ?)
        AND domain = ?
        LIMIT 1
    """
    
    # Try exact match first
    cur.execute(query, (f"%{calc_name}%", f"{calc_name}%", f"%{calc_name}%", domain))
    result = cur.fetchone()
    return result if result else (None, None)

def apply_dynamic_workflow_patterns():
    """Apply workflow patterns from configuration table to all workflows."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    print("=" * 80)
    print("DYNAMIC WORKFLOW PATTERN TRANSFORMATION")
    print("=" * 80)
    
    try:
        # Get all configuration templates
        cur.execute("""
            SELECT id, domain, template_name, steps_config 
            FROM workflow_templates
            ORDER BY domain, template_name
        """)
        
        templates = cur.fetchall()
        
        if not templates:
            print("❌ No workflow templates found. Run create_workflow_config.py first.")
            return
        
        for domain in ["electrical", "mechanical", "civil"]:
            domain_templates = [t for t in templates if t[1] == domain]
            print(f"\n🔧 {domain.upper()} - {len(domain_templates)} templates available")
            
            # Get all workflows for this domain
            cur.execute("""
                SELECT id FROM workflows 
                WHERE domain = ? 
                ORDER BY id
            """, (domain,))
            
            workflow_ids = [row[0] for row in cur.fetchall()]
            print(f"   Assigning to {len(workflow_ids)} workflows...")
            
            # Round-robin assign templates to workflows
            for idx, wf_id in enumerate(workflow_ids):
                template_idx = idx % len(domain_templates)
                template_id, temp_domain, temp_name, steps_json = domain_templates[template_idx]
                
                steps_config = json.loads(steps_json)
                steps = steps_config.get("steps", [])
                
                # Clear existing steps
                cur.execute("DELETE FROM workflow_steps WHERE workflow_id = ?", (wf_id,))
                conn.commit()
                
                # Insert new steps with dynamic calculation linking
                for step_num, step in enumerate(steps, 1):
                    step_name = step.get("name", f"Step {step_num}")
                    step_desc = step.get("description", "")
                    calc_name = step.get("calculation")
                    
                    # Find calculation in database
                    calc_id, equation = find_calculation_by_name(cur, calc_name, domain)
                    
                    # Insert step
                    cur.execute("""
                        INSERT INTO workflow_steps
                        (workflow_id, step_number, name, description, calculation_id, equation)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (wf_id, step_num, step_name, step_desc, calc_id, equation))
                
                conn.commit()
                
                if (idx + 1) % 100 == 0:
                    print(f"   ✅ {idx + 1} workflows processed...")
            
            print(f"   ✅ All {len(workflow_ids)} {domain} workflows assigned!")
        
        print("\n" + "=" * 80)
        print("✨ DYNAMIC TRANSFORMATION COMPLETE!")
        print("=" * 80)
        
        # Statistics
        cur.execute("""
            SELECT domain, 
                   COUNT(DISTINCT w.id) as workflows,
                   COUNT(ws.id) as total_steps,
                   COUNT(CASE WHEN ws.calculation_id IS NOT NULL THEN 1 END) as linked_steps
            FROM workflows w
            LEFT JOIN workflow_steps ws ON w.id = ws.workflow_id
            GROUP BY domain
            ORDER BY domain
        """)
        
        print("\n📊 Transformation Results:")
        print("-" * 80)
        for domain, wf_count, step_count, linked_count in cur.fetchall():
            pct = (linked_count / step_count * 100) if step_count > 0 else 0
            print(f"{domain.upper()}:")
            print(f"  Workflows: {wf_count} | Total steps: {step_count} | Equations linked: {linked_count} ({pct:.1f}%)")
        
    finally:
        conn.close()

if __name__ == "__main__":
    apply_dynamic_workflow_patterns()
