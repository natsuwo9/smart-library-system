from datetime import datetime, date

from sqlalchemy import String, Integer, ForeignKey, DateTime, Date, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    author: Mapped[str] = mapped_column(String(255), index=True)
    genre: Mapped[str] = mapped_column(String(100), index=True)
    isbn: Mapped[str] = mapped_column(String(20), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")
    published_year: Mapped[int] = mapped_column(Integer, default=2000)
    total_copies: Mapped[int] = mapped_column(Integer, default=1)
    available_copies: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    loans: Mapped[list["Loan"]] = relationship(back_populates="book")


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    loans: Mapped[list["Loan"]] = relationship(back_populates="member")


class Loan(Base):
    __tablename__ = "loans"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id"), index=True)
    borrowed_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    due_date: Mapped[date] = mapped_column(Date)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    book: Mapped["Book"] = relationship(back_populates="loans")
    member: Mapped["Member"] = relationship(back_populates="loans")
