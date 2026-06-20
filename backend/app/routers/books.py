from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Book, Loan
from ..schemas import BookCreate, BookOut, BookUpdate

router = APIRouter(prefix="/api/books", tags=["books"])


@router.get("", response_model=list[BookOut])
def list_books(
    search: str | None = Query(default=None),
    genre: str | None = Query(default=None),
    available_only: bool = Query(default=False),
    db: Session = Depends(get_db),
):
    stmt = select(Book)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(
            or_(Book.title.ilike(like), Book.author.ilike(like), Book.isbn.ilike(like))
        )
    if genre:
        stmt = stmt.where(Book.genre == genre)
    if available_only:
        stmt = stmt.where(Book.available_copies > 0)
    stmt = stmt.order_by(Book.title)
    return db.scalars(stmt).all()


@router.get("/genres", response_model=list[str])
def list_genres(db: Session = Depends(get_db)):
    rows = db.scalars(select(Book.genre).distinct().order_by(Book.genre)).all()
    return list(rows)


@router.get("/{book_id}", response_model=BookOut)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.post("", response_model=BookOut, status_code=201)
def create_book(payload: BookCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(Book).where(Book.isbn == payload.isbn))
    if existing:
        raise HTTPException(status_code=400, detail="A book with this ISBN already exists")
    book = Book(
        **payload.model_dump(),
        available_copies=payload.total_copies,
    )
    db.add(book)
    db.commit()
    db.refresh(book)
    return book


@router.put("/{book_id}", response_model=BookOut)
def update_book(book_id: int, payload: BookUpdate, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    data = payload.model_dump(exclude_unset=True)
    if "total_copies" in data:
        borrowed = book.total_copies - book.available_copies
        if data["total_copies"] < borrowed:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot set total copies below {borrowed} (currently borrowed)",
            )
        book.available_copies = data["total_copies"] - borrowed
    for key, value in data.items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.get(Book, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    active = db.scalar(
        select(Loan).where(Loan.book_id == book_id, Loan.returned_at.is_(None))
    )
    if active:
        raise HTTPException(
            status_code=400, detail="Cannot delete a book with active loans"
        )
    db.execute(Loan.__table__.delete().where(Loan.book_id == book_id))
    db.delete(book)
    db.commit()
