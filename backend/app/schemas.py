from datetime import datetime, date

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ----- Book -----
class BookBase(BaseModel):
    title: str
    author: str
    genre: str
    isbn: str
    description: str = ""
    published_year: int = 2000
    total_copies: int = Field(default=1, ge=1)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    genre: str | None = None
    isbn: str | None = None
    description: str | None = None
    published_year: int | None = None
    total_copies: int | None = Field(default=None, ge=1)


class BookOut(BookBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    available_copies: int
    created_at: datetime


# ----- Member -----
class MemberBase(BaseModel):
    name: str
    email: EmailStr


class MemberCreate(MemberBase):
    pass


class MemberOut(MemberBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    joined_at: datetime


# ----- Loan -----
class LoanCreate(BaseModel):
    book_id: int
    member_id: int
    loan_days: int = Field(default=14, ge=1, le=90)


class LoanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    book_id: int
    member_id: int
    borrowed_at: datetime
    due_date: date
    returned_at: datetime | None


class LoanDetail(LoanOut):
    book_title: str
    book_author: str
    member_name: str
    is_overdue: bool


# ----- Recommendations -----
class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    book: BookOut
    score: float
    reason: str
