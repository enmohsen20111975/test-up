from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class WorkflowCategory(Base):
    __tablename__ = "workflow_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    domain = Column(String, index=True, nullable=False)  # civil, electrical, mechanical
    subcategory = Column(String, index=True, nullable=True)
    
    workflows = relationship("Workflow", back_populates="category")

class Workflow(Base):
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String, unique=True, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    domain = Column(String, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("workflow_categories.id"))
    
    category = relationship("WorkflowCategory", back_populates="workflows")
    inputs = relationship("WorkflowInput", back_populates="workflow")
    outputs = relationship("WorkflowOutput", back_populates="workflow")
    steps = relationship("WorkflowStep", back_populates="workflow")

class WorkflowInput(Base):
    __tablename__ = "workflow_inputs"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    name = Column(String, nullable=False)
    type = Column(String, default="text")
    description = Column(String, nullable=True)
    required = Column(Integer, default=1)
    data_type = Column(String, nullable=True)
    default_value = Column(String, nullable=True)
    validation_pattern = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    display_order = Column(Integer, nullable=True)
    
    workflow = relationship("Workflow", back_populates="inputs")

class WorkflowOutput(Base):
    __tablename__ = "workflow_outputs"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    name = Column(String, nullable=False)
    type = Column(String, default="text")
    description = Column(String, nullable=True)
    
    workflow = relationship("Workflow", back_populates="outputs")

class WorkflowStep(Base):
    __tablename__ = "workflow_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"))
    step_number = Column(Integer, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    equation = Column(String, nullable=True)
    calculation_id = Column(String, nullable=True)
    
    workflow = relationship("Workflow", back_populates="steps")
