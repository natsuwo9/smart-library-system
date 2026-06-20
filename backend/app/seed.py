"""Seed the database with realistic sample data on first run."""

import random
from datetime import date, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Book, Loan, Member

BOOKS = [
    ("The Pragmatic Programmer", "Andrew Hunt", "Technology", "9780201616224", 1999),
    ("Clean Code", "Robert C. Martin", "Technology", "9780132350884", 2008),
    ("The Mythical Man-Month", "Frederick P. Brooks Jr.", "Technology", "9780201835953", 1975),
    ("Designing Data-Intensive Applications", "Martin Kleppmann", "Technology", "9781449373320", 2017),
    ("Introduction to Algorithms", "Thomas H. Cormen", "Technology", "9780262033848", 2009),
    ("Sapiens", "Yuval Noah Harari", "History", "9780062316097", 2011),
    ("Guns, Germs, and Steel", "Jared Diamond", "History", "9780393317558", 1997),
    ("The Silk Roads", "Peter Frankopan", "History", "9781101912379", 2015),
    ("SPQR: A History of Ancient Rome", "Mary Beard", "History", "9781631492228", 2015),
    ("Dune", "Frank Herbert", "Science Fiction", "9780441013593", 1965),
    ("Neuromancer", "William Gibson", "Science Fiction", "9780441569595", 1984),
    ("The Left Hand of Darkness", "Ursula K. Le Guin", "Science Fiction", "9780441478125", 1969),
    ("Foundation", "Isaac Asimov", "Science Fiction", "9780553293357", 1951),
    ("Project Hail Mary", "Andy Weir", "Science Fiction", "9780593135204", 2021),
    ("The Hobbit", "J.R.R. Tolkien", "Fantasy", "9780547928227", 1937),
    ("The Name of the Wind", "Patrick Rothfuss", "Fantasy", "9780756404741", 2007),
    ("A Game of Thrones", "George R.R. Martin", "Fantasy", "9780553103540", 1996),
    ("Mistborn: The Final Empire", "Brandon Sanderson", "Fantasy", "9780765311788", 2006),
    ("Pride and Prejudice", "Jane Austen", "Classic", "9780141439518", 1813),
    ("1984", "George Orwell", "Classic", "9780451524935", 1949),
    ("To Kill a Mockingbird", "Harper Lee", "Classic", "9780061120084", 1960),
    ("The Great Gatsby", "F. Scott Fitzgerald", "Classic", "9780743273565", 1925),
    ("Thinking, Fast and Slow", "Daniel Kahneman", "Psychology", "9780374533557", 2011),
    ("Atomic Habits", "James Clear", "Self-Help", "9780735211292", 2018),
    ("Deep Work", "Cal Newport", "Self-Help", "9781455586691", 2016),
    ("The Selfish Gene", "Richard Dawkins", "Science", "9780198788607", 1976),
    ("A Brief History of Time", "Stephen Hawking", "Science", "9780553380163", 1988),
    ("Cosmos", "Carl Sagan", "Science", "9780345539434", 1980),
    ("The Gene", "Siddhartha Mukherjee", "Science", "9781476733500", 2016),
    ("Educated", "Tara Westover", "Memoir", "9780399590504", 2018),
]

MEMBERS = [
    ("Alice Johnson", "alice.johnson@example.com"),
    ("Bob Smith", "bob.smith@example.com"),
    ("Carla Mendez", "carla.mendez@example.com"),
    ("David Chen", "david.chen@example.com"),
    ("Emma Wilson", "emma.wilson@example.com"),
    ("Frank Okafor", "frank.okafor@example.com"),
    ("Grace Park", "grace.park@example.com"),
    ("Hiro Tanaka", "hiro.tanaka@example.com"),
    ("Isabella Rossi", "isabella.rossi@example.com"),
    ("James Brown", "james.brown@example.com"),
    ("Kira Petrova", "kira.petrova@example.com"),
    ("Liam O'Brien", "liam.obrien@example.com"),
]

# Genre affinities give each member a "taste" so recommendations are meaningful.
TASTES = [
    ["Technology", "Science"],
    ["Science Fiction", "Fantasy"],
    ["History", "Classic"],
    ["Technology", "Self-Help"],
    ["Fantasy", "Classic"],
    ["Science", "Psychology"],
    ["Science Fiction", "Science"],
    ["History", "Memoir"],
    ["Classic", "Psychology"],
    ["Self-Help", "Technology"],
    ["Fantasy", "Science Fiction"],
    ["Memoir", "History"],
]


def seed_if_empty(db: Session) -> None:
    if db.scalar(select(func.count(Book.id))):
        return

    rng = random.Random(42)

    books: list[Book] = []
    for title, author, genre, isbn, year in BOOKS:
        copies = rng.randint(2, 5)
        book = Book(
            title=title,
            author=author,
            genre=genre,
            isbn=isbn,
            published_year=year,
            description=f"{title} by {author}.",
            total_copies=copies,
            available_copies=copies,
        )
        db.add(book)
        books.append(book)

    members: list[Member] = []
    for name, email in MEMBERS:
        member = Member(name=name, email=email)
        db.add(member)
        members.append(member)

    db.flush()

    books_by_genre: dict[str, list[Book]] = {}
    for book in books:
        books_by_genre.setdefault(book.genre, []).append(book)

    today = date.today()
    for member, taste in zip(members, TASTES):
        num_loans = rng.randint(4, 9)
        pool: list[Book] = []
        for genre in taste:
            pool.extend(books_by_genre.get(genre, []))
        # A little cross-genre noise.
        pool.extend(rng.sample(books, k=min(4, len(books))))

        chosen = rng.sample(pool, k=min(num_loans, len(set(b.id for b in pool))))
        seen: set[int] = set()
        for book in chosen:
            if book.id in seen:
                continue
            seen.add(book.id)
            days_ago = rng.randint(1, 80)
            borrowed_at = datetime.now() - timedelta(days=days_ago)
            loan_days = rng.choice([14, 21, 28])
            due = borrowed_at.date() + timedelta(days=loan_days)

            returned_at = None
            # ~65% of older loans returned; recent ones often still out.
            if rng.random() < 0.65 and days_ago > 7:
                returned_at = borrowed_at + timedelta(days=rng.randint(3, loan_days + 4))

            loan = Loan(
                book_id=book.id,
                member_id=member.id,
                borrowed_at=borrowed_at,
                due_date=due,
                returned_at=returned_at,
            )
            if returned_at is None:
                book.available_copies = max(0, book.available_copies - 1)
            db.add(loan)

    db.commit()
