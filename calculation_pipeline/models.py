"""
Calculation Pipeline Database Models
This module defines the schema for the calculation pipeline system, 
implementing the deterministic calculation pipeline architecture for engineering workflows.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Float, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from workflow_database import WorkflowBase


class EngineeringStandard(WorkflowBase):
    """
    Engineering standards that calculations reference (IEC, NEC, IEEE, BS, etc.)
    """
    __tablename__ = "engineering_standards"
    
    id = Column(Integer, primary_key=True, index=True)
    standard_code = Column(String(100), unique=True, index=True, nullable=False)  # e.g., "IEC_60364_5_52"
    name = Column(String(200), nullable=False)  # e.g., "IEC 60364-5-52: Low-voltage electrical installations"
    description = Column(Text, nullable=True)
    standard_type = Column(String(50), nullable=False)  # "cable_sizing", "load_calculation", "protection", etc.
    domain = Column(String(50), index=True, nullable=False)  # civil, electrical, mechanical
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    coefficients = relationship("StandardCoefficient", back_populates="standard")
    pipelines = relationship("CalculationPipeline", back_populates="standard")
    steps = relationship("CalculationStep", back_populates="standard")


class StandardCoefficient(WorkflowBase):
    """
    Lookup tables for engineering standards (derating factors, grouping factors, etc.)
    """
    __tablename__ = "standard_coefficients"
    
    id = Column(Integer, primary_key=True, index=True)
    standard_id = Column(Integer, ForeignKey("engineering_standards.id"), nullable=False)
    coefficient_name = Column(String(100), index=True, nullable=False)
    coefficient_type = Column(String(50), index=True, nullable=False)  # "derating", "grouping", "temperature"
    data_source = Column(String(50), nullable=False)  # "table", "formula", "lookup"
    
    # For table-based data
    coefficient_table = Column(JSON, nullable=True)  # {"25": 1.0, "30": 0.95, "35": 0.9}
    # For formula-based data
    formula = Column(String(200), nullable=True)
    # For lookup from external data
    external_reference = Column(String(200), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    standard = relationship("EngineeringStandard", back_populates="coefficients")


class CalculationPipeline(WorkflowBase):
    """
    Calculation pipeline definition - top-level DAG configuration
    """
    __tablename__ = "calculation_pipelines"
    
    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String(50), index=True, nullable=False)  # civil, electrical, mechanical
    standard_id = Column(Integer, ForeignKey("engineering_standards.id"), nullable=True)
    version = Column(String(20), default="1.0")
    
    estimated_time = Column(Integer, nullable=True)
    difficulty_level = Column(String(20), default="intermediate")
    tags = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    standard = relationship("EngineeringStandard", back_populates="pipelines")
    steps = relationship("CalculationStep", back_populates="pipeline")
    dependencies = relationship("CalculationDependency", back_populates="pipeline")


class CalculationStep(WorkflowBase):
    """
    Individual calculation step in a pipeline
    """
    __tablename__ = "calculation_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("calculation_pipelines.id"), nullable=False)
    step_id = Column(String(100), index=True, nullable=False)
    step_number = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    standard_id = Column(Integer, ForeignKey("engineering_standards.id"), nullable=True)
    formula_ref = Column(String(200), nullable=True)
    formula = Column(Text, nullable=True)
    
    # Input/output configuration
    input_config = Column(JSON, nullable=True)  # {"param": "source", "required": true, "type": "number"}
    output_config = Column(JSON, nullable=True)  # {"param": "unit", "type": "number", "precision": 2}
    
    # Calculation settings
    calculation_type = Column(String(50), default="formula")  # formula, lookup, table, custom
    precision = Column(Integer, default=2)
    step_type = Column(String(50), default="calculation")  # calculation, input, output, validation
    
    # Validation configuration
    validation_config = Column(JSON, nullable=True)  # {"range": {"min": 0, "max": 100}}
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    pipeline = relationship("CalculationPipeline", back_populates="steps")
    standard = relationship("EngineeringStandard", back_populates="steps")
    dependencies = relationship("CalculationDependency", back_populates="step")
    validations = relationship("CalculationValidation", back_populates="step")


class CalculationDependency(WorkflowBase):
    """
    Dependency between calculation steps (DAG edges)
    """
    __tablename__ = "calculation_dependencies"
    
    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("calculation_pipelines.id"), nullable=False)
    step_id = Column(Integer, ForeignKey("calculation_steps.id"), nullable=False)
    depends_on_step_id = Column(Integer, ForeignKey("calculation_steps.id"), nullable=False)
    
    # How the output from depends_on_step is used as input
    input_mapping = Column(JSON, nullable=True)  # {"from": "current_a", "to": "load_current"}
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    pipeline = relationship("CalculationPipeline", back_populates="dependencies")
    step = relationship("CalculationStep", foreign_keys=[step_id], back_populates="dependencies")
    depends_on_step = relationship("CalculationStep", foreign_keys=[depends_on_step_id])


class CalculationValidation(WorkflowBase):
    """
    Validation gates for calculation steps
    """
    __tablename__ = "calculation_validations"
    
    id = Column(Integer, primary_key=True, index=True)
    step_id = Column(Integer, ForeignKey("calculation_steps.id"), nullable=False)
    validation_type = Column(String(50), nullable=False)  # "range", "lookup", "formula", "standard"
    
    # Validation configuration
    validation_config = Column(JSON, nullable=True)
    failure_action = Column(String(50), default="stop")  # stop, warn, auto_retry
    
    # For standard-based validation
    standard_id = Column(Integer, ForeignKey("engineering_standards.id"), nullable=True)
    standard_section = Column(String(100), nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    step = relationship("CalculationStep", back_populates="validations")
    standard = relationship("EngineeringStandard")


class CalculationExecution(WorkflowBase):
    """
    Execution history of calculation pipelines
    """
    __tablename__ = "calculation_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    pipeline_id = Column(Integer, ForeignKey("calculation_pipelines.id"), nullable=False)
    execution_id = Column(String(100), unique=True, index=True, nullable=False)
    status = Column(String(50), default="pending")  # pending, running, completed, failed, aborted
    
    # Input parameters
    input_data = Column(JSON, nullable=True)
    
    # Output results
    output_data = Column(JSON, nullable=True)
    
    # Execution metadata
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    execution_time = Column(Float, nullable=True)  # in seconds
    
    # Error information
    error_message = Column(Text, nullable=True)
    error_stacktrace = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    pipeline = relationship("CalculationPipeline")
    step_executions = relationship("StepExecution", back_populates="execution")


class StepExecution(WorkflowBase):
    """
    Execution history of individual calculation steps
    """
    __tablename__ = "step_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    execution_id = Column(Integer, ForeignKey("calculation_executions.id"), nullable=False)
    step_id = Column(Integer, ForeignKey("calculation_steps.id"), nullable=False)
    
    status = Column(String(50), default="pending")
    input_data = Column(JSON, nullable=True)
    output_data = Column(JSON, nullable=True)
    calculation_result = Column(JSON, nullable=True)
    
    # Validation results
    validation_passed = Column(Boolean, nullable=True)
    validation_errors = Column(JSON, nullable=True)
    
    start_time = Column(DateTime(timezone=True))
    end_time = Column(DateTime(timezone=True))
    execution_time = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    execution = relationship("CalculationExecution", back_populates="step_executions")
    step = relationship("CalculationStep")
