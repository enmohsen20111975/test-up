#!/usr/bin/env python
"""Verify workflows.db has been updated with new workflows"""
import sqlite3

db_path = "workflows.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 70)
print("WORKFLOWS.DB VERIFICATION")
print("=" * 70)

# Check tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [t[0] for t in cursor.fetchall()]
print(f"\n✅ Tables found ({len(tables)}):")
for table in sorted(tables):
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    count = cursor.fetchone()[0]
    print(f"   • {table}: {count} rows")

# Check workflows
print("\n✅ WORKFLOWS BY DOMAIN:")
cursor.execute("""
  SELECT domain, COUNT(*) as count
  FROM workflows
  GROUP BY domain
  ORDER BY domain
""")

for domain, count in cursor.fetchall():
    print(f"   • {domain}: {count} workflows")

# Sample workflow
print("\n✅ SAMPLE WORKFLOW:")
cursor.execute("""
  SELECT workflow_id, title
  FROM workflows
  LIMIT 1
""")
result = cursor.fetchone()
if result:
    wf_id, title = result
    print(f"   ID: {wf_id}")
    print(f"   Title: {title}")
    
    # Check steps
    cursor.execute("""
      SELECT COUNT(*) FROM workflow_steps
      WHERE workflow_id = (SELECT id FROM workflows WHERE workflow_id = ?)
    """, (wf_id,))
    step_count = cursor.fetchone()[0]
    print(f"   Steps: {step_count}")

print("\n" + "=" * 70)
print("✨ Verification complete!")
print("=" * 70)

conn.close()
