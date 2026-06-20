"""Recommendation engine.

Combines two lightweight, dependency-free strategies:

1. Content-based filtering: score candidate books by how well their genre and
   author match the genres/authors the member has borrowed before.
2. Collaborative filtering (item co-occurrence): members who borrowed the same
   books as this member also borrowed these other books.

Scores from both strategies are normalised to [0, 1] and blended. When a member
has no borrowing history we fall back to globally popular books.
"""

from collections import Counter, defaultdict

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import Book, Loan

CONTENT_WEIGHT = 0.6
COLLAB_WEIGHT = 0.4
GENRE_MATCH = 1.0
AUTHOR_MATCH = 1.5


def _normalise(scores: dict[int, float]) -> dict[int, float]:
    if not scores:
        return {}
    top = max(scores.values())
    if top <= 0:
        return {k: 0.0 for k in scores}
    return {k: v / top for k, v in scores.items()}


def _content_scores(
    db: Session, borrowed_book_ids: set[int], candidates: list[Book]
) -> dict[int, float]:
    if not borrowed_book_ids:
        return {}
    borrowed_books = db.scalars(
        select(Book).where(Book.id.in_(borrowed_book_ids))
    ).all()
    genre_counts = Counter(b.genre for b in borrowed_books)
    author_counts = Counter(b.author for b in borrowed_books)

    scores: dict[int, float] = {}
    for book in candidates:
        score = 0.0
        if book.genre in genre_counts:
            score += GENRE_MATCH * genre_counts[book.genre]
        if book.author in author_counts:
            score += AUTHOR_MATCH * author_counts[book.author]
        if score > 0:
            scores[book.id] = score
    return scores


def _collaborative_scores(
    db: Session, member_id: int, borrowed_book_ids: set[int]
) -> dict[int, float]:
    if not borrowed_book_ids:
        return {}
    # Members who share at least one borrowed book with us (the "neighbours").
    neighbour_ids = set(
        db.scalars(
            select(Loan.member_id)
            .where(Loan.book_id.in_(borrowed_book_ids), Loan.member_id != member_id)
            .distinct()
        ).all()
    )
    if not neighbour_ids:
        return {}

    # Count how many neighbours borrowed each candidate book.
    scores: dict[int, float] = defaultdict(float)
    rows = db.execute(
        select(Loan.book_id, func.count(func.distinct(Loan.member_id)))
        .where(Loan.member_id.in_(neighbour_ids))
        .group_by(Loan.book_id)
    ).all()
    for book_id, count in rows:
        if book_id not in borrowed_book_ids:
            scores[book_id] = float(count)
    return dict(scores)


def _popular_fallback(db: Session, limit: int) -> list[dict]:
    stmt = (
        select(Book, func.count(Loan.id).label("loan_count"))
        .join(Loan, Loan.book_id == Book.id, isouter=True)
        .where(Book.available_copies > 0)
        .group_by(Book.id)
        .order_by(func.count(Loan.id).desc(), Book.title)
        .limit(limit)
    )
    out = []
    for book, loan_count in db.execute(stmt).all():
        reason = (
            f"Popular pick — borrowed {loan_count} times"
            if loan_count
            else "New to the catalog"
        )
        out.append({"book": book, "score": 1.0, "reason": reason})
    return out


def recommend_for_member(db: Session, member_id: int, limit: int = 8) -> list[dict]:
    borrowed_book_ids = set(
        db.scalars(select(Loan.book_id).where(Loan.member_id == member_id)).all()
    )

    if not borrowed_book_ids:
        return _popular_fallback(db, limit)

    candidates = db.scalars(
        select(Book).where(
            Book.id.notin_(borrowed_book_ids), Book.available_copies > 0
        )
    ).all()
    candidate_map = {b.id: b for b in candidates}

    content = _normalise(_content_scores(db, borrowed_book_ids, candidates))
    collab_raw = _collaborative_scores(db, member_id, borrowed_book_ids)
    collab = _normalise({k: v for k, v in collab_raw.items() if k in candidate_map})

    blended: dict[int, float] = defaultdict(float)
    for book_id, score in content.items():
        blended[book_id] += CONTENT_WEIGHT * score
    for book_id, score in collab.items():
        blended[book_id] += COLLAB_WEIGHT * score

    if not blended:
        return _popular_fallback(db, limit)

    ranked = sorted(blended.items(), key=lambda kv: kv[1], reverse=True)[:limit]

    results = []
    for book_id, score in ranked:
        book = candidate_map[book_id]
        reasons = []
        if content.get(book_id, 0) > 0:
            reasons.append(f"matches your taste in {book.genre}")
        if collab.get(book_id, 0) > 0:
            reasons.append("readers like you also borrowed it")
        reason = "Recommended because it " + " and ".join(reasons) if reasons else "Recommended for you"
        results.append({"book": book, "score": round(score, 3), "reason": reason})
    return results


def similar_books(db: Session, book_id: int, limit: int = 6) -> list[dict]:
    """Content-based 'more like this' for a single book."""
    book = db.get(Book, book_id)
    if not book:
        return []
    candidates = db.scalars(select(Book).where(Book.id != book_id)).all()
    scored = []
    for cand in candidates:
        score = 0.0
        if cand.author == book.author:
            score += AUTHOR_MATCH
        if cand.genre == book.genre:
            score += GENRE_MATCH
        if score > 0:
            reason_parts = []
            if cand.author == book.author:
                reason_parts.append(f"same author ({book.author})")
            if cand.genre == book.genre:
                reason_parts.append(f"same genre ({book.genre})")
            scored.append(
                {"book": cand, "score": score, "reason": "Similar: " + ", ".join(reason_parts)}
            )
    scored.sort(key=lambda r: r["score"], reverse=True)
    top = scored[:limit]
    if top:
        max_score = max(r["score"] for r in top)
        for r in top:
            r["score"] = round(r["score"] / max_score, 3)
    return top
