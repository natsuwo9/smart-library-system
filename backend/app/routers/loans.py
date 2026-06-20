from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..models import Book, Loan, Member
from ..schemas import LoanCreate, LoanDetail, LoanOut

router = APIRouter(prefix="/api/loans", tags=["loans"])


def _to_detail(loan: Loan) -> LoanDetail:
    is_overdue = loan.returned_at is None and loan.due_date < date.today()
    return LoanDetail(
        id=loan.id,
        book_id=loan.book_id,
        member_id=loan.member_id,
        borrowed_at=loan.borrowed_at,
        due_date=loan.due_date,
        returned_at=loan.returned_at,
        book_title=loan.book.title,
        book_author=loan.book.author,
        member_name=loan.member.name,
        is_overdue=is_overdue,
    )


@router.get("", response_model=list[LoanDetail])
def list_loans(
    active_only: bool = Query(default=False),
    member_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Loan).options(joinedload(Loan.book), joinedload(Loan.member))
    if active_only:
        stmt = stmt.where(Loan.returned_at.is_(None))
    if member_id is not None:
        stmt = stmt.where(Loan.member_id == member_id)
    stmt = stmt.order_by(Loan.borrowed_at.desc())
    return [_to_detail(loan) for loan in db.scalars(stmt).all()]


@router.post("", response_model=LoanOut, status_code=201)
def create_loan(payload: LoanCreate, db: Session = Depends(get_db)):
    book = db.get(Book, payload.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    member = db.get(Member, payload.member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    if book.available_copies < 1:
        raise HTTPException(status_code=400, detail="No copies available")

    loan = Loan(
        book_id=payload.book_id,
        member_id=payload.member_id,
        borrowed_at=datetime.now(),
        due_date=date.today() + timedelta(days=payload.loan_days),
    )
    book.available_copies -= 1
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


@router.post("/{loan_id}/return", response_model=LoanOut)
def return_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = db.get(Loan, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.returned_at is not None:
        raise HTTPException(status_code=400, detail="Loan already returned")
    loan.returned_at = datetime.now()
    book = db.get(Book, loan.book_id)
    if book:
        book.available_copies = min(book.available_copies + 1, book.total_copies)
    db.commit()
    db.refresh(loan)
    return loan
