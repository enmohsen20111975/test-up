from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth.router import get_current_user
from auth.models import User
from ai.deepseek_client import DeepSeekClient
from ai.qwen_client import QwenClient
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/ai", tags=["ai"])

class ExplainRequest(BaseModel):
    calc_type: str
    inputs: Dict[str, Any]
    results: Dict[str, Any]

class AnalyzeRequest(BaseModel):
    dataset_summary: str
    chart_type: str = "bar"

class ReportRequest(BaseModel):
    calc_results: Dict[str, Any]
    analysis_data: str
    template: str = "professional"

class ChatRequest(BaseModel):
    message: str
    context: str = ""

async def get_ai_response(func, *args, **kwargs):
    """Get AI response with fallback"""
    deepseek_client = DeepSeekClient()
    qwen_client = QwenClient()
    
    try:
        result = await func(deepseek_client, *args, **kwargs)
        if result:
            return result
    except Exception as e:
        print(f"DeepSeek failed: {e}")
    
    try:
        result = await func(qwen_client, *args, **kwargs)
        if result:
            return result
    except Exception as e:
        print(f"Qwen failed: {e}")
    
    return "تعذر الحصول على استجابة AI. يرجى المحاولة مرة أخرى."

@router.post("/explain")
async def explain_calculation(
    request: ExplainRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        response = await get_ai_response(
            lambda client, req: client.explain_calculation(req.calc_type, req.inputs, req.results),
            request
        )
        
        return {"explanation": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze")
async def analyze_data(
    request: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        response = await get_ai_response(
            lambda client, req: client.analyze_data(req.dataset_summary),
            request
        )
        
        return {"analysis": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/report")
async def generate_report(
    request: ReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        response = await get_ai_response(
            lambda client, req: client.generate_report(req.calc_results, req.analysis_data, req.template),
            request
        )
        
        return {"report": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        response = await get_ai_response(
            lambda client, req: client.chat(req.message, req.context),
            request
        )
        
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))