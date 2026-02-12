"""
Learning Management System Models
Database models for courses, chapters, lessons, articles, simulations, and progress tracking
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, Boolean, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Discipline(Base):
    """Engineering discipline (Electrical, Mechanical, Civil)"""
    __tablename__ = "disciplines"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(50), unique=True, index=True)
    name = Column(String(100))
    icon = Column(String(50))
    color = Column(String(20))
    description = Column(Text)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chapters = relationship("Chapter", back_populates="discipline", lazy="dynamic")


class Chapter(Base):
    """Chapter within a discipline"""
    __tablename__ = "chapters"

    id = Column(Integer, primary_key=True, index=True)
    discipline_id = Column(Integer, ForeignKey("disciplines.id"))
    title = Column(String(200))
    slug = Column(String(100), index=True)
    description = Column(Text)
    icon = Column(String(50))
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    discipline = relationship("Discipline", back_populates="chapters")
    lessons = relationship("Lesson", back_populates="chapter", lazy="dynamic")


class Lesson(Base):
    """Individual lesson within a chapter"""
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    chapter_id = Column(Integer, ForeignKey("chapters.id"))
    title = Column(String(200))
    slug = Column(String(100), index=True)
    duration_minutes = Column(Integer)
    level = Column(String(50))  # Beginner, Intermediate, Advanced
    type = Column(String(50))  # theory, practice, mixed
    order = Column(Integer, default=0)
    is_published = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chapter = relationship("Chapter", back_populates="lessons")
    objectives = relationship("LearningObjective", back_populates="lesson", cascade="all, delete")
    article = relationship("Article", back_populates="lesson", uselist=False, cascade="all, delete")
    simulations = relationship("Simulation", back_populates="lesson", cascade="all, delete")
    problems = relationship("PracticeProblem", back_populates="lesson", cascade="all, delete")


class LearningObjective(Base):
    """Learning objectives for a lesson"""
    __tablename__ = "learning_objectives"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    objective = Column(Text)
    order = Column(Integer, default=0)

    lesson = relationship("Lesson", back_populates="objectives")


class Article(Base):
    """Full article content for a lesson (stored as Markdown or HTML)"""
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"), unique=True)
    content_type = Column(String(20), default="markdown")  # markdown, html
    content = Column(Text)  # Full article content
    summary = Column(Text)
    key_concepts = Column(JSON)  # Array of key concepts
    related_formulas = Column(JSON)  # Array of formula references
    reading_time = Column(Integer)  # Estimated reading time in minutes
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="article")


class Simulation(Base):
    """Interactive simulation configuration for a lesson"""
    __tablename__ = "simulations"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    name = Column(String(100))
    type = Column(String(50))  # ohms-law, series-circuit, beam-analysis, etc.
    description = Column(Text)
    canvas_width = Column(Integer, default=800)
    canvas_height = Column(Integer, default=300)
    config = Column(JSON)  # Simulation configuration
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="simulations")
    controls = relationship("SimulationControl", back_populates="simulation", cascade="all, delete")
    results = relationship("SimulationResult", back_populates="simulation", cascade="all, delete")


class SimulationControl(Base):
    """Control parameters for simulations"""
    __tablename__ = "simulation_controls"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"))
    name = Column(String(100))
    label = Column(String(100))
    control_type = Column(String(50))  # slider, input, select, button
    min_value = Column(Float)
    max_value = Column(Float)
    default_value = Column(Float)
    step = Column(Float, default=1)
    unit = Column(String(20))
    order = Column(Integer, default=0)

    simulation = relationship("Simulation", back_populates="controls")


class SimulationResult(Base):
    """Result display configuration for simulations"""
    __tablename__ = "simulation_results"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(Integer, ForeignKey("simulations.id"))
    name = Column(String(100))
    label = Column(String(100))
    display_format = Column(String(50), default="value")  # value, formula, calculation
    unit = Column(String(20))
    order = Column(Integer, default=0)

    simulation = relationship("Simulation", back_populates="results")


class PracticeProblem(Base):
    """Practice problems for lessons"""
    __tablename__ = "practice_problems"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    title = Column(String(200))
    description = Column(Text)
    difficulty = Column(String(50))  # Easy, Medium, Hard
    problem_type = Column(String(50))  # numerical, multiple-choice, true-false
    correct_answer = Column(Text)
    tolerance = Column(Float, default=0.01)  # Acceptable error for numerical answers
    explanation = Column(Text)
    solution_steps = Column(JSON)  # Array of solution step descriptions
    formula = Column(Text)  # LaTeX formula for solution
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lesson = relationship("Lesson", back_populates="problems")
    choices = relationship("ProblemChoice", back_populates="problem", cascade="all, delete")


class ProblemChoice(Base):
    """Multiple choice options for problems"""
    __tablename__ = "problem_choices"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("practice_problems.id"))
    value = Column(String(10))  # a, b, c, d
    text = Column(Text)
    is_correct = Column(Boolean, default=False)
    order = Column(Integer, default=0)

    problem = relationship("PracticeProblem", back_populates="choices")


class UserProgress(Base):
    """User progress tracking for lessons"""
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    progress_percent = Column(Integer, default=0)
    objectives_completed = Column(JSON)  # Array of completed objective IDs
    problems_solved = Column(JSON)  # Array of solved problem IDs
    simulation_completed = Column(Boolean, default=False)
    time_spent_seconds = Column(Integer, default=0)
    last_accessed = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    lesson = relationship("Lesson")


class UserBookmark(Base):
    """User bookmarks for lessons"""
    __tablename__ = "user_bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


class HelpArticle(Base):
    """Help center articles"""
    __tablename__ = "help_articles"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("help_categories.id"))
    title = Column(String(200))
    slug = Column(String(100), index=True)
    summary = Column(Text)
    content = Column(Text)
    content_type = Column(String(20), default="markdown")
    order = Column(Integer, default=0)
    is_published = Column(Boolean, default=True)
    views = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    category = relationship("HelpCategory", back_populates="articles")


class HelpCategory(Base):
    """Help center categories"""
    __tablename__ = "help_categories"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100))
    slug = Column(String(100), index=True)
    icon = Column(String(50))
    description = Column(Text)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    articles = relationship("HelpArticle", back_populates="category", lazy="dynamic")