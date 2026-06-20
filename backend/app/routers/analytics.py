from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..services import analytics

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    return analytics.get_summary(db)


@router.get("/popular-books")
def popular_books(limit: int = Query(default=10, ge=1, le=50), db: Session = Depends(get_db)):
    return analytics.get_popular_books(db, limit)


@router.get("/genre-distribution")
def genre_distribution(db: Session = Depends(get_db)):
    return analytics.get_genre_distribution(db)


@router.get("/loan-trends")
def loan_trends(weeks: int = Query(default=12, ge=1, le=52), db: Session = Depends(get_db)):
    return analytics.get_loan_trends(db, weeks)


@router.get("/top-members")
def top_members(limit: int = Query(default=5, ge=1, le=50), db: Session = Depends(get_db)):
    return analytics.get_top_members(db, limit)
