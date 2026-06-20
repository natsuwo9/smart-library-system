import { useCallback, useEffect, useState } from "react";
import {
  getBooks,
  getGenres,
  createBook,
  updateBook,
  deleteBook,
  getSimilarBooks,
} from "../api";
import Modal from "../components/Modal.jsx";

const EMPTY = {
  title: "",
  author: "",
  genre: "",
  isbn: "",
  description: "",
  published_year: 2020,
  total_copies: 1,
};

function BookForm({ initial, onSubmit, onClose, error }) {
  const [form, setForm] = useState(initial);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  const submit = (e) => {
    e.preventDefault();
    onSubmit({
      ...form,
      published_year: Number(form.published_year),
      total_copies: Number(form.total_copies),
    });
  };

  return (
    <form onSubmit={submit}>
      {error && <div className="error-banner">{error}</div>}
      <div className="form-row">
        <div className="field">
          <label>Title</label>
          <input value={form.title} onChange={set("title")} required />
        </div>
        <div className="field">
          <label>Author</label>
          <input value={form.author} onChange={set("author")} required />
        </div>
      </div>
      <div className="form-row">
        <div className="field">
          <label>Genre</label>
          <input value={form.genre} onChange={set("genre")} required />
        </div>
        <div className="field">
          <label>ISBN</label>
          <input value={form.isbn} onChange={set("isbn")} required />
        </div>
      </div>
      <div className="form-row">
        <div className="field">
          <label>Published Year</label>
          <input
            type="number"
            value={form.published_year}
            onChange={set("published_year")}
          />
        </div>
        <div className="field">
          <label>Total Copies</label>
          <input
            type="number"
            min="1"
            value={form.total_copies}
            onChange={set("total_copies")}
          />
        </div>
      </div>
      <div className="field">
        <label>Description</label>
        <textarea rows="3" value={form.description} onChange={set("description")} />
      </div>
      <div className="modal-actions">
        <button type="button" className="btn secondary" onClick={onClose}>
          Cancel
        </button>
        <button type="submit" className="btn">
          Save
        </button>
      </div>
    </form>
  );
}

export default function Catalog() {
  const [books, setBooks] = useState([]);
  const [genres, setGenres] = useState([]);
  const [search, setSearch] = useState("");
  const [genre, setGenre] = useState("");
  const [availableOnly, setAvailableOnly] = useState(false);
  const [editing, setEditing] = useState(null); // book object or {} for new
  const [formError, setFormError] = useState("");
  const [similar, setSimilar] = useState(null); // { book, items }
  const [error, setError] = useState("");

  const load = useCallback(() => {
    getBooks({
      search: search || undefined,
      genre: genre || undefined,
      available_only: availableOnly || undefined,
    })
      .then(setBooks)
      .catch((e) => setError(e.message));
  }, [search, genre, availableOnly]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    getGenres().then(setGenres).catch(() => {});
  }, []);

  const refreshGenres = () => getGenres().then(setGenres).catch(() => {});

  const handleSubmit = async (payload) => {
    setFormError("");
    try {
      if (editing.id) {
        await updateBook(editing.id, payload);
      } else {
        await createBook(payload);
      }
      setEditing(null);
      load();
      refreshGenres();
    } catch (e) {
      setFormError(e.response?.data?.detail || e.message);
    }
  };

  const handleDelete = async (book) => {
    if (!window.confirm(`Delete "${book.title}"?`)) return;
    try {
      await deleteBook(book.id);
      load();
    } catch (e) {
      window.alert(e.response?.data?.detail || e.message);
    }
  };

  const showSimilar = async (book) => {
    const items = await getSimilarBooks(book.id, 6);
    setSimilar({ book, items });
  };

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Book Catalog</h1>
          <p>{books.length} titles shown</p>
        </div>
        <button className="btn" onClick={() => setEditing({ ...EMPTY })}>
          + Add Book
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="toolbar">
        <input
          placeholder="Search title, author, ISBN…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <select value={genre} onChange={(e) => setGenre(e.target.value)}>
          <option value="">All genres</option>
          {genres.map((g) => (
            <option key={g} value={g}>
              {g}
            </option>
          ))}
        </select>
        <label className="muted" style={{ display: "flex", gap: 6, alignItems: "center" }}>
          <input
            type="checkbox"
            style={{ width: "auto" }}
            checked={availableOnly}
            onChange={(e) => setAvailableOnly(e.target.checked)}
          />
          Available only
        </label>
      </div>

      {books.length === 0 ? (
        <div className="card empty">No books match your filters.</div>
      ) : (
        <div className="grid book-grid">
          {books.map((b) => (
            <div key={b.id} className="card book-card">
              <div className="title">{b.title}</div>
              <div className="author">by {b.author}</div>
              <div>
                <span className="badge genre">{b.genre}</span>{" "}
                <span className="muted" style={{ fontSize: 13 }}>{b.published_year}</span>
              </div>
              <div className="meta">
                <span
                  className={`badge ${b.available_copies > 0 ? "success" : "danger"}`}
                >
                  {b.available_copies}/{b.total_copies} available
                </span>
              </div>
              <div className="actions">
                <button className="btn secondary small" onClick={() => setEditing(b)}>
                  Edit
                </button>
                <button className="btn secondary small" onClick={() => showSimilar(b)}>
                  Similar
                </button>
                <button className="btn danger small" onClick={() => handleDelete(b)}>
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {editing && (
        <Modal
          title={editing.id ? "Edit Book" : "Add Book"}
          onClose={() => {
            setEditing(null);
            setFormError("");
          }}
        >
          <BookForm
            initial={editing.id ? { ...EMPTY, ...editing } : { ...EMPTY }}
            onSubmit={handleSubmit}
            onClose={() => {
              setEditing(null);
              setFormError("");
            }}
            error={formError}
          />
        </Modal>
      )}

      {similar && (
        <Modal
          title={`Similar to "${similar.book.title}"`}
          onClose={() => setSimilar(null)}
        >
          {similar.items.length === 0 ? (
            <p className="muted">No similar books found.</p>
          ) : (
            <div className="grid" style={{ gap: 12 }}>
              {similar.items.map((r) => (
                <div key={r.book.id} className="card rec-card">
                  <div className="title" style={{ fontSize: 15 }}>
                    {r.book.title}
                  </div>
                  <div className="author">by {r.book.author}</div>
                  <div className="reason">{r.reason}</div>
                </div>
              ))}
            </div>
          )}
        </Modal>
      )}
    </>
  );
}
