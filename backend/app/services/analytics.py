from collections import defaultdict
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Book, Loan, Member


def get_summary(db: Session) -> dict:
    total_books = db.scalar(select(func.count(Book.id))) or 0
    total_copies = db.scalar(select(func.coalesce(func.sum(Book.total_copies), 0))) or 0
    available_copies = (
        db.scalar(select(func.coalesce(func.sum(Book.available_copies), 0))) or 0
    )
    total_members = db.scalar(select(func.count(Member.id))) or 0
    total_loans = db.scalar(select(func.count(Loan.id))) or 0
    active_loans = (
        db.scalar(select(func.count(Loan.id)).where(Loan.returned_at.is_(None))) or 0
    )
    overdue_loans = (
        db.scalar(
            select(func.count(Loan.id)).where(
                Loan.returned_at.is_(None), Loan.due_date < date.today()
            )
        )
        or 0
    )
    return {
        "total_books": total_books,
        "total_copies": int(total_copies),
        "available_copies": int(available_copies),
        "books_on_loan": int(total_copies) - int(available_copies),
        "total_members": total_members,
        "total_loans": total_loans,
        "active_loans": active_loans,
        "overdue_loans": overdue_loans,
    }


def get_popular_books(db: Session, limit: int = 10) -> list[dict]:
    stmt = (
        select(Book, func.count(Loan.id).label("loan_count"))
        .join(Loan, Loan.book_id == Book.id)
        .group_by(Book.id)
        .order_by(func.count(Loan.id).desc())
        .limit(limit)
    )
    results = []
    for book, loan_count in db.execute(stmt).all():
        results.append(
            {
                "id": book.id,
                "title": book.title,
                "author": book.author,
                "genre": book.genre,
                "loan_count": loan_count,
            }
        )
    return results


def get_genre_distribution(db: Session) -> list[dict]:
    """Loans grouped by genre — what subjects members actually read."""
    stmt = (
        select(Book.genre, func.count(Loan.id).label("loan_count"))
        .join(Loan, Loan.book_id == Book.id)
        .group_by(Book.genre)
        .order_by(func.count(Loan.id).desc())
    )
    return [
        {"genre": genre, "loan_count": loan_count}
        for genre, loan_count in db.execute(stmt).all()
    ]


def get_loan_trends(db: Session, weeks: int = 12) -> list[dict]:
    """Loans per week for the last `weeks` weeks."""
    today = date.today()
    start = today - timedelta(weeks=weeks - 1)
    start = start - timedelta(days=start.weekday())  # align to Monday

    loans = db.scalars(
        select(Loan).where(func.date(Loan.borrowed_at) >= start.isoformat())
    ).all()

    buckets: dict[date, int] = defaultdict(int)
    for loan in loans:
        borrowed = loan.borrowed_at
        if isinstance(borrowed, datetime):
            borrowed = borrowed.date()
        week_start = borrowed - timedelta(days=borrowed.weekday())
        buckets[week_start] += 1

    trends = []
    cursor = start
    while cursor <= today:
        trends.append(
            {"week": cursor.isoformat(), "loan_count": buckets.get(cursor, 0)}
        )
        cursor += timedelta(weeks=1)
    return trends


def get_top_members(db: Session, limit: int = 5) -> list[dict]:
    stmt = (
        select(Member, func.count(Loan.id).label("loan_count"))
        .join(Loan, Loan.member_id == Member.id)
        .group_by(Member.id)
        .order_by(func.count(Loan.id).desc())
        .limit(limit)
    )
    return [
        {
            "id": member.id,
            "name": member.name,
            "email": member.email,
            "loan_count": loan_count,
        }
        for member, loan_count in db.execute(stmt).all()
    ]
