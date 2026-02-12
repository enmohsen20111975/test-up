from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class CalculationCategory(Base):
    __tablename__ = "calculation_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    domain = Column(String, index=True, nullable=False)  # civil, electrical, mechanical
    subcategory = Column(String, index=True, nullable=True)
    
    calculations = relationship("Calculation", back_populates="category")

class Calculation(Base):
    __tablename__ = "calculations"
    
    id = Column(Integer, primary_key=True, index=True)
    calculation_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    equation = Column(String, nullable=False)
    domain = Column(String, index=True, nullable=False)
    category_id = Column(Integer, ForeignKey("calculation_categories.id"))
    description = Column(String, nullable=True)
    difficulty = Column(String, nullable=True)
    tags = Column(String, nullable=True)
    reference = Column(String, nullable=True)
    example_input = Column(String, nullable=True)
    example_output = Column(String, nullable=True)
    notes = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, nullable=True)
    
    category = relationship("CalculationCategory", back_populates="calculations")
    variables = relationship("CalculationVariable", back_populates="calculation")

class CalculationVariable(Base):
    __tablename__ = "calculation_variables"
    
    id = Column(Integer, primary_key=True, index=True)
    calculation_id = Column(Integer, ForeignKey("calculations.id"))
    name = Column(String, nullable=False)
    symbol = Column(String, nullable=False)
    unit = Column(String, nullable=True)
    description = Column(String, nullable=True)
    is_input = Column(Boolean, default=True)
    data_type = Column(String, nullable=True)
    default_value = Column(String, nullable=True)
    min_value = Column(Float, nullable=True)
    max_value = Column(Float, nullable=True)
    validation_pattern = Column(String, nullable=True)
    unit_system = Column(String, nullable=True)
    conversion_factor = Column(Float, nullable=True)
    is_required = Column(Boolean, default=True)
    display_order = Column(Integer, nullable=True)
    
    calculation = relationship("Calculation", back_populates="variables")
