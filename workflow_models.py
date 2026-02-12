"""
Workflow Database Models
This module contains all models for the workflow database, which includes:
- Equations (calculations) with enhanced categorization
- Workflows with steps, inputs, and outputs
- Categories for both equations and workflows
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, Float, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from workflow_database import WorkflowBase


# ============================================================================
# EQUATION MODELS
# ============================================================================

class EquationCategory(WorkflowBase):
    """
    Categories for organizing equations by engineering discipline
    Examples: Civil, Electrical, Mechanical, Chemical, etc.
    """
    __tablename__ = "equation_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    domain = Column(String(50), index=True, nullable=False)  # civil, electrical, mechanical, etc.
    subcategory = Column(String(100), index=True, nullable=True)  # e.g., "Structural", "Circuits"
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)  # Icon identifier for UI
    display_order = Column(Integer, default=0)  # For ordering in UI
    
    equations = relationship("Equation", back_populates="category")


class Equation(WorkflowBase):
    """
    Enhanced equation model with comprehensive metadata
    """
    __tablename__ = "equations"
    
    id = Column(Integer, primary_key=True, index=True)
    equation_id = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "ohms-law-v"
    name = Column(String(200), nullable=False)  # e.g., "Ohm's Law - Voltage"
    description = Column(Text, nullable=True)
    
    # Categorization
    domain = Column(String(50), index=True, nullable=False)  # civil, electrical, mechanical, etc.
    category_id = Column(Integer, ForeignKey("equation_categories.id"), nullable=True)
    
    # Equation Details
    equation = Column(Text, nullable=False)  # The mathematical equation
    equation_latex = Column(Text, nullable=True)  # LaTeX representation for display
    equation_pattern = Column(String(200), nullable=True)  # Pattern for AI recognition
    
    # Additional Metadata
    difficulty_level = Column(String(20), default="intermediate")  # beginner, intermediate, advanced
    tags = Column(JSON, nullable=True)  # Array of tags for search/filtering
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("EquationCategory", back_populates="equations")
    inputs = relationship("EquationInput", back_populates="equation", cascade="all, delete-orphan")
    outputs = relationship("EquationOutput", back_populates="equation", cascade="all, delete-orphan")
    units = relationship("EquationUnit", back_populates="equation", cascade="all, delete-orphan")
    examples = relationship("EquationExample", back_populates="equation", cascade="all, delete-orphan")


class EquationInput(WorkflowBase):
    """
    Input parameters for an equation
    """
    __tablename__ = "equation_inputs"
    
    id = Column(Integer, primary_key=True, index=True)
    equation_id = Column(Integer, ForeignKey("equations.id"), nullable=False)
    name = Column(String(100), nullable=False)  # e.g., "Voltage"
    symbol = Column(String(20), nullable=False)  # e.g., "V"
    description = Column(Text, nullable=True)
    data_type = Column(String(20), default="float")  # float, int, string, boolean
    unit = Column(String(50), nullable=True)  # Default unit
    unit_category = Column(String(50), nullable=True)  # e.g., "electrical", "mechanical"
    
    # Validation
    required = Column(Boolean, default=True)
    default_value = Column(Float, nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    validation_regex = Column(String(200), nullable=True)
    
    # UI Configuration
    input_order = Column(Integer, default=0)
    placeholder = Column(String(200), nullable=True)
    help_text = Column(Text, nullable=True)
    
    equation = relationship("Equation", back_populates="inputs")


class EquationOutput(WorkflowBase):
    """
    Output results from an equation
    """
    __tablename__ = "equation_outputs"
    
    id = Column(Integer, primary_key=True, index=True)
    equation_id = Column(Integer, ForeignKey("equations.id"), nullable=False)
    name = Column(String(100), nullable=False)  # e.g., "Current"
    symbol = Column(String(20), nullable=False)  # e.g., "I"
    description = Column(Text, nullable=True)
    data_type = Column(String(20), default="float")  # float, int, string, boolean
    unit = Column(String(50), nullable=True)  # Output unit
    unit_category = Column(String(50), nullable=True)  # e.g., "electrical", "mechanical"
    
    # Display Configuration
    output_order = Column(Integer, default=0)
    precision = Column(Integer, default=2)  # Number of decimal places
    format_string = Column(String(50), nullable=True)  # e.g., "{:.2f}"
    
    equation = relationship("Equation", back_populates="outputs")


class EquationUnit(WorkflowBase):
    """
    Unit conversions for equation inputs/outputs
    """
    __tablename__ = "equation_units"
    
    id = Column(Integer, primary_key=True, index=True)
    equation_id = Column(Integer, ForeignKey("equations.id"), nullable=False)
    parameter_name = Column(String(100), nullable=False)  # References input/output name
    base_unit = Column(String(50), nullable=False)  # The unit used in calculation
    alternative_units = Column(JSON, nullable=True)  # Array of alternative units with conversion factors
    # Example: {"V": 1, "mV": 0.001, "kV": 1000}
    
    equation = relationship("Equation", back_populates="units")


class EquationExample(WorkflowBase):
    """
    Example calculations for an equation
    """
    __tablename__ = "equation_examples"
    
    id = Column(Integer, primary_key=True, index=True)
    equation_id = Column(Integer, ForeignKey("equations.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Input values for this example
    input_values = Column(JSON, nullable=True)  # {"Voltage": 12, "Resistance": 4}
    
    # Expected output
    expected_output = Column(JSON, nullable=True)  # {"Current": 3.0}
    
    # Additional context
    notes = Column(Text, nullable=True)
    display_order = Column(Integer, default=0)
    
    equation = relationship("Equation", back_populates="examples")


# ============================================================================
# WORKFLOW MODELS
# ============================================================================

class WorkflowCategory(WorkflowBase):
    """
    Categories for organizing workflows by engineering discipline
    """
    __tablename__ = "workflow_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    domain = Column(String(50), index=True, nullable=False)  # civil, electrical, mechanical, etc.
    subcategory = Column(String(100), index=True, nullable=True)
    description = Column(Text, nullable=True)
    icon = Column(String(50), nullable=True)
    display_order = Column(Integer, default=0)
    
    workflows = relationship("Workflow", back_populates="category")


class Workflow(WorkflowBase):
    """
    Enhanced workflow model for multi-step calculations
    """
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Categorization
    domain = Column(String(50), index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("workflow_categories.id"), nullable=True)
    
    # Workflow Configuration
    estimated_time = Column(Integer, nullable=True)  # Estimated completion time in minutes
    difficulty_level = Column(String(20), default="intermediate")
    tags = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    category = relationship("WorkflowCategory", back_populates="workflows")
    inputs = relationship("WorkflowInput", back_populates="workflow", cascade="all, delete-orphan")
    outputs = relationship("WorkflowOutput", back_populates="workflow", cascade="all, delete-orphan")
    steps = relationship("WorkflowStep", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowInput(WorkflowBase):
    """
    Input parameters for a workflow
    """
    __tablename__ = "workflow_inputs"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(20), default="text")  # text, number, select, boolean, file
    description = Column(Text, nullable=True)
    required = Column(Boolean, default=True)
    
    # Validation
    default_value = Column(String(200), nullable=True)
    validation_regex = Column(String(200), nullable=True)
    
    # UI Configuration
    input_order = Column(Integer, default=0)
    placeholder = Column(String(200), nullable=True)
    help_text = Column(Text, nullable=True)
    
    # For select type
    options = Column(JSON, nullable=True)  # Array of options
    
    workflow = relationship("Workflow", back_populates="inputs")


class WorkflowOutput(WorkflowBase):
    """
    Output results from a workflow
    """
    __tablename__ = "workflow_outputs"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    name = Column(String(100), nullable=False)
    type = Column(String(20), default="text")  # text, number, boolean, json, chart
    description = Column(Text, nullable=True)
    
    # Display Configuration
    output_order = Column(Integer, default=0)
    precision = Column(Integer, default=2)
    
    workflow = relationship("Workflow", back_populates="outputs")


class WorkflowStep(WorkflowBase):
    """
    Individual steps within a workflow
    """
    __tablename__ = "workflow_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(Integer, ForeignKey("workflows.id"), nullable=False)
    step_number = Column(Integer, nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    
    # Step Configuration
    step_type = Column(String(50), default="calculation")  # calculation, input, output, conditional
    equation = Column(Text, nullable=True)  # The equation to execute
    equation_id = Column(String(50), nullable=True)  # Reference to equation if using predefined equation
    calculation_id = Column(String(50), nullable=True)  # Legacy reference
    
    # Conditional logic
    condition = Column(Text, nullable=True)  # Condition for executing this step
    
    # UI Configuration
    help_text = Column(Text, nullable=True)
    
    workflow = relationship("Workflow", back_populates="steps")
