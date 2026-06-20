from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Loan, Member
from ..schemas import MemberCreate, MemberOut

router = APIRouter(prefix="/api/members", tags=["members"])


@router.get("", response_model=list[MemberOut])
def list_members(db: Session = Depends(get_db)):
    return db.scalars(select(Member).order_by(Member.name)).all()


@router.get("/{member_id}", response_model=MemberOut)
def get_member(member_id: int, db: Session = Depends(get_db)):
    member = db.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.post("", response_model=MemberOut, status_code=201)
def create_member(payload: MemberCreate, db: Session = Depends(get_db)):
    existing = db.scalar(select(Member).where(Member.email == payload.email))
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    member = Member(name=payload.name, email=payload.email)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


@router.delete("/{member_id}", status_code=204)
def delete_member(member_id: int, db: Session = Depends(get_db)):
    member = db.get(Member, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    active = db.scalar(
        select(Loan).where(Loan.member_id == member_id, Loan.returned_at.is_(None))
    )
    if active:
        raise HTTPException(
            status_code=400, detail="Cannot delete a member with active loans"
        )
    db.execute(Loan.__table__.delete().where(Loan.member_id == member_id))
    db.delete(member)
    db.commit()
