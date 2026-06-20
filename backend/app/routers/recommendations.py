from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Book, Member
from ..schemas import RecommendationOut
from ..services import recommendations

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("/member/{member_id}", response_model=list[RecommendationOut])
def for_member(
    member_id: int,
    limit: int = Query(default=8, ge=1, le=30),
    db: Session = Depends(get_db),
):
    if not db.get(Member, member_id):
        raise HTTPException(status_code=404, detail="Member not found")
    return recommendations.recommend_for_member(db, member_id, limit)


@router.get("/book/{book_id}/similar", response_model=list[RecommendationOut])
def similar(
    book_id: int,
    limit: int = Query(default=6, ge=1, le=30),
    db: Session = Depends(get_db),
):
    if not db.get(Book, book_id):
        raise HTTPException(status_code=404, detail="Book not found")
    return recommendations.similar_books(db, book_id, limit)
