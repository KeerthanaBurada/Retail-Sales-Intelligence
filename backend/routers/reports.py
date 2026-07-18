import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db
from models.user import User
from models.forecast import SavedReport
from services.report_service import ReportService
from middleware.auth_middleware import get_current_user


class GenerateReportRequest(BaseModel):
    dataset_id: int
    title: str
    report_type: str = 'summary'


router = APIRouter(prefix='/api/reports', tags=['Reports'])


@router.post('/generate')
def generate_report(
    request: GenerateReportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a new report for the specified dataset."""
    report = ReportService.generate_report(
        db, request.dataset_id, current_user.id, request.title, request.report_type
    )
    return {
        'id': report.id,
        'title': report.title,
        'report_type': report.report_type,
        'created_at': report.created_at.isoformat()
    }


@router.get('/')
def list_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all reports belonging to the current user."""
    reports = (
        db.query(SavedReport)
        .filter(SavedReport.user_id == current_user.id)
        .order_by(SavedReport.created_at.desc())
        .all()
    )
    return [
        {
            'id': r.id,
            'title': r.title,
            'report_type': r.report_type,
            'created_at': r.created_at.isoformat()
        }
        for r in reports
    ]


@router.get('/{report_id}/download')
def download_report(
    report_id: int,
    format: str = Query('csv'),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download a report in CSV or PDF format."""
    report = (
        db.query(SavedReport)
        .filter(SavedReport.id == report_id, SavedReport.user_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(404, detail='Report not found')

    if format == 'pdf':
        content = ReportService.export_pdf(report)
        return StreamingResponse(
            io.BytesIO(content),
            media_type='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="{report.title}.pdf"'}
        )
    else:
        content = ReportService.export_csv(report)
        return StreamingResponse(
            io.BytesIO(content),
            media_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="{report.title}.csv"'}
        )


@router.delete('/{report_id}')
def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a report."""
    report = (
        db.query(SavedReport)
        .filter(SavedReport.id == report_id, SavedReport.user_id == current_user.id)
        .first()
    )
    if not report:
        raise HTTPException(404, detail='Report not found')

    db.delete(report)
    db.commit()
    return {'message': 'Report deleted successfully'}
