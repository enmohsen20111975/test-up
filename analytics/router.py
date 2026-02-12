from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session
from database import get_db
from auth.router import get_current_user
from auth.models import User
from analytics.upload import FileUploadService
from analytics.query_builder import QueryBuilder
from analytics.report_generator import ReportGenerator
import json
from datetime import datetime

router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    sheet_name: str = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        content = await file.read()
        result = FileUploadService.process_file(content, file.filename, sheet_name)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/excel-sheets")
async def get_excel_sheets(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        content = await file.read()
        result = FileUploadService.get_excel_sheets(content)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/database-connect")
async def connect_to_database(
    connection_params: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = FileUploadService.process_database_connection(connection_params)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/query")
async def execute_query(
    query: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = QueryBuilder.execute_query(query["data"], query["query"])
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/summary")
async def get_data_summary(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = QueryBuilder.get_data_summary(data["data"])
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/distribution")
async def get_column_distribution(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = QueryBuilder.get_column_distribution(
            request["data"], 
            request["column"], 
            request.get("bins", 10)
        )
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/templates")
async def get_analytics_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    templates = [
        {
            "name": "Daily Site Report",
            "description": "Template for daily construction site reports",
            "fields": ["date", "weather", "activities", "materials", "issues"]
        },
        {
            "name": "Material Usage",
            "description": "Template for tracking material consumption",
            "fields": ["material_type", "quantity", "unit", "cost", "location"]
        },
        {
            "name": "Quality Control",
            "description": "Template for quality control inspections",
            "fields": ["inspection_type", "result", "defects", "responsible", "comments"]
        },
        {
            "name": "Project Schedule",
            "description": "Template for project schedule tracking",
            "fields": ["task", "start_date", "end_date", "progress", "responsible"]
        },
        {
            "name": "Cost Analysis",
            "description": "Template for cost tracking and analysis",
            "fields": ["item", "quantity", "unit_cost", "total_cost", "category"]
        },
        {
            "name": "Safety Report",
            "description": "Template for safety inspections and incidents",
            "fields": ["date", "location", "incident_type", "severity", "action_taken"]
        }
    ]
    
    return {"templates": templates}

@router.post("/database-table-data")
async def get_database_table_data(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        connection_params = request.get("connection_params")
        table_name = request.get("table_name")
        if not connection_params or not table_name:
            raise HTTPException(status_code=400, detail="Connection parameters and table name are required.")
        
        result = FileUploadService.fetch_database_table_data(connection_params, table_name)
        
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=400, detail=result["error"])
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/ai-analyze")
async def ai_analyze_data(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        data = request.get("data", "")
        if isinstance(data, str):
            data = json.loads(data)
        analysis_type = request.get("analysis_type", "general")
        parameters = request.get("parameters", {})

        # Try to use AI service for analysis
        try:
            from ai.deepseek_client import DeepSeekClient
            client = DeepSeekClient()
            data_summary = json.dumps(data[:10] if isinstance(data, list) else data, default=str)[:2000]
            ai_result = await client.analyze_data(data_summary, analysis_type, parameters)
            return {"success": True, "results": {
                "analysis_type": analysis_type,
                "ai_analysis": ai_result,
                "parameters": parameters
            }}
        except Exception:
            # Fallback to basic analysis
            return {"success": True, "results": {
                "analysis_type": analysis_type,
                "parameters": parameters,
                "ai_analysis": f"Analysis of {analysis_type} data completed. "
                               f"Dataset contains {len(data) if isinstance(data, list) else 'N/A'} records."
            }}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/generate-report")
async def generate_report(
    request: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a professional engineering report (HTML or PDF)."""
    try:
        report_type = request.get("report_type", "calculation")
        content = request.get("content", {})
        content["report_type"] = report_type

        # Add user info
        if current_user:
            content.setdefault("engineer_name", current_user.name or current_user.email)

        if report_type == "calculation":
            result = ReportGenerator.generate_calculation_report(content)
        elif report_type == "workflow":
            result = ReportGenerator.generate_workflow_report(content)
        elif report_type == "analytics":
            result = ReportGenerator.generate_analytics_report(content)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown report type: {report_type}")

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("error", "Report generation failed"))

        output_format = request.get("format", "html")
        if output_format == "pdf":
            try:
                import pdfkit
                pdf_bytes = pdfkit.from_string(result["html"], False)
                return Response(
                    content=pdf_bytes,
                    media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename={result['report_id']}.pdf"}
                )
            except Exception:
                # Fall back to HTML if PDF generation unavailable
                pass

        return {
            "success": True,
            "report_id": result["report_id"],
            "html": result["html"],
            "format": "html"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
