# Smart Library Management System

A web-based smart library management system with an **analytics dashboard** and a
**recommendation engine**. Manage a book catalog, members and loans, visualize
library activity, and surface personalized book recommendations.

## Features

- **Book Catalog** — full CRUD, search by title/author/ISBN, filter by genre and
  availability, copy tracking.
- **Members** — register and manage library members.
- **Loans** — borrow and return books with due dates and automatic overdue
  detection; availability updates automatically.
- **Analytics Dashboard** — KPI cards (titles, copies, active/overdue loans,
  members) plus charts: loan trends over time, most-borrowed titles, loans by
  genre, and top members.
- **Recommendation Engine** — personalized per-member recommendations combining:
  - *Content-based filtering* — genre/author affinity from a member's history.
  - *Collaborative filtering* — item co-occurrence ("readers like you also
    borrowed…").
  - *Popularity fallback* — for members with no history.
  - Plus "more like this" similar-book suggestions for any title.

## Tech Stack

| Layer    | Technology                              |
| -------- | --------------------------------------- |
| Backend  | FastAPI, SQLAlchemy 2, SQLite, Pydantic |
| Frontend | React 18, Vite, React Router, Recharts  |

## Project Structure

```
smart-library-system/
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI app + startup seeding
│   │   ├── database.py        # SQLAlchemy engine/session
│   │   ├── models.py          # Book, Member, Loan ORM models
│   │   ├── schemas.py         # Pydantic schemas
│   │   ├── seed.py            # Sample data seeding
│   │   ├── routers/           # books, members, loans, analytics, recommendations
│   │   └── services/          # analytics + recommendation logic
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── api.js             # API client
    │   ├── App.jsx            # Layout + routes
    │   ├── pages/             # Dashboard, Catalog, Loans, Members, Recommendations
    │   └── components/
    └── package.json
```

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

The database (`backend/library.db`) is created and seeded with sample books,
members and loans automatically on first run. API docs are available at
http://127.0.0.1:8000/docs.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api` requests to the
backend on port 8000.

## API Overview

| Method | Endpoint                                    | Description                       |
| ------ | ------------------------------------------- | --------------------------------- |
| GET    | `/api/books`                                | List/search/filter books          |
| POST   | `/api/books`                                | Create a book                     |
| PUT    | `/api/books/{id}`                           | Update a book                     |
| DELETE | `/api/books/{id}`                           | Delete a book                     |
| GET    | `/api/members`                              | List members                      |
| POST   | `/api/members`                              | Register a member                 |
| GET    | `/api/loans`                                | List loans (active/overdue flags) |
| POST   | `/api/loans`                                | Borrow a book                     |
| POST   | `/api/loans/{id}/return`                    | Return a book                     |
| GET    | `/api/analytics/summary`                    | KPI summary                       |
| GET    | `/api/analytics/popular-books`              | Most borrowed titles              |
| GET    | `/api/analytics/genre-distribution`         | Loans grouped by genre            |
| GET    | `/api/analytics/loan-trends`                | Weekly loan counts                |
| GET    | `/api/analytics/top-members`                | Most active members               |
| GET    | `/api/recommendations/member/{id}`          | Personalized recommendations      |
| GET    | `/api/recommendations/book/{id}/similar`    | Similar books                     |

## Resetting the Database

Stop the backend and delete `backend/library.db`. It will be recreated and
reseeded on the next start.
