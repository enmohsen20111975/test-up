"""
Learning Management System API Routes
RESTful API for courses, lessons, articles, simulations, and progress tracking
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime
import json

from database import get_db
from auth.router import get_current_user
from auth.models import User

router = APIRouter(prefix="/api/learning", tags=["Learning"])


# ============== DISCIPLINES ==============

@router.get("/disciplines")
def get_disciplines(
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all engineering disciplines"""
    query = db.query(Discipline)
    if active_only:
        query = query.filter(Discipline.is_active == True)
    query = query.order_by(Discipline.order)
    disciplines = query.all()
    return {
        "success": True,
        "data": [serialize_discipline(d) for d in disciplines]
    }


@router.get("/disciplines/{discipline_key}")
def get_discipline(
    discipline_key: str,
    db: Session = Depends(get_db)
):
    """Get specific discipline with chapters"""
    discipline = db.query(Discipline).filter(
        Discipline.key == discipline_key
    ).first()
    
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    
    return {
        "success": True,
        "data": serialize_discipline(discipline, include_chapters=True)
    }


# ============== CHAPTERS ==============

@router.get("/chapters")
def get_chapters(
    discipline_key: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get chapters, optionally filtered by discipline"""
    query = db.query(Chapter)
    
    if discipline_key:
        discipline = db.query(Discipline).filter(
            Discipline.key == discipline_key
        ).first()
        if discipline:
            query = query.filter(Chapter.discipline_id == discipline.id)
    
    if active_only:
        query = query.filter(Chapter.is_active == True)
    
    query = query.order_by(Chapter.order)
    chapters = query.all()
    
    return {
        "success": True,
        "data": [serialize_chapter(c, include_lessons=False) for c in chapters]
    }


@router.get("/chapters/{chapter_id}")
def get_chapter(
    chapter_id: int,
    db: Session = Depends(get_db)
):
    """Get specific chapter with lessons"""
    chapter = db.query(Chapter).filter(Chapter.id == chapter_id).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return {
        "success": True,
        "data": serialize_chapter(chapter, include_lessons=True)
    }


# ============== LESSONS ==============

@router.get("/lessons")
def get_lessons(
    chapter_id: Optional[int] = None,
    discipline_key: Optional[str] = None,
    level: Optional[str] = None,
    published_only: bool = True,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get lessons with filtering and pagination"""
    query = db.query(Lesson)
    
    if chapter_id:
        query = query.filter(Lesson.chapter_id == chapter_id)
    elif discipline_key:
        discipline = db.query(Discipline).filter(
            Discipline.key == discipline_key
        ).first()
        if discipline:
            query = query.join(Chapter).filter(
                Chapter.discipline_id == discipline.id
            )
    
    if level:
        query = query.filter(Lesson.level == level)
    
    if published_only:
        query = query.filter(Lesson.is_published == True)
    
    # Pagination
    total = query.count()
    query = query.order_by(Lesson.order)
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    lessons = query.all()
    
    return {
        "success": True,
        "data": [serialize_lesson(l, include_content=False) for l in lessons],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": (total + page_size - 1) // page_size
        }
    }


@router.get("/lessons/{lesson_id}")
def get_lesson(
    lesson_id: int,
    db: Session = Depends(get_db)
):
    """Get full lesson data including article, simulations, and problems"""
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    return {
        "success": True,
        "data": serialize_lesson(lesson, include_content=True)
    }


@router.get("/lessons/slug/{discipline_key}/{chapter_slug}/{lesson_slug}")
def get_lesson_by_slug(
    discipline_key: str,
    chapter_slug: str,
    lesson_slug: str,
    db: Session = Depends(get_db)
):
    """Get lesson by slugs"""
    discipline = db.query(Discipline).filter(
        Discipline.key == discipline_key
    ).first()
    
    if not discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    
    chapter = db.query(Chapter).filter(
        Chapter.discipline_id == discipline.id,
        Chapter.slug == chapter_slug
    ).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    lesson = db.query(Lesson).filter(
        Lesson.chapter_id == chapter.id,
        Lesson.slug == lesson_slug
    ).first()
    
    if not lesson:
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    return {
        "success": True,
        "data": serialize_lesson(lesson, include_content=True)
    }


# ============== ARTICLES ==============

@router.get("/articles/{lesson_id}")
def get_article(
    lesson_id: int,
    db: Session = Depends(get_db)
):
    """Get article content for a lesson"""
    article = db.query(Article).filter(Article.lesson_id == lesson_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return {
        "success": True,
        "data": serialize_article(article)
    }


# ============== SIMULATIONS ==============

@router.get("/simulations/{lesson_id}")
def get_simulations(
    lesson_id: int,
    db: Session = Depends(get_db)
):
    """Get all simulations for a lesson"""
    simulations = db.query(Simulation).filter(
        Simulation.lesson_id == lesson_id
    ).all()
    
    return {
        "success": True,
        "data": [serialize_simulation(s) for s in simulations]
    }


@router.post("/simulations/{simulation_id}/calculate")
def calculate_simulation(
    simulation_id: int,
    params: dict,
    db: Session = Depends(get_db)
):
    """Calculate simulation results based on parameters"""
    simulation = db.query(Simulation).filter(
        Simulation.id == simulation_id
    ).first()
    
    if not simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    
    # Calculate results based on simulation type
    results = calculate_simulation_results(simulation, params)
    
    return {
        "success": True,
        "data": {
            "simulation_id": simulation_id,
            "results": results
        }
    }


# ============== PRACTICE PROBLEMS ==============

@router.get("/problems/{lesson_id}")
def get_problems(
    lesson_id: int,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get practice problems for a lesson"""
    query = db.query(PracticeProblem).filter(
        PracticeProblem.lesson_id == lesson_id
    )
    
    if difficulty:
        query = query.filter(PracticeProblem.difficulty == difficulty)
    
    query = query.order_by(PracticeProblem.order)
    problems = query.all()
    
    return {
        "success": True,
        "data": [serialize_problem(p, include_choices=True) for p in problems]
    }


@router.post("/problems/{problem_id}/check")
def check_answer(
    problem_id: int,
    answer: dict,
    db: Session = Depends(get_db)
):
    """Check if answer is correct"""
    problem = db.query(PracticeProblem).filter(
        PracticeProblem.id == problem_id
    ).first()
    
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    user_answer = answer.get("answer", "")
    is_correct = check_problem_answer(problem, user_answer)
    
    return {
        "success": True,
        "data": {
            "problem_id": problem_id,
            "correct": is_correct,
            "correct_answer": problem.correct_answer,
            "explanation": problem.explanation if not is_correct else None
        }
    }


# ============== USER PROGRESS ==============

@router.get("/progress/{lesson_id}")
def get_lesson_progress(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's progress for a lesson"""
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.lesson_id == lesson_id
    ).first()
    
    if not progress:
        return {
            "success": True,
            "data": {
                "progress_percent": 0,
                "objectives_completed": [],
                "problems_solved": [],
                "simulation_completed": False,
                "time_spent_seconds": 0
            }
        }
    
    return {
        "success": True,
        "data": serialize_progress(progress)
    }


@router.post("/progress/{lesson_id}")
def update_progress(
    lesson_id: int,
    progress_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's progress for a lesson"""
    progress = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.lesson_id == lesson_id
    ).first()
    
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            lesson_id=lesson_id
        )
        db.add(progress)
    
    # Update progress fields
    if "progress_percent" in progress_data:
        progress.progress_percent = progress_data["progress_percent"]
    
    if "objectives_completed" in progress_data:
        progress.objectives_completed = json.dumps(progress_data["objectives_completed"])
    
    if "problems_solved" in progress_data:
        progress.problems_solved = json.dumps(progress_data["problems_solved"])
    
    if "simulation_completed" in progress_data:
        progress.simulation_completed = progress_data["simulation_completed"]
    
    if "time_spent_seconds" in progress_data:
        progress.time_spent_seconds += progress_data["time_spent_seconds"]
    
    progress.last_accessed = datetime.utcnow()
    
    # Check if completed
    if progress_data.get("progress_percent", 0) >= 100:
        progress.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "data": serialize_progress(progress)
    }


@router.get("/progress/summary")
def get_progress_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's overall learning progress"""
    total_lessons = db.query(func.count(Lesson.id)).filter(
        Lesson.is_published == True
    ).scalar()
    
    completed_lessons = db.query(func.count(UserProgress.id)).filter(
        UserProgress.user_id == current_user.id,
        UserProgress.completed_at != None
    ).scalar()
    
    total_problems = db.query(PracticeProblem).join(Lesson).filter(
        Lesson.is_published == True
    ).count()
    
    problems_solved = db.query(UserProgress).filter(
        UserProgress.user_id == current_user.id
    ).all()
    
    solved_count = 0
    for p in problems_solved:
        if p.problems_solved:
            solved = json.loads(p.problems_solved)
            solved_count += len(solved)
    
    return {
        "success": True,
        "data": {
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "progress_percent": round((completed_lessons / total_lessons * 100), 1) if total_lessons > 0 else 0,
            "total_problems": total_problems,
            "problems_solved": solved_count
        }
    }


# ============== BOOKMARKS ==============

@router.get("/bookmarks")
def get_bookmarks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's bookmarked lessons"""
    bookmarks = db.query(UserBookmark).filter(
        UserBookmark.user_id == current_user.id
    ).order_by(desc(UserBookmark.created_at)).all()
    
    return {
        "success": True,
        "data": [serialize_bookmark(b) for b in bookmarks]
    }


@router.post("/bookmarks/{lesson_id}")
def add_bookmark(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bookmark a lesson"""
    # Check if already bookmarked
    existing = db.query(UserBookmark).filter(
        UserBookmark.user_id == current_user.id,
        UserBookmark.lesson_id == lesson_id
    ).first()
    
    if existing:
        return {"success": True, "message": "Already bookmarked"}
    
    bookmark = UserBookmark(
        user_id=current_user.id,
        lesson_id=lesson_id
    )
    db.add(bookmark)
    db.commit()
    
    return {
        "success": True,
        "data": serialize_bookmark(bookmark)
    }


@router.delete("/bookmarks/{lesson_id}")
def remove_bookmark(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove bookmark"""
    bookmark = db.query(UserBookmark).filter(
        UserBookmark.user_id == current_user.id,
        UserBookmark.lesson_id == lesson_id
    ).first()
    
    if bookmark:
        db.delete(bookmark)
        db.commit()
    
    return {"success": True, "message": "Bookmark removed"}


# ============== HELP CENTER ==============

@router.get("/help/categories")
def get_help_categories(db: Session = Depends(get_db)):
    """Get help center categories"""
    categories = db.query(HelpCategory).filter(
        HelpCategory.is_active == True
    ).order_by(HelpCategory.order).all()
    
    return {
        "success": True,
        "data": [serialize_help_category(c) for c in categories]
    }


@router.get("/help/articles")
def get_help_articles(
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get help articles"""
    query = db.query(HelpArticle).filter(HelpArticle.is_published == True)
    
    if category_id:
        query = query.filter(HelpArticle.category_id == category_id)
    
    if search:
        query = query.filter(
            (HelpArticle.title.contains(search)) |
            (HelpArticle.content.contains(search))
        )
    
    query = query.order_by(HelpArticle.order)
    articles = query.all()
    
    return {
        "success": True,
        "data": [serialize_help_article(a) for a in articles]
    }


@router.get("/help/articles/{article_id}")
def get_help_article(article_id: int, db: Session = Depends(get_db)):
    """Get specific help article"""
    article = db.query(HelpArticle).filter(HelpArticle.id == article_id).first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Increment view count
    article.views += 1
    db.commit()
    
    return {
        "success": True,
        "data": serialize_help_article(article, include_content=True)
    }


# ============== HELPER FUNCTIONS ==============

def serialize_discipline(d, include_chapters=False):
    data = {
        "id": d.id,
        "key": d.key,
        "name": d.name,
        "icon": d.icon,
        "color": d.color,
        "description": d.description
    }
    if include_chapters:
        data["chapters"] = [serialize_chapter(c, include_lessons=False) for c in d.chapters]
    return data


def serialize_chapter(c, include_lessons=True):
    data = {
        "id": c.id,
        "title": c.title,
        "slug": c.slug,
        "description": c.description,
        "icon": c.icon,
        "order": c.order
    }
    if include_lessons:
        data["lessons"] = [serialize_lesson(l, include_content=False) for l in c.lessons]
    return data


def serialize_lesson(l, include_content=True):
    data = {
        "id": l.id,
        "title": l.title,
        "slug": l.slug,
        "chapter_id": l.chapter_id,
        "duration_minutes": l.duration_minutes,
        "level": l.level,
        "type": l.type,
        "order": l.order,
        "objectives": [o.objective for o in l.objectives]
    }
    if include_content:
        if l.article:
            data["article"] = serialize_article(l.article)
        data["simulations"] = [serialize_simulation(s) for s in l.simulations]
        data["problems"] = [serialize_problem(p, include_choices=False) for p in l.problems]
    return data


def serialize_article(a):
    return {
        "id": a.id,
        "lesson_id": a.lesson_id,
        "content_type": a.content_type,
        "content": a.content,
        "summary": a.summary,
        "key_concepts": a.key_concepts or [],
        "related_formulas": a.related_formulas or [],
        "reading_time": a.reading_time
    }


def serialize_simulation(s):
    return {
        "id": s.id,
        "name": s.name,
        "type": s.type,
        "description": s.description,
        "canvas_width": s.canvas_width,
        "canvas_height": s.canvas_height,
        "config": s.config or {},
        "controls": [serialize_control(c) for c in s.controls],
        "results": [serialize_result(r) for r in s.results]
    }


def serialize_control(c):
    return {
        "id": c.id,
        "name": c.name,
        "label": c.label,
        "type": c.control_type,
        "min": c.min_value,
        "max": c.max_value,
        "default": c.default_value,
        "step": c.step,
        "unit": c.unit
    }


def serialize_result(r):
    return {
        "id": r.id,
        "name": r.name,
        "label": r.label,
        "format": r.display_format,
        "unit": r.unit
    }


def serialize_problem(p, include_choices=False):
    data = {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "difficulty": p.difficulty,
        "problem_type": p.problem_type,
        "solution_steps": p.solution_steps or [],
        "formula": p.formula,
        "explanation": p.explanation
    }
    if include_choices:
        data["choices"] = [
            {"value": c.value, "text": c.text} 
            for c in p.choices
        ]
    return data


def serialize_progress(p):
    return {
        "lesson_id": p.lesson_id,
        "progress_percent": p.progress_percent,
        "objectives_completed": json.loads(p.objectives_completed) if p.objectives_completed else [],
        "problems_solved": json.loads(p.problems_solved) if p.problems_solved else [],
        "simulation_completed": p.simulation_completed,
        "time_spent_seconds": p.time_spent_seconds,
        "last_accessed": p.last_accessed.isoformat() if p.last_accessed else None,
        "completed_at": p.completed_at.isoformat() if p.completed_at else None
    }


def serialize_bookmark(b):
    return {
        "id": b.id,
        "lesson_id": b.lesson_id,
        "notes": b.notes,
        "created_at": b.created_at.isoformat()
    }


def serialize_help_category(c):
    return {
        "id": c.id,
        "title": c.title,
        "slug": c.slug,
        "icon": c.icon,
        "description": c.description
    }


def serialize_help_article(a, include_content=False):
    data = {
        "id": a.id,
        "category_id": a.category_id,
        "title": a.title,
        "slug": a.slug,
        "summary": a.summary,
        "views": a.views
    }
    if include_content:
        data["content"] = a.content
    return data


def calculate_simulation_results(simulation, params):
    """Calculate simulation results based on type"""
    sim_type = simulation.type
    
    if sim_type == "ohms-law":
        voltage = float(params.get("voltage", 12))
        resistance = float(params.get("resistance", 100))
        current = voltage / resistance
        power = voltage * current
        return {
            "current": round(current, 3),
            "power": round(power, 2)
        }
    
    elif sim_type == "series-circuit":
        r1 = float(params.get("r1", 100))
        r2 = float(params.get("r2", 200))
        r3 = float(params.get("r3", 300))
        voltage = float(params.get("vsource", 12))
        r_total = r1 + r2 + r3
        current = voltage / r_total
        return {
            "r_total": r_total,
            "current": round(current * 1000, 2),
            "v1": round(current * r1, 2),
            "v2": round(current * r2, 2),
            "v3": round(current * r3, 2)
        }
    
    elif sim_type == "parallel-circuit":
        r1 = float(params.get("r1", 100))
        r2 = float(params.get("r2", 200))
        r3 = float(params.get("r3", 300))
        voltage = float(params.get("vsource", 12))
        r_parallel = 1 / (1/r1 + 1/r2 + 1/r3)
        i_total = voltage / r_parallel
        return {
            "r_total": round(r_parallel, 2),
            "i_total": round(i_total * 1000, 2),
            "i1": round(voltage / r1 * 1000, 2),
            "i2": round(voltage / r2 * 1000, 2),
            "i3": round(voltage / r3 * 1000, 2)
        }
    
    elif sim_type == "beam-analysis":
        load = float(params.get("load", 10))
        span = float(params.get("span", 6))
        m_max = (load * span * span) / 8
        return {
            "m_max": round(m_max, 2),
            "ra": round(load * span / 2, 2),
            "rb": round(load * span / 2, 2)
        }
    
    return {}


def check_problem_answer(problem, user_answer):
    """Check if user's answer is correct"""
    if problem.problem_type == "numerical":
        try:
            user_val = float(user_answer)
            correct_val = float(problem.correct_answer)
            tolerance = problem.tolerance or 0.01
            return abs(user_val - correct_val) <= tolerance
        except ValueError:
            return False
    else:
        return user_answer.lower().strip() == problem.correct_answer.lower().strip()


# Import models at the end to avoid circular imports
from learning.models import (
    Discipline, Chapter, Lesson, Article, Simulation,
    SimulationControl, SimulationResult, PracticeProblem,
    ProblemChoice, UserProgress, UserBookmark, HelpCategory, HelpArticle
)