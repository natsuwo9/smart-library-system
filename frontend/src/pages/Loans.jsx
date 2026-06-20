import { useCallback, useEffect, useState } from "react";
import {
  getLoans,
  getMembers,
  getBooks,
  createLoan,
  returnLoan,
} from "../api";
import Modal from "../components/Modal.jsx";

export default function Loans() {
  const [loans, setLoans] = useState([]);
  const [activeOnly, setActiveOnly] = useState(true);
  const [members, setMembers] = useState([]);
  const [books, setBooks] = useState([]);
  const [adding, setAdding] = useState(false);
  const [form, setForm] = useState({ member_id: "", book_id: "", loan_days: 14 });
  const [formError, setFormError] = useState("");
  const [error, setError] = useState("");

  const load = useCallback(() => {
    getLoans({ active_only: activeOnly || undefined })
      .then(setLoans)
      .catch((e) => setError(e.message));
  }, [activeOnly]);

  useEffect(() => {
    load();
  }, [load]);

  const openForm = async () => {
    const [m, b] = await Promise.all([getMembers(), getBooks({ available_only: true })]);
    setMembers(m);
    setBooks(b);
    setForm({ member_id: "", book_id: "", loan_days: 14 });
    setFormError("");
    setAdding(true);
  };

  const submit = async (e) => {
    e.preventDefault();
    setFormError("");
    try {
      await createLoan({
        member_id: Number(form.member_id),
        book_id: Number(form.book_id),
        loan_days: Number(form.loan_days),
      });
      setAdding(false);
      load();
    } catch (err) {
      setFormError(err.response?.data?.detail || err.message);
    }
  };

  const handleReturn = async (loan) => {
    try {
      await returnLoan(loan.id);
      load();
    } catch (err) {
      window.alert(err.response?.data?.detail || err.message);
    }
  };

  const statusBadge = (loan) => {
    if (loan.returned_at)
      return <span className="badge muted">Returned</span>;
    if (loan.is_overdue) return <span className="badge danger">Overdue</span>;
    return <span className="badge success">On loan</span>;
  };

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Loans</h1>
          <p>{loans.length} loans shown</p>
        </div>
        <button className="btn" onClick={openForm}>
          + New Loan
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="toolbar">
        <label className="muted" style={{ display: "flex", gap: 6, alignItems: "center" }}>
          <input
            type="checkbox"
            style={{ width: "auto" }}
            checked={activeOnly}
            onChange={(e) => setActiveOnly(e.target.checked)}
          />
          Active loans only
        </label>
      </div>

      <div className="card" style={{ padding: 0 }}>
        <table>
          <thead>
            <tr>
              <th>Book</th>
              <th>Member</th>
              <th>Borrowed</th>
              <th>Due</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {loans.map((l) => (
              <tr key={l.id}>
                <td>
                  <strong>{l.book_title}</strong>
                  <div className="muted" style={{ fontSize: 12 }}>
                    {l.book_author}
                  </div>
                </td>
                <td>{l.member_name}</td>
                <td className="muted">
                  {new Date(l.borrowed_at).toLocaleDateString()}
                </td>
                <td className="muted">
                  {new Date(l.due_date).toLocaleDateString()}
                </td>
                <td>{statusBadge(l)}</td>
                <td style={{ textAlign: "right" }}>
                  {!l.returned_at && (
                    <button
                      className="btn secondary small"
                      onClick={() => handleReturn(l)}
                    >
                      Return
                    </button>
                  )}
                </td>
              </tr>
            ))}
            {loans.length === 0 && (
              <tr>
                <td colSpan="6" className="empty">
                  No loans to show.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {adding && (
        <Modal title="New Loan" onClose={() => setAdding(false)}>
          <form onSubmit={submit}>
            {formError && <div className="error-banner">{formError}</div>}
            <div className="field" style={{ marginBottom: 14 }}>
              <label>Member</label>
              <select
                value={form.member_id}
                onChange={(e) => setForm({ ...form, member_id: e.target.value })}
                required
              >
                <option value="">Select a member…</option>
                {members.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="field" style={{ marginBottom: 14 }}>
              <label>Book (available only)</label>
              <select
                value={form.book_id}
                onChange={(e) => setForm({ ...form, book_id: e.target.value })}
                required
              >
                <option value="">Select a book…</option>
                {books.map((b) => (
                  <option key={b.id} value={b.id}>
                    {b.title} ({b.available_copies} left)
                  </option>
                ))}
              </select>
            </div>
            <div className="field">
              <label>Loan period (days)</label>
              <input
                type="number"
                min="1"
                max="90"
                value={form.loan_days}
                onChange={(e) => setForm({ ...form, loan_days: e.target.value })}
              />
            </div>
            <div className="modal-actions">
              <button
                type="button"
                className="btn secondary"
                onClick={() => setAdding(false)}
              >
                Cancel
              </button>
              <button type="submit" className="btn">
                Create Loan
              </button>
            </div>
          </form>
        </Modal>
      )}
    </>
  );
}
