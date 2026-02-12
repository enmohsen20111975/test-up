"""
Workflow Database Module
This module handles the connection to the workflow database, which contains:
- Equations (calculations)
- Workflows
- Categories
- All engineering-related content
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

WORKFLOW_DATABASE_URL = settings.WORKFLOW_DATABASE_URL

# Create engine with SQLite compatibility
if WORKFLOW_DATABASE_URL.startswith("sqlite"):
    workflow_engine = create_engine(
        WORKFLOW_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    workflow_engine = create_engine(WORKFLOW_DATABASE_URL)
    
WorkflowSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=workflow_engine)

WorkflowBase = declarative_base()

def get_workflow_db():
    """Dependency to get workflow database session"""
    db = WorkflowSessionLocal()
    try:
        yield db
    finally:
        db.close()
